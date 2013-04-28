from core import BaseAuthRequest

class HomeHandler(BaseAuthRequest):
  def get(self, *a, **kw):
    self.render('pages/home.html')
