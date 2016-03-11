import bottle
import os
from client import Crowdscores

with open(os.getenv("HOME") + "/.crowdscores", "r") as auth:
   token = auth.read()

client = Crowdscores(token)
client.list_events()

@bottle.get('/check_events')
def check_events():
   events = client.check_events()
   if not events:
      return {"No New": "No new events", "Old": client.events[-1]}
   else:
      return {"New": client.events[-1]}

@bottle.get('/mystyle.css')
def style():
   return bottle.static_file('/static/mystyle.css',root=os.path.dirname(os.path.realpath(__file__)))

@bottle.get('/')
def root():
   return bottle.static_file('/static/index.html',root=os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
   bottle.run(host='127.0.0.1', port=8080)
