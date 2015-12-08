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
   '''Object to hold the individual games. Takes the team names and initial scores as tuples. Order is important (home, away)'''
   def __init__(self, team_names, score):
      self.teams = {
                    team_names[0].lower() : "h", 
                    team_names[1].lower() : "a",
                    "h" : team_names[0].lower(),
                    "a" : team_names[1].lower()
                   }
      self.team_home_score = score[0]
      self.team_away_score = score[1]
      self.screen = Screen()
      self.update_screen()
      self.show_scores()
      self.talk()

   def help(self):
      '''Shows a list of methods for the class'''
      return pprint(dir(self))

   def talk(self):   
      '''Horrible hack because I ran out of time say.py will read anything in a file called game'''
      os.system("python say.py")

   def random_zero(self):
      '''Method to randomly write bugger all instead of zero. Method has been implemented in a greedy way so all zeros will be replaced'''
       return "bugger all" if random.choice([True,False]) else "0"

   def show_scores(self):
      '''prints scores to screen and writes them to the game file for reading.'''
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
      '''Will return either h, a or None depending on the team name. '''
      return self.teams.get(team_name.lower(), None)

   def update_score(self, team_name):
      '''Updates score and refreshes screen'''
      if self.which_team(team_name.lower()) == "h" or team_name=="h":
         self.team_home_score += 1 
      elif self.which_team(team_name.lower()) == "a" or team_name=="a":
         self.team_away_score += 1
      self.update_screen()   
      return self.team_a_score, self.team_b_score   
  
   def set_score(self, score):
      '''Hard sets score if set incorrectly'''
      self.team_home_score = score[0]
      self.team_away_score = score[1]
      self.update_screen()
      return self.team_home_score, self.team_away_score
   
   def update_screen(self):
      '''Updates the piface screen with the score'''
      self.screen.show_scores(self.teams["h"],
                              self.teams["a"],
                              self.team_home_score,
                              self.team_away_score)

class Matches(object):
   '''Object for harvesting the list of matches'''
   def __init__(self):
      '''Simple method for keeping api key out of repo. Could be made more setting the API key as an environment variable'''
      with open(os.getenv("HOME") + "/.crowdscores", "r") as auth:
         self.token = auth.read()
      self.client = Crowdscores(self.token)
   
   def list_of_matches(self):
      '''Matches listed must have started within the last 3 hours'''
      then = now  - timedelta(hours=3)
      self.raw_matches = self.client.get_matches(from_=then, to=now)
      self.matches = {(match['homeTeam']['name'], match['awayTeam']['name']):
                      (match['homeGoals'], match['awayGoals']) 
                      for match in self.raw_matches['response'] 
                      if match['currentState'] < 200}
      return self.matches

class Screen(object):
   '''Object for handling display'''
   def __init__(self):
      self.cad = pifacecad.PiFaceCAD()
      self.cad.lcd.blink_off()
      self.cad.lcd.backlight_on()
      self.hide_cursor()
      self.width = 16
      self.height = 2
       
   def hide_cursor(self):
      '''Places the cursor off the screen so you don't see it'''
      self.cad.lcd.set_cursor(24,0)
       

   def buffer_string(self, string_):
      '''
         Method to set strings to exactly 16 characters.
         This way any other characters that are on the screen will be overwritten.
      '''  
      if len(string_)<self.width:
         return string_ + " " * (self.width - len(string_))
      else:
         return string_[:15:]  

   def show_scores(self, team_a, team_b, score_a, score_b):
      '''Slightly verbose method of getting the Team Names and scores written.'''
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
   '''
      Main loop pulls down matches, displays them to the screen and tries to voice them outloud
      as it waits for this process to complete, this serves as the rate limiting step in the loop.
      if there are no games during the last 3 hours the loop sleeps for 60 seconds.
   '''
   print("Initiating") 
   matches = Matches()
   while True:
      print("pulling matches")
      matches.list_of_matches()
      print("iterating..."))
      if matches.matches:
         for match in matches.matches:
            current_game = Game(match, score=matches.matches[match])
      else:
         print("No games sleeping...")
         time.sleep(60)
