import os
import json
import tornado.ioloop
import tornado.web
import tornado.log
import requests
from dotenv import load_dotenv
from jinja2 import \
  Environment, PackageLoader, select_autoescape

load_dotenv(".env")

GIT_REV = os.environ.get('GIT_REV', 'NONE')
print(GIT_REV)
ENV = Environment(
  loader=PackageLoader('weather', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
    def render_template (self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))

class MainHandler(TemplateHandler):
    def get(self):
        self.render_template("home.html", {'main': 'main'})
        pass

    def post(self):
        pass
        cityname = self.get_body_argument('cityname')

        payload = {'q': cityname, 'APPID': os.environ.get('APIKEY'), 'units': 'imperial' }
        r = requests.get('http://api.openweathermap.org/data/2.5/weather', params=payload)
        data=r.json()
        self.render_template("home.html", {'main': data['main'], 'weather' : data['weather']})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)",
            tornado.web.StaticFileHandler, {'path': 'static'}),
    ], autoreload=True)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8080')))
  tornado.ioloop.IOLoop.current().start()
