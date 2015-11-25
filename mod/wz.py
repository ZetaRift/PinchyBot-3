#Weather from wunderground (This requires an API key)
import requests
import dataset



db = dataset.connect("sqlite:///wz-Data.db") #Note that this will create the database file at the root directory of the bot (Where pinchybot.py is)
dbtable = db["UserData"]

def readvar():
 return conf["TestKey"]

def adduser(user, param):
 t = dbtable.find_one(Username=user)
 if t:
  #update row
  ID = t['id']
  dbtable.update(dict(id=ID, Username=user, Location=param), ['id'])
 else:
  #place new row
  dbtable.insert(dict(Username=user, Location=param))
  
  
def rmuser(user):
 dbtable.delete(Username=user)

def savedb():
 db.commit()

def getinfo(sparam, api_key):  #Use this - faster
 sparam = sparam.replace(" ", "_")
 sparam = sparam.replace(", ", ",")
 r = requests.get('http://api.wunderground.com/api/'+api_key+'/conditions/q/'+sparam+'.json')
 if r.status_code != 200:
  return None
 else:
  return r.json()
 
 
_lostr = lambda w_info: w_info['current_observation']['display_location']['full'] 
_cond = lambda w_info: w_info['current_observation']['weather']
_tempstr = lambda w_info: w_info['current_observation']['temperature_string']
_atm_mb = lambda w_info: w_info['current_observation']['pressure_mb']
_atm_in = lambda w_info: w_info['current_observation']['pressure_in']
_winddir = lambda w_info: w_info['current_observation']['wind_dir']
_winddeg = lambda w_info: w_info['current_observation']['wind_degrees']
_wind_km = lambda w_info: w_info['current_observation']['wind_kph']
_wind_mph = lambda w_info: w_info['current_observation']['wind_mph']
_humid = lambda w_info: w_info['current_observation']['relative_humidity']

 
def info_string(sparam, database_fetch, user, api_key):
 if database_fetch == True:
  user = dbtable.find_one(Username=user)
  if user:
   w_info = getinfo(user['Location'], api_key)
  else:
   return "User not in database"
 else:
  w_info = getinfo(sparam, api_key)
 if w_info is None:
  return None
 else:
  return "Conditions for <u>{lo}</u>: {cond} | <b>Temperature</b>: {temp} | <b>Pressure</b>: {atm_in} inHg ({atm_mb} mb) | <b>Wind</b>: {wdir} ({wdeg}) at {windmph} MPH ({windkph} kM/h) | <b>Humidity</b>: {hum}".format(
    lo=_lostr(w_info),
    cond=_cond(w_info),
    temp=_tempstr(w_info),
    atm_in=_atm_in(w_info),
    atm_mb=_atm_mb(w_info),
    wdir=_winddir(w_info),
    wdeg=_winddeg(w_info),
    windmph=_wind_mph(w_info),
    windkph=_wind_km(w_info),
    hum=_humid(w_info)
    )





