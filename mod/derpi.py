import requests
import random
import logging
"""
Derpiboooru API accessing for parsing, function parameters are explicitly strings
Changed from urllib2 to requests (3rd party)
Changes are being applied to the derpibooru API
2015-05-31: Minor changes to return non-200 HTTP status codes as if to back off
2015-06-12: More changes to the derpibooru API, but no errors raised on parsing image page URLs.
2015-07-05: Added small function to limit how many tags it can show
2015-07-23: stats_string now returns a tuple with two messages, first one being the image info(Excluding the tags), and the second containing the tags. This has been marked as a major change
2015-08-03: randimg searches for anything specified and returns a random image with the tag or tag combination
2015-08-08: randimg requires two arguments, first is the search string, second is the boolean for unfiltering
2015-08-25: Added in uploaded and updated time and shorter way of tag checking for questionable/explicit/grimdark

"""

system_tags = ["explicit", "grimdark", "grotesque", "questionable", "safe", "semi-grimdark", "suggestive"]

logging.basicConfig(filename='logs/derpi.log',level=logging.WARNING)
templist = ""


def rating_iterate(taglist):
 tlist = taglist.split(", ")
 return ", ".join([i for i in tlist if i in system_tags]).title()

def split_taglist(tag_str):
 length = 200
 suffix = "..."
 taglen = len(tag_str.split(", ", maxsplit=-1)[0:])
 if len(tag_str) <= length:
  return tag_str
 else:
  return tag_str[:length].rsplit(' ', 1)[0]+suffix+" ("+str(taglen)+" total tags)"
 
def derpitimestamp(time_string): #Returns in Y-m-d H:M format
 ts_re = re.compile("(?P<year>[0-9]*-)?(?P<month>[0-9]*-)(?P<day>[0-9]*)?(T)?(?P<hour>[0-9]*:)?(?P<minute>[0-9]*:)?(?P<second>[0-9]*.)?(?P<millisecond>[0-9]*.)")
 ftime = re.match(ts_re, time_string)
 timestamp_str = "{y}-{mo}-{d} {h}:{m}".format(
  y=ftime.group("year").rstrip("-"),
  mo=ftime.group("month").rstrip("-"),
  d=ftime.group("day"),
  h=ftime.group("hour").rstrip(":"),
  m=ftime.group("minute").rstrip(":")
  )
 return timestamp_str

def randimg(t, apikey):
    #Param room: 'Room' object from ch.py
    #Param t: Search term string
    #Param nofilter: Boolean to ignore default filter.
    if apikey != None:
     if t is None:
      r = requests.get("https://derpibooru.org/search.json?key={key}&q=cute".format(key=apikey))
     else:
      t = t.replace(" ", "+")
      t = t.replace(", ", ",")
      r = requests.get("https://derpibooru.org/search.json?key={key}&q={t}".format(t=t,key=apikey))

    else:
     if t is None:
      r = requests.get("https://derpibooru.org/search.json?q=cute")
     else:
      t = t.replace(" ", "+")
      t = t.replace(", ", ",")
      r = requests.get("https://derpibooru.org/search.json?q={t}".format(t=t))
      
    if r.status_code != 200: #Back off in events of a non-200 status code
     return "Status returned {status}".format(status=r.status_code)
     
    else:
     jso = r.json()
     if jso['total'] == 0:
      room.message("That tag or tag combination does not exist")
     else:
      dat = random.choice(jso['search'])
      iid = int(dat['id'])
      return "https://derpibooru.org/{id} (Tag/Tag combination has {n} images)".format(id=iid,n=str(jso['total']))
    

def tagsearch(tag):
    ser1 = tag.replace(" ", "+")
    ser1 = ser1.replace(", ", ",")
    r = requests.get("https://derpibooru.org/search.json?q={t}".format(t=ser1))
    if r.status_code != 200: #Back off in events of a non-200 status code
     return "Status returned {status}".format(status=r.status_code)
    else:
     jso = r.json()
     if jso['total'] == 0:
      return None
     else:
      img_count = jso['total']
      return str(img_count)

def tagsp(tag):        #Returns URL of spoiler image, returns None (or null) if no url is present
    ser1 = tag.replace(" ", "+")
    ser1 = ser1.replace(":", "-colon-")
    r = requests.get("https://derpibooru.org/tags/"+ser1+".json")
    if r.status_code != 200:
     return "Status returned {status}".format(status=r.status_code)

    else:
     jso = r.json()
     sp = jso['tag']['spoiler_image_uri']
     if sp is None:
      logging.warning('No spoiler image for tag "{tag}"'.format(tag=tag))
      return None
     else:
      return "http:"+sp

def rating(num_id):
    r = requests.get('https://derpibooru.org/'+num_id+'.json')
    if r.status_code != 200:
     return "Server returned {status}".format(status=r.status_code)
    else:
     jso = r.json()
     sp = "http:"+jso['representations']['rating']
     return str(sp)

def fetch_info(numid):
    r = requests.get('https://derpibooru.org/images/{num}.json'.format(num=numid))
    if r.status_code != 200:
     logging.warning("Server returned {status}")
     return None
    else:
     return r.json()
 
_score = lambda img_info: int(img_info['score'])
_upv = lambda img_info: int(img_info['upvotes'])
_dwv = lambda img_info: int(img_info['downvotes'])
_faves = lambda img_info: int(img_info['faves'])
_cmts = lambda img_info: int(img_info['comment_count'])
_uled = lambda img_info: img_info['uploader']
_tags = lambda img_info: img_info['tags']
_format = lambda img_info: img_info['original_format']
_created_time = lambda img_info: img_info['created_at']
_updated_time = lambda img_info: img_info['updated_at']


def stats_string(numid):
    #Param room: 'Room' object from ch.py
    #Param numid: numid string for image number
    img_info = fetch_info(numid)
    if img_info is None: #Return none if fetch_info sees a non-200 HTTP status code
     room.message("Image dosen't exist?")
    else:
     uled_time = derpitimestamp(_created_time(img_info))
     upd_time = derpitimestamp(_updated_time(img_info))
     rating = rating_iterate(_tags(img_info))
      
     return ("<b>({rating})</b> https://derpibooru.org/{num} | <b>Uploaded at</b>: {uledtime} UTC by {uled} | <b>Score</b>: {score} ({upv} up / {dwv} down) with {faves} faves | <b>Comment count</b>: {cmts} ".format(
        rating=rating,
        uledtime=uled_time,
        score=_score(img_info),
        upv=_upv(img_info),
        dwv=_dwv(img_info),
        faves=_faves(img_info),
        cmts=_cmts(img_info),
        uled=_uled(img_info),
        num=numid
        ),
     "Image #{n} tags: {tlist}".format(
     n=numid,
     tlist=split_taglist(_tags(img_info))
     ))
