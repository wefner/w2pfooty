routers = dict( 
   BASE = dict(
        default_application='footy')
)

routes_in = (
    # Admin routes
    ('/admin/$anything', '/admin/$anything'),
    # if starts with footy we dont change any routing
    ('/footy/$anything', '/footy/$anything'),
)

routes_onerror = [
  ('footy/400', '/footy/default/login'),
  ('footy/*', '/footy/default/index'),
  ('*/404', '/footy/static/404.html'),
  ('*/*', '/footy/default/index')
]

routes_out = [(x, y) for (y, x) in routes_in]

