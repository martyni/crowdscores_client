import pyttsx
import time
engine = pyttsx.init()
engine.setProperty('rate', 120)
engine.setProperty('voice', 'lancashire')


with open('game', 'r') as games:
   line = games.read()
engine.say(line)
print "trying to say {}".format(line)
engine.runAndWait()
