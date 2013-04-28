import jinja2, os, hashlib
from webapp2_extras import i18n

# Copy this file into secrets.py and set keys, secrets and scopes.

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here: 
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
# SESSION_KEY = "a very long and secret session key goes here"

# http://www.mapload.net/login/<provider>/callback

# Google APIs
# https://developers.google.com/accounts/docs/OAuth2WebServer
# http://code.google.com/apis/console
GOOGLE_APP_ID = '241280104740.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'dMN-3GW-BSpHSqia2cxnufjy'

# Facebook auth apis
# https://developers.facebook.com/docs/authentication/server-side/
# https://developers.facebook.com/apps
FACEBOOK_APP_ID = '165389813609241'
FACEBOOK_APP_SECRET = 'aff65e150732ca64d347ff84a8a3110f'

# https://www.linkedin.com/secure/developer
LINKEDIN_CONSUMER_KEY = '79njdpdotx10'
LINKEDIN_CONSUMER_SECRET = 'QxdEAapTEqSulsBR'

# https://manage.dev.live.com/AddApplication.aspx
# https://manage.dev.live.com/Applications/Index
WL_CLIENT_ID = '00000000400EC633'
WL_CLIENT_SECRET = 'wYrMj8ALIxcCBzPu87dMTMPVlecU7SI8'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = '4HTUy9n3PQKj8a3xGHiXVA'
TWITTER_CONSUMER_SECRET = 'pNO5STCOBpyKxhAddksp8QUwboatabXJBMCEP7Lz1Y'

# https://foursquare.com/developers/apps
FOURSQUARE_CLIENT_ID = ''
FOURSQUARE_CLIENT_SECRET = ''

# config that summarizes the above
AUTH_CONFIG = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.profile'),
  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'user_about_me'),
  'live'        : (WL_CLIENT_ID, WL_CLIENT_SECRET,
                  'wl.signin'),
  'foursquare'  : (FOURSQUARE_CLIENT_ID,FOURSQUARE_CLIENT_SECRET,
                  'authorization_code'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
  'linkedin'    : (LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET),

  # OpenID doesn't need any key/secret
}

TEMPLATE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRNMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(TEMPLATE_DIRECTORY),
  extensions=['jinja2.ext.i18n'],
  autoescape=True
)
JINJA_ENVIRNMENT.install_gettext_translations(i18n)

# Languages for translations from country code
LANGUAGES = {
  'RS'      : 'sr',
}

# secret_key for sessions module
SESSION_SECRET = hashlib.sha1('map-lo-ad').hexdigest()

# xmpp IDs
CHAT_SERVER_ID = 'map-lo-ad@appspot.com'
CHAT_CLIENT_ID = '@map-lo-ad.appspotchat.com'

PROVIDER_NAME = {
  'google'  : 'Google',
  'facebook': 'Facebook',
  'linkedin': 'LinkedIn',
  'live'    : 'Windows Live',
  'twitter' : 'Twitter',
}

GOOGLE_API_KEY = 'AIzaSyAAM1DrbWLf4ioEKUtfscnJSBE4jftIlGo'

USER_ATTRIBUTES = {
  'google': {
  # Response from Google
    'picture'       : 'picture',
    'name'          : 'name',
    'first_name'    : 'given_name',
    'last_name'     : 'family_name',
    'profile'       : 'link',
    'gender'        : 'gender',
  }, 'facebook': {
  # Response from Facebook
    lambda id: ('picture', 'http://graph.facebook.com/{0}/picture?type=large'.format(id)) : 'id',
    'name'          : 'name',
    'first_name'    : 'first_name',
    'last_name'     : 'last_name',
    'profile'       : 'link',
    'gender'        : 'gender',

  }, 'linkedin': {
  # Response from LinkedIn
    'picture'       : 'picture-url',
    'name'          : '',
    'first_name'    : 'first-name',
    'last_name'     : 'last-name',
    'profile'       : 'public-profile-url',
    'gender'        : '',
  }, 'live': {
  # Response from Windows Live
    'picture'       : 'avatar_url',
    'name'          : 'name',
    'first_name'    : 'first_name',
    'last_name'     : 'last_name',
    'profile'       : '',
    'gender'        : 'gender',
  }, 'twitter': {
  # Response from Twitter
    'picture'       : 'profile_image_url',
    'name'          : 'name',
    'first_name'    : '',
    'last_name'     : '',
    'profile'       : 'link',
    'gender'        : '',
  },
}

DATE_TIME_FORMAT = '%d-$m-%Y %h-%m-%s'
DATE_FORMAT = '%d-$m-%Y'
TIME_FORMAT = '%h-%m-%s'