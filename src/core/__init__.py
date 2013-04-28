import os, sys, gettext, re
import webapp2
from webapp2_extras import sessions, i18n, auth
from config import JINJA_ENVIRNMENT, AUTH_CONFIG, USER_ATTRIBUTES, PROVIDER_NAME, LANGUAGES
from config import DATE_TIME_FORMAT, DATE_FORMAT, TIME_FORMAT
from lib.simpleauth.handler import SimpleAuthHandler
from google.appengine.ext import ndb, blobstore
from google.appengine.api import search
import logging
import datetime

if os.path.dirname(__file__) not in sys.path:
  sys.path.append(os.path.join(os.path.dirname(__file__)))

gettext.install('messages', 'locale', True, names=['ugettext'])

class BaseRequest(webapp2.RequestHandler):
  url = ''
  title = ''
  language = None
  
  def __init__(self, *a, **kw):
    super(BaseRequest, self).__init__(*a, **kw)
    self.url = self.request.path_url
    self.language = self.locale
    
  def dispatch(self):
    # Set session
    self.session_store = sessions.get_store(request=self.request)
    # Set translation
    i18n.get_i18n().set_locale( self.language )
    
    try:
      super(BaseRequest, self).dispatch()
    finally:
      # Save session
      self.session_store.save_sessions(self.response)
  
  def write(self, *a, **kw):
    return self.response.out.write(*a, **kw)
  
  @property
  def locale(self):
    if self.request.get('lang'):
      return self.request.get('lang')
    else:
      return LANGUAGES.get(self.request.headers.get('X-AppEngine-Country')) or 'en'
    
  @webapp2.cached_property
  def session(self):
    return self.session_store.get_session()

class BaseAuthRequest(BaseRequest, SimpleAuthHandler):
  def _on_signin(self, data, auth_info, provider):
    """Callback whenever a new or existing user is logging in.
     data is a user info dictionary.
     auth_info contains access token or oauth token and secret.
    """
    
    # Check structure of incoming data
    # to setup USER_ATTRIBUTES for current provider
    self.auth.unset_session()
    try:
      auth_id = '%s:%s' % (provider, data['id'])
      user = self.auth.store.user_model.get_by_auth_id(auth_id)
      user_attributes = self._process_user_attributes(data, USER_ATTRIBUTES[provider])
      user_attributes['provider'] = PROVIDER_NAME[provider]
    except:
      self.session.add_flash(_('Login Error'), key='error')
      return self.redirect('/account/login')

    if user:
      # If auth_id exists:
      # Compare user_attributes with user's properties fetched
      # from the datastore and update local user in case something's changed.
      for key, value in user_attributes.iteritems():
        if not getattr(user, key) == value:
          user.populate(**user_attributes)
          user.put()
          break

      self.auth.set_session( self.auth.store.user_to_dict(user) )
    else:
      # If auth_id doesn't exist:
      # Check whether there's a user currently logged in.
      if not self.logged_in:
        # TODO: Check if user with same name exists,
        # ask if that's desired profile and offer to signin
        # with that profile to connect accounts
        
        # Create a new user if nobody's signed in. 
        user_attributes['active'] = False
        ok, user = self.auth.store.user_model.create_user(auth_id, **user_attributes)
        if ok:
          self.auth.set_session(self.auth.store.user_to_dict(user))
          return self.redirect( '/account/register' )
      else:
        # Add this auth_id to currently logged in user.
        self.user.populate(**user_attributes)
        self.user.add_auth_id(auth_id)

    return self.redirect( '/account/overview' )
  
  def login(self):
    self.auth.unset_session()
    self.render('pages/login.html')

  def logout(self):
    self.auth.unset_session()
    self.redirect('/')

  def _callback_uri_for(self, provider):
    return self.uri_for('auth_callback', provider=provider, _full=True)

  def _get_consumer_info_for(self, provider):
    """Returns a tuple (key, secret) for auth init requests."""
    return AUTH_CONFIG[provider]

  def _process_user_attributes(self, data, user_attributes_map):
    """Get the needed information from the provider dataset."""
    user_attributes = {}
    for key, value in user_attributes_map.iteritems():
      attribute = (key, data.get(value)) if isinstance(key, str) else key(data.get(value))
      user_attributes.setdefault(*attribute)
    return user_attributes

  # Render template to screen with optional argument
  def render(self, name, values={}):
    template = JINJA_ENVIRNMENT.get_template(name)
    values.update({
      'core'        : {
        'language'        : self.language,
        'title'           : self.title,
        'url'             : self.url,
        'x_city'          : self.request.headers.get('X-AppEngine-City') or '',
        'x_coordinates'   : self.request.headers.get('X-AppEngine-CityLatLong') or '',
        'x_country'       : self.request.headers.get('X-AppEngine-Country') or '',
        'x_region'        : self.request.headers.get('X-AppEngine-Region') or '',
        },
      'user'        : self.user,
      
      'error'       : self.session.get_flashes('error')[0][0] if self.session.get('error') else None,
      'action'      : self.session.get_flashes('action')[0][0] if self.session.get('action') else None,
      'status'      : self.session.get_flashes('status')[0][0] if self.session.get('status') else None,
    })
    self.write(template.render(**values))

  @property
  def user_id(self):
    return self.user.key.id()

  @webapp2.cached_property
  def auth(self):
    return auth.get_auth()

  @webapp2.cached_property
  def user(self):
    """Returns currently logged in user"""
    user_dict = self.auth.get_user_by_session()
    return self.auth.store.user_model.get_by_id(user_dict['user_id']) if self.logged_in else None

  @webapp2.cached_property
  def logged_in(self):
    """Returns true if a user is currently logged in, false otherwise"""
    return self.auth.get_user_by_session() is not None

