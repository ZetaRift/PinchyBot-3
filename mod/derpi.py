import requests
import json
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

"""

logging.basicConfig(filename='logs/derpi.log',level=logging.WARNING)
templist = ""

api_key = "" #Optional API key goes here, it can be accessed on the account settings page for your account on Derpibooru

def randimg(t, nofilter):
    if nofilter == True:
     if t is None:
      r = requests.get("http://derpibooru.org/search.json?key={key}&q=cute".format(key=api_key))
     else:
      t = t.replace(" ", "+")
      t = t.replace(", ", ",")
      r = requests.get("http://derpibooru.org/search.json?key={key}&q={t}".format(t=t,key=api_key))

    else:
     if t is None:
      r = requests.get("http://derpibooru.org/search.json?q=cute")
     else:
      t = t.replace(" ", "+")
      t = t.replace(", ", ",")
      r = requests.get("http://derpibooru.org/search.json?q={t}".format(t=t))
      
    if r.status_code != 200: #Back off in events of a non-200 status code
     return "Status returned {status}".format(status=r.status_code)
     
    else:
     jso = json.loads(r.text)
     if jso['total'] == 0:
      return("That tag or tag combination does not exist")
     else:
      dat = random.choice(jso['search'])
      iid = dat['id_number']
      return str("http://derpibooru.org/{id} (Tag/Tag combination has {n} images)".format(id=iid,n=str(jso['total'])))
    

def tagsearch(tag):        #Dosen't work because it says "list indices must be integers, not str" on eval
    ser1 = tag.replace(" ", "+")
    ser1 = ser1.replace(", ", ",")
    r = requests.get("http://derpibooru.org/search.json?q={t}".format(t=ser1))
    if r.status_code != 200: #Back off in events of a non-200 status code
     return "Status returned {status}".format(status=r.status_code)
    else:
     jso = json.loads(r.text)
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
     jso = json.loads(r.text)
     sp = jso['tag']['spoiler_image_uri']
     if sp is None:
      logging.warning('No spoiler image for tag "{tag}"'.format(tag=tag))
      return None
     else:
      return "http:"+sp

def thumb(num_id):
    r = requests.get('http://derpibooru.org/'+num_id+'.json')
    if r.status_code != 200:
     return "Server returned {status}".format(status=r.status_code)
    else:
     jso = json.loads(r.text)
     sp = "http:"+jso['representations']['thumb']
     return str(sp)

def fetch_info(numid):
    r = requests.get('https://derpibooru.org/images/{num}.json'.format(num=numid))
    if r.status_code != 200:
     logging.warning("Server returned {status}")
     return None
    else:
     return json.loads(r.text)
 
_score = lambda img_info: int(img_info['score'])
_upv = lambda img_info: int(img_info['upvotes'])
_dwv = lambda img_info: int(img_info['downvotes'])
_faves = lambda img_info: int(img_info['faves'])
_cmts = lambda img_info: int(img_info['comment_count'])
_uled = lambda img_info: img_info['uploader']
_tags = lambda img_info: img_info['tags']
_chk_tags = lambda img_info: img_info['tag_ids']
_thumb = lambda img_info: "http:"+img_info['representations']['thumb']
_format = lambda img_info: img_info['original_format']


def stats_string(numid):
    img_info = fetch_info(numid)
    if img_info is None: #Return none if fetch_info sees a non-200 HTTP status code
     return None
    else:
     if len(_chk_tags(img_info)) >= 25:
      templist = "[Too many tags]"
     else:
      templist = _tags(img_info)
     if "explicit" in _chk_tags(img_info):
      return ("<b>(Explicit)</b> http://derpibooru.org/{num} | <b>Score</b>: {score} ({upv} up / {dwv} down) with {faves} faves | <b>Comment count</b>: {cmts} | <b>Uploaded by</b>: {uled}".format(
         score=_score(img_info),
         upv=_upv(img_info),
         dwv=_dwv(img_info),
         faves=_faves(img_info),
         cmts=_cmts(img_info),
         uled=_uled(img_info),
         num=numid
         ),
         "<b>Image #{num} tags</b>: {tgs}".format(
         tgs=templist,
         num=numid
         ))
     elif "questionable" in _chk_tags(img_info):
      return ("<b>(Questionable)</b> http://derpibooru.org/{num} | <b>Score</b>: {score} ({upv} up / {dwv} down) with {faves} faves | <b>Comment count</b>: {cmts} | <b>Uploaded by</b>: {uled}".format(
         score=_score(img_info),
         upv=_upv(img_info),
         dwv=_dwv(img_info),
         faves=_faves(img_info),
         cmts=_cmts(img_info),
         uled=_uled(img_info),
         num=numid
         ),
         "<b>Image #{num} tags</b>: {tgs}".format(
         tgs=templist,
         num=numid
         ))
     elif "grimdark" in _chk_tags(img_info):
      return ("<b>(Grimdark)</b> http://derpibooru.org/{num} | <b>Score</b>: {score} ({upv} up / {dwv} down) with {faves} faves | <b>Comment count</b>: {cmts} | <b>Uploaded by</b>: {uled}".format(
         score=_score(img_info),
         upv=_upv(img_info),
         dwv=_dwv(img_info),
         faves=_faves(img_info),
         cmts=_cmts(img_info),
         uled=_uled(img_info),
         num=numid
         ),
         "<b>Image #{num} tags</b>: {tgs}".format(
         tgs=templist,
         num=numid
         ))
     elif _format(img_info) == "gif":
      return ("http://derpibooru.org/{num} | <b>Score</b>: {score} ({upv} up / {dwv} down) with {faves} faves | <b>Comment count</b>: {cmts} | <b>Uploaded by</b>: {uled}".format(
         score=_score(img_info),
         upv=_upv(img_info),
         dwv=_dwv(img_info),
         faves=_faves(img_info),
         cmts=_cmts(img_info),
         uled=_uled(img_info),
         num=numid
         ),
         "<b>Image #{num} tags</b>: {tgs}".format(
         tgs=templist,
         num=numid
         ))
     else:
      return ("{thumb} http://derpibooru.org/{num} | <b>Score</b>: {score} ({upv} up / {dwv} down) with {faves} faves | <b>Comment count</b>: {cmts} | <b>Uploaded by</b>: {uled}".format(
         score=_score(img_info),
         upv=_upv(img_info),
         dwv=_dwv(img_info),
         faves=_faves(img_info),
         cmts=_cmts(img_info),
         uled=_uled(img_info),
         num=numid,
         thumb=_thumb(img_info)
         ),
         "<b>Image #{num} tags</b>: {tgs}".format(
         tgs=templist,
         num=numid
         ))
