import requests
import json
import time
import os
from datetime import date, timedelta, datetime
from pprint import pprint
#from geopy.geocoders import Nominatim
today = date.today()
yesterday = today - timedelta(1)
rate_limited = 0

#def get_country(latitude, longitude):
#   global rate_limited
#   geolocator = Nominatim()
#   try:
#      return  geolocator.reverse("{:f}, {:f}".format(latitude, longitude)).address.split(', ')[-1]
#   except:
#      rate_limited +=1
#      pprint("rate limiting on geo_lookups: %s" % str(rate_limited))
#      time.sleep(0.1 * rate_limited)
#      return get_country(latitude, longitude)
class Crowdscores(object):
   def __init__(self, api_key, base='https://api.crowdscores.com/api/v1/'):
      self.api_key = api_key
      self.base =  base
      self.stuff = {'co-ord lookup':{}}
      self._add_stuff('competitions')
      self._add_stuff('rounds')
      self._add_stuff('seasons')
      self._add_stuff('football_states') 
   def help(self):
      pprint(dir(self))

   def base_request(self, endpoint):
      '''Wraps endpoint requests with the authentication and base crowdscores url'''
      headers = {
                 'x-crowdscores-api-key': self.api_key,
                 'Content-Type': 'application/json'
                }
      r = requests.get(self.base + endpoint, headers=headers)
      return r.text

   def response(self, endpoint, response, error=False, error_detail=None):
      '''Standardizes returned responses with endpoints '''
      return {
              'error' : error,
              'error_detail': error_detail,
              'response' : response,
              'endpoint' : self.base + endpoint 
             }
   
   def _from_cache(self, key):
       try:
          return self.response(self.base + key, self.stuff[key])
       except:
          return self.response(self.base + key, 
                                key, 
                                error=True, 
                                error_detail='"%s" not found in cache' % key)

   def _dictionify(self, endpoint):
      raw_request = self.base_request(endpoint)
      try:
         json_ =  json.loads(raw_request)
         if type(json_) == list :
            return self.response(endpoint, json_)

         if json_.get('errorText' ,False):
            return self.response(endpoint, dict_, error=True, error_detail=json_['errorText'])

         else:
            return self.response(endpoint, json_)

      except ValueError:
         return self.response(endpoint, raw_request, error=True, error_detail='no json in response')

   def _dicto_listonify(self, key, arg, dict_ ):
      '''Creates dictionary of lists'''
      try:
         dict_[key].append(arg)
      except KeyError:
         dict_[key] = [arg]
      return dict_

   def _add_stuff(self, request):
      try:
         self.stuff[request] = json.loads(self.base_request(request))
      except TypeError:
         pass
      except ValueError:
         pass

   def get_competions_from_cache(self):
       return self._from_cache('competitions')
 
   def get_rounds_from_cache(self):
       return self._from_cache('rounds')

   def get_seasons_from_cache(self):
       return self._from_cache('seasons')

   def get_football_states(self):
       return self._from_cache('football_states')

   def get_rounds_by_competition_id(self, competition_id):
       return self._dictionify('rounds?competition_id=%s' % competition_id)

   def get_rounds_by_competition_name(self, competition_name):
       competition_name = competition_name.lower()
       search_results = []
       competition_ids = []
       for competition in self.stuff['competitions']:
          all_names = [name.lower() for name in competition['allNames']]
          if competition['fullName'].lower() == competition_name or competition_name in all_names:
             search_results.append(competition) 
                                   #self.get_rounds_by_competition_id(competition['dbid'])
             competition_ids.append(str(competition['dbid']))
 
       if len(search_results) > 1:
          competition_string = ','.join(competition_ids)
          url = 'rounds?competition_ids=%s' % competition_string
          return self.response(url, search_results)
 
       elif len(search_results) == 1:
          return self.response('rounds?competition_ids=%s' % competition_ids[0],
                                search_results[0])
       else:
          return self.response(competition_name, None, error=True, error_detail='No team %s found' % competition_name)

   def get_league_table(self, round_id):
       return self._dictionify('league-table/%s' % round_id)
      
   def get_teams(self, round_ids, competition_ids):
       return self._dictionify('teams?round_ids=%s,competition_ids=%s' % (round_ids, competition_ids))
    
   def date_handle(self, a_date):
      '''Formats a date or datetime object correctly'''
      return a_date.strftime('%Y-%m-%dT%H:%M:%S')
     
   def get_matches(self, from_=yesterday, to=today):
      from_string = self.date_handle(from_)
      to_string = self.date_handle(to)
      return self._dictionify('matches?from=%s&to=%s' % (from_string, to_string))
 
   def list_league_tables(self):
      return [{'round_id' : round_['dbid'],
               'full_name': round_['fullName'],
               'season' : round_['season']['name']}  
                for round_ in self.stuff['rounds'] 
                if round_['hasLeagueTable']] 

   def list_football_states(self):
      return [(key,
               client.stuff['football_states'][key]['longName']) 
               for key in client.get_football_states()['response']]

   def list_competitions(self):
      return [{'competition_id' : competition['dbid'],
               'full_name' : competition['fullName']}
               for competition in self.stuff['competitions']]
   
   def get_events(self):
      return self._dictionify('events')
 
   def list_events(self, save=True):
      live_events = self.get_events()["response"][::-1]
      if save:
         self.events = live_events
      return live_events
   
   def check_events(self):
     live_events = self.list_events(save=False)
     if live_events == self.events:
        return False
     else:
       new_events = []
       for event in live_events:
          if event not in self.events:
             new_events.append(event)
       self.events = live_events
       return new_events
    

   #def list_by_country(self, from_=yesterday, to=today):
   #   matches = self.get_matches(from_, to)['response']
   #   self.stuff['countries'] = {}
   #   for match in matches:
   #      if match['venue'] and match['venue']['geolocation']:
   #         la = match['venue']['geolocation']['latitude']
   #         lo = match['venue']['geolocation']['longitude']
   #         match['country'] = self.stuff['co-ord lookup'].get('%s%s' % (la, lo), get_country(la, lo))
   #         self.stuff['co-ord lookup']['%s%s' % (la, lo)] = match['country']
   #         self.stuff['countries'] = self._dicto_listonify(match['country'], match, self.stuff['countries'])
   #      else:
   #         match['country'] = None
   #   
   #   return self.countries 
   #   #return {country : [match for match in matches if match['country'] == country] for country in self.countries}

                 
   def _convert_time(self, stamp):
      return datetime.fromtimestamp(int(stamp/1000))

if __name__ == '__main__':
   with open(os.getenv("HOME") + "/.crowdscores", "r") as auth:
      token = auth.read()
   print(token) 
   client = Crowdscores(token)   
