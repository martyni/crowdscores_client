from unidecode import unidecode
import random
import os
import time
import pifacecad
import pifacecad.tools
from pprint import pprint
from pifacecad.lcd import LCD_WIDTH
from client import Crowdscores, datetime, date, timedelta

now = datetime.utcnow()

class Game(object):
   def __init__(self, team_names, score):
      self.teams = {
                    team_names[0].lower() : "h", 
                    team_names[1].lower() : "a",
                    "h" : team_names[0].lower(),
                    "a" : team_names[1].lower()
                   }
      self.team_home_score = score[0]
      self.team_away_score = score[1]
      #self.show_scores()
      self.screen = Screen()
      self.update_screen()
      self.show_scores()
      self.talk()

   def help(self):
      return pprint(dir(self))

   def talk(self):   
      os.system("python say.py")

   def random_zero(self):
       return "bugger all" if random.choice([True,False]) else "0"

   def show_scores(self):
      with open('game', 'w+') as game:
         game.write(unidecode("{0} {2}, {1} {3}".format(self.teams["h"],
                                self.teams["a"],
                                self.team_home_score,
                                self.team_away_score )).replace("0", self.random_zero()))

      print("\n{0}:{2}\n{1}:{3}".format(self.teams["h"],
                                self.teams["a"],
                                self.team_home_score,
                                self.team_away_score ))
      
   def which_team(self, team_name):
      return self.teams.get(team_name, None)

   def update_score(self, team_name):
      if self.which_team(team_name.lower()) == "h" or team_name=="h":
         self.team_home_score += 1 
      elif self.which_team(team_name.lower()) == "a" or team_name=="a":
         self.team_away_score += 1
      self.update_screen()   
      return self.team_a_score, self.team_b_score   
  
   def set_score(self, score):
      self.team_home_score = score[0]
      self.team_away_score = score[1]
      self.update_screen()
      return self.team_home_score, self.team_away_score
   
   def update_screen(self):
      self.screen.show_scores(self.teams["h"],
                              self.teams["a"],
                              self.team_home_score,
                              self.team_away_score)

class Matches(object):
   def __init__(self):
      with open(os.getenv("HOME") + "/.crowdscores", "r") as auth:
         self.token = auth.read()
      self.client = Crowdscores(self.token)
   
   def list_of_matches(self):
      #print(now)
      then = now  - timedelta(hours=3)
      #print(then)
      self.raw_matches = self.client.get_matches(from_=then, to=now)
      #print(self.raw_matches)
      self.matches = {(match['homeTeam']['name'], match['awayTeam']['name']):
                      (match['homeGoals'], match['awayGoals']) 
                      for match in self.raw_matches['response'] 
                      if match['currentState'] < 200}
      return self.matches

class Screen(object):
   def __init__(self):
      self.cad = pifacecad.PiFaceCAD()
      self.cad.lcd.blink_off()
      self.cad.lcd.backlight_on()
      self.hide_cursor()
      self.width = 16
      self.height = 2
       
   def hide_cursor(self):
      self.cad.lcd.set_cursor(24,0)
       

   def buffer_string(self, string_):
      '''Method to set strings to exactly 16 characters'''
      if len(string_)<self.width:
         return string_ + " " * (self.width - len(string_))
      else:
         return string_[:15:]  

   def show_scores(self, team_a, team_b, score_a, score_b):
      team_a = self.buffer_string(team_a).title()
      team_b = self.buffer_string(team_b).title()
      self.cad.lcd.set_cursor(0,0)
      self.cad.lcd.write(team_a)
      self.cad.lcd.set_cursor(0,1)
      self.cad.lcd.write(team_b)   
      self.cad.lcd.set_cursor(13,0)
      self.cad.lcd.write(":{:0>2}".format(score_a))
      self.cad.lcd.set_cursor(13,1)
      self.cad.lcd.write(":{:0>2}".format(score_b))
      self.hide_cursor() 

if __name__ == "__main__":
   print("Initiating") 
   matches = Matches()
   while True:
      print("pulling matches")
      matches.list_of_matches()
      print("iterating..")
      for match in matches.matches:
         current_game = Game(match, score=matches.matches[match])
