import webapp2, lib
from config import SESSION_SECRET

import modules.pages

app = webapp2.WSGIApplication([
  webapp2.Route('/', name='home', handler='pages.home.HomeHandler'),
  # Authentication
  webapp2.Route('/login', name='login', handler='core.BaseAuthRequest:login'),
  webapp2.Route('/login/<provider>', name='auth_login', handler='core.BaseAuthRequest:_simple_auth'),
  webapp2.Route('/login/<provider>/callback', name='auth_callback', handler='core.BaseAuthRequest:_auth_callback'),
  webapp2.Route('/logout', name='logout', handler='core.BaseAuthRequest:logout'),

], debug=True, config={
  # Modules configuration
  'webapp2_extras.sessions':{ 'secret_key': SESSION_SECRET },
  'webapp2_extras.i18n':{ 'translations_path': 'locale' },
})