class BaseModel(ndb.Model):
  # Document Identifier for indexing and search with Search API
  doc_id = ndb.StringProperty()
  # Created and Modified time 
  created = ndb.DateTimeProperty(auto_now_add = True)
  modified = ndb.DateTimeProperty(auto_now = True)

  def index(self, name=None):
    """Index document property of the instance.
    Add doc_id to the instance
    """
    if not name:
      # use clase name for name of this index
      name = self.__class__.__name__.lower()
    index = search.Index( name )
    if not self.doc_id:
      if self.document():
        self.doc_id = index.put( self.document() )[0].id
        self.put()
    else:
      index.put( self.document(self.doc_id) )
  
  def document(self):
    return None

  @property
  def id(self):
    return int(self.key.id())

  @classmethod
  def attributes(cls, data={}):
    """Generates class properties and matches them against data dictionary.
    Usefull for batch processing data from POST: data = dict(self.request.POST),
    if html form input field names match model properties
    """
    _attr = {}
    for property_name, property_type in cls._properties.items():
      #logging.info(property_name + ': ' + str(type(property_type)))
      _a = False
      _data = data.get(property_name)
      if _data:
        _values = map(lambda s: s.strip(), _data.split(',')) if type(_data) == str else _data
        logging.info(type(_data))
        #
        # ndb.IntegerProperty
        # 
        if type(property_type) is ndb.IntegerProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: int(s), _values ))
          else:
            _a = (property_name, int(_data))
        #
        # ndb.FloatProperty
        # 
        elif type(property_type) is ndb.FloatProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: float(s.strip()), _values ))
          else:
            _a = (property_name, float(_data))
        #
        # ndb.BooleanProperty
        # 
        elif type(property_type) is ndb.BooleanProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: bool(int(s.strip())), _values ))
          else:
            _a = (property_name, bool(_data))
        #
        # ndb.StringProperty
        # 
        elif type(property_type) is ndb.StringProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: s.strip(), _data.split(';') ))
          else:
            _a = (property_name, _data)
        #
        # ndb.TextProperty
        # 
        elif type(property_type) is ndb.TextProperty:
          _a = (property_name, _data)
        # 
        # ndb.DateTimeProperty
        # 
        elif type(property_type) is ndb.DateTimeProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: datetime.datetime.strptime(s, DATE_TIME_FORMAT) , _values ))
          else:
            _a = (property_name, datetime.datetime.strptime(_data, DATE_TIME_FORMAT) )
        # 
        # ndb.DateProperty
        # 
        elif type(property_type) is ndb.DateProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: datetime.datetime.strptime(s, DATE_FORMAT) , _values ))
          else:
            _a = (property_name, datetime.datetime.strptime(_data, DATE_FORMAT) )
        # 
        # ndb.TimeProperty
        # 
        elif type(property_type) is ndb.TimeProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: datetime.datetime.strptime(s, TIME_FORMAT) , _values ))
          else:
            _a = (property_name, datetime.datetime.strptime(_data, TIME_FORMAT) )
        # 
        # ndb.GeoPtProperty
        # 
        elif type(property_type) is ndb.GeoPtProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: ndb.GeoPt(s.strip()) , _data.split(';') ))
          else:
            _a = (property_name, ndb.GeoPt( _data ))
        # 
        # ndb.KeyProperty
        # 
        elif type(property_type) is ndb.KeyProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: ndb.Key(s) , _values ))
          else:
            _a = (property_name, ndb.Key(_data) )
        # 
        # ndb.BlobKeyProperty
        # 
        elif type(property_type) is ndb.BlobKeyProperty:
          if property_type._repeated:
            _a = (property_name, map( lambda s: blobstore.BlobKey(s) , _values ))
          else:
            _a = (property_name, blobstore.BlobKey(_data) )
        # 
        # Other types
        # 
        elif True:
          if property_type._repeated:
            _a = (property_name, map( lambda s: s , _data ))
          else:
            _a = (property_name, _data )

      if _a:
        _attr.setdefault(*_a)
    return _attr

  @classmethod
  def create(cls, data):
    """Create instance of the model and writes it to datastore.
    """
    _i = cls()
    if cls.attributes(data):
      _i.populate(**cls.attributes(data))
    else:
      return
    if _i.put():
      _i.index()
      return _i
  
  @classmethod
  def update(cls, data):
    """Update instance of the model and write updates to datastore.
    """
    _i = cls.get_by_id( int(data['id']) )
    _i.populate(**cls.attributes(data))
    if _i.put():
      _i.index()
      return _i
  
  @classmethod
  def delete(cls, data):
    """Delete instance of the model from datastore.
    Removes Search API indexes
    """
    _i = cls.get_by_id( int(data['id']) )
    if _i.doc_id:
      name = _i.__class__.__name__.lower()
      search.Index(name).delete(_i.doc_id)
    _i.key.delete()
  
  @classmethod
  def get_latest(cls):
    return cls.query().order(-cls.created).get()
  
  @classmethod
  def fetch_latest(cls):
    return cls.query().order(-cls.created).fetch()
  
