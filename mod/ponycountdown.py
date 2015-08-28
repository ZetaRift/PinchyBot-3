import requests
import datetime
import time
#Pony countdown
#API by Xe (https://github.com/Xe/PonyAPI)

host = "ponyapi.apps.xeserv.us" #Host to be defined (Without the http://)
port = 80 #Port to be defined

def epsearch(param):
 cur_time = time.time()
 st = param.replace(" ", "%20")
 r = requests.get("http://{h}:{p}/search?q={st}".format(st=st,h=host,p=port))
 j = r.json()
 air_date_u = int(j['episodes'][0]['air_date'])
 eptime = str(datetime.datetime.fromtimestamp(j['episodes'][0]['air_date']).strftime('%Y, %B, %d %H:%M'))
 if cur_time >= air_date_u:
  return "Season {s}, Episode {e}: <b>{etitle}</b> Aired on {time} UTC".format(
   s=str(j['episodes'][0]['season']),
   e=str(j['episodes'][0]['episode']),
   etitle=j['episodes'][0]['name'],
   time=eptime
   )
 else:
   return "Season {s}, Episode {e}: <b>{etitle}</b> Airs on {time} UTC".format(
   s=str(j['episodes'][0]['season']),
   e=str(j['episodes'][0]['episode']),
   etitle=j['episodes'][0]['name'],
   time=eptime
   )
 
 
 
def nextep():
 
 cur_time = time.time()
 r = requests.get("http://{h}:{p}/newest".format(h=host,p=port))
 j = r.json()
 air_date = datetime.datetime.fromtimestamp(int(j['episode']['air_date'])).strftime('%Y, %B, %d %H:%M')
 air_date_u = int(j['episode']['air_date'])
 not_time = str(air_date)
 tahead = int(j['episode']['air_date']) + 172800 #Usually on the following Monday
 if cur_time >= air_date_u:
  return "Episode <b>{etitle}</b> (S{s}E{e}) has aired on {time} UTC".format(
   etitle=j['episode']['name'],
   s=str(j['episode']['season']),
   e=str(j['episode']['episode']),
   time=not_time
   )
   
 elif cur_time > tahead:
  return "Next episode air time is unknown"
 
 else:
  return "Next episode: <b>{etitle}</b> (S{s}E{e}) airs on {time} UTC".format(
   etitle=j['episode']['name'],
   s=j['episode']['season'],
   e=j['episode']['episode'],
   time=not_time
   )
