#!/usr/bin/python3.4


#PinchyBot for chatango by ZetaRift
""""
Depends:
lxml
requests
pytz
"""
#Configuration is stored in a JSON file: "Name" string, "Pass" string, "Rooms" string array, "FontColor" string, "NameColor" string, and "FontSize" integer
import sys
if sys.version_info < (3, 0):
 print("Requires python 3.x, exiting.")
 sys.exit(1)
################################
#Imports
################################
import ch
import string
import os
import random
import time
import datetime
import logging
import binascii
import re
from random import randint
import lxml.html
from xml.dom import minidom
import requests
import _thread as thread
import json
from datetime import timedelta
import decimal
import hashlib
import traceback
import goslate
from mod import *   #Because python 3 hates doing a "from foo import *" even though a __init__.py is present
import signal
from functools import reduce
from PIL import Image
from pytz import reference
import html.parser as htmlparser

################################################################
#Major.Minor.Micro
################################################################
version_string = "0.20.2-beta"

################################################################
#Some global variables
################################################################
conf = json.load(open("settings.json", "r"))

echo = 0

total = 0

quiet = 0

seendb = None

partcommandisused = False

logging.basicConfig(filename='logs/PinchyBot.log',level=logging.WARNING)

upt = time.time() #Grab current unix time upon execution

hparser = htmlparser.HTMLParser()


def sighandle(signal, frame):
 seendb.savefile()
 wz.savedb()
 print("Caught SIGINT, saving and exiting")
 sys.exit(0)

 
signal.signal(signal.SIGINT, sighandle)


def urlparse(url):    #URL parsing for title. Needs lxml
     h = requests.head(url) #Send a HEAD request first for meta-info such as content type and content length without requesting the entire content
     content_type = h.headers['Content-Type']
     if h.status_code != 200:
      return "Err: "+str(h.status_code)
     else:
      if re.match("(image\S+?(?P<format>(jpeg)|(png)|(gif)))", content_type):
       print("Image URL")
       imgpattern = "(image\S+?(?P<format>(jpeg)|(png)|(gif)))"
       if int(h.headers["content-length"]) > 4194304: #Ignore if bigger than 4 MiB
        print("Ignored large image")
        pass
       else:
        reg = re.compile(imgpattern)
        imgformat = reg.search(content_type)
        f = requests.get(url, stream=True)
        s = Image.open(f.raw)
        msg = "{f} image, {size}, {w} x {h}".format(f=imgformat.group("format").upper(),size=readablesize(int(f.headers["content-length"])),w=s.size[0],h=s.size[1])
        return msg
      else:
       f = requests.get(url)
       s = lxml.html.fromstring(f.content) #lxml wants a consistently undecoded file, so f.content does it
       title = '[ '+s.find(".//title").text+" ]"
       return title
     
def readablesize(i):
 if i >= 1048576:
  size = float(i / 1048576)
  return "{s} MiB".format(s=str("%.2f" % size))
 elif i >= 1024:
  size = float(i / 1024)
  return "{s} KiB".format(s=str("%.2f" % size))
 else:
  return "{s} Bytes".format(s=str(i))

def slate(tran, lang): #I think they changed the translation API?
    gs = goslate.Goslate()
    tr = gs.translate(tran, lang)
    return tr

def roll(sides, count):
    r = [random.randrange(1, sides) for i in range(count)]
    dice_array = r
    total = reduce(lambda x, y: x+y, dice_array) #Squish the array elements into one integer through addiction.
    r1 = str(r)
    r1 = r1.strip("[]")
    return (r1, total)
   


def curtime(): #Return string of current time in Y-m-D H:M:S format
    ts = time.time()
    st = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    return st

def tstamp(t): #Return string of human-readable time from t (unix time)
    st = str(datetime.datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d %H:%M:%S'))
    return st

def readRoom(room):					
	bestand = open('arooms.txt', 'r')
	for line in bestand:
		if room in line:
			rstatus = True
			return rstatus
		else:
			rstatus = False
			return rstatus

def blist(user):					
	bestand = open('blacklist.txt', 'r')
	for line in bestand:
		if user in line:
			rstatus = True
			return rstatus
		else:
			rstatus = False
			return rstatus


def tempconv(pfix, value):
    if pfix == 'cf':
       tmp = value * 1.8 + 32
       return str(float(tmp))
    elif pfix == 'fc':
       tmp = (value - 32) * 5 / 9
       return str(float(tmp))
    elif pfix == 'ck':
       tmp = value + 273.15
       return str(float(tmp))
    elif pfix == 'kc':
       tmp = value - 273.15
       return str(float(tmp))


def uhex(binary):
    n = int(binary, 2)
    nt = binascii.unhexlify('%x' % n)
    return nt

def uptime():
    upd = time.time() - upt
    tz = str(timedelta(seconds=upd))
    tz = tz.split(".")[0]
    return tz


def UserMetric(user):					
	bestand = open('user_metric.txt', 'r')
	for line in bestand:
		if user in line:
			mstatus = 1
			return mstatus
		else:
			mstatus = 0
			return mstatus


def wmetric(user):
 with open("wz-data.json", 'r') as f:
  jso = json.load(f)
  rt = jso['users'][user]['metric']
  return rt

def wzip(user):
 with open("wz-data.json", 'r') as f:
  jso = json.load(f)
  rt = jso['users'][user]['zip']
  return rt

def wexist(user):
 try:
  with open("wz-data.json", 'r') as f:
   jso = json.load(f)
   rt = jso['users'][user]
   return 1
 except:
   return 0

def ignoreurl():
 print("URL ignored.")
 
def gettimezone():
 localtime = reference.LocalTimezone()
 return localtime.tzname(datetime.datetime.now())

 
def restart():
 py = sys.executable
 seendb.savefile()
 wz.savedb()
 print("Restarting...")
 os.execl(py, py, * sys.argv)
 
 
def ttimer(room, dur, user):
         count = 0
         if dur > 172800:
          room.message("Too high")
         elif dur < 0:
          room.message("Not a positive number")
         else:
          while count != dur:
           time.sleep(1)
           count += 1
          room.message("Timeup for {u}".format(u=user))
   
   
   
def multi_message(room, arraylist): #Circumvents the timing bug, but does not circumvent the network latency, so it /should/ appear as correctly ordered in the console
 if type(arraylist) is list:
  if len(arraylist) > 5:
   room.message("Too long")
  else:
   for i in arraylist:
    room.message(i, True)
 else:
  room.message("Not a list")
   


################################################################
#Main Pinchybot Class, this is where the events are called
################################################################

class PinchyBot(ch.RoomManager):  #Main class


  def onConnect(self, room):
    print("["+curtime()+"] Connected to "+room.name)
    self.setFontColor(conf["FontColor"])
    self.setNameColor(conf["NameColor"])
    self.setFontSize(conf["FontSize"])

 

  def onReconnect(self, room):

    print("Reconnected to "+room.name)

  def onConnectFail(self, room):
      print("Failed to connect to "+room.name+ ", trying to reconnect..")
      room.reconnect()

 

  def onDisconnect(self, room):   #Wouldn't reconnect to the room unless you restart the script
    global partcommandisused
    print("[" + curtime() + "] Parted "+room.name+" (Disconnect)")
    
    if partcommandisused == True:
     partcommandisused = False
     pass
    else:
     roomtup = (self, room.name)
     thread.start_new_thread(self.conntimeout, (roomtup) )
     self.joinRoom(room.name)
     
  def conntimeout(self, room, roomstr):
   c = 0
   print("Waiting for timeout..")
   while self.getRoom(roomstr) == None:
    time.sleep(1)
    c += 1
    if c >= 60:
     print("Timeout")
     restart()
   print("Timeout abort")

  def onFloodWarning(self, room):
    print("Flood warning for %s, cooling down" % room.name)



  def onJoin(self, room, user):
      self.safePrint("[{ts}] {user} joined {room}".format(ts=curtime(),user=user.name,room=room.name))
      if conf['Greet'] == True:
       room.setSilent(False)
       room.message("{user} has joined, hi!".format(user=user.name))
      else:
       print("Greet omitted")

  def onLeave(self, room, user):
      self.safePrint("[{ts}] {user} left {room}".format(ts=curtime(),user=user.name,room=room.name))
      seendb.search(user.name, room.name, True)
      print("Replaced/Added element")
      
  def onBan(self, room, user, target): #Cannot see bans unless the bot is a moderator in the occurring room.
   print("[{ts}] User {t} banned from {r} by {u}".format(ts=curtime(),t=target.name,r=room.name,u=user.name))  
   
  def onUnban(self, room, user, target):
   print("[{ts}] User {t} unbanned from {r} by {u}".format(ts=curtime(),t=target.name,r=room.name,u=user.name))
   
  def onMessageDelete(self, room, user, message):
   print("[{ts}] ({r}) Message ({u}: {m}) deleted".format(ts=curtime(),r=room.name,u=user.name,m=message.body))   
    
 
  def onMessage(self, room, user, message):
    global echo
    global quiet
    global partcommandisused
    bl_pass = False
    unescaped_message = hparser.unescape(message.body)

    rstatus = blist(user.name) #Checks if a user is whitelisted
    if rstatus == True:
     print("User in blacklist, passing")
     bl_pass = True
    else:
     bl_pass = False
    ts = unescaped_message
    
    self.safePrint("[" + curtime() + "] (" + room.name + ") "+user.name + ': ' + unescaped_message)
    try: #Try statement over the bot's commands, If something goes wrong, throw a traceback and keep running
     urlpattern = "(https?://\S+)"
     regex = re.compile(urlpattern)
     url = regex.search(unescaped_message)
     cmd = '' #Otherwise UnboundLocalError is raised
     args = ''
	
     if unescaped_message:
      if bl_pass == True:
       pass
      elif unescaped_message[0] == cmdprefix: #Command prefix.
       data = unescaped_message[1:].split(" ", 1)

       if len(data) > 1: #To treat the second word to EOL as args, eg: "$eval" is the command, and "foo.bar()" is the argument parameter, if only command is issued, argument variable will be null

        cmd, args = data[0], data[1]

       else:

        cmd, args = data[0], None
      elif re.match("((?i)"+conf['Name'].lower()+", (?P<cmd>(\S+)) *(?P<args>(.*)))", unescaped_message): #Another type of issuing a command to the bot
       commandpattern = "((?i)"+conf['Name'].lower()+", (?P<cmd>(\S+)) *(?P<args>(.*)))"
       command_reg = re.compile(commandpattern)
       rawcommand = command_reg.search(unescaped_message)
       cmd = rawcommand.group("cmd")
       if rawcommand.group("args"):
        args = rawcommand.group("args")
       else:
        args = None
       print("command: {s}".format(s=cmd)) #Printing for verbosity, will be removed soon
       print("args: {s}".format(s=args))

################################################################
#Start of commands
################################################################

      if cmd == 'whoami':
       if user.name in conf["Admins"]:
        room.message('Bot admin')
       else:
        room.message('A puny user :3')
        
      elif cmd == 'restart':
       if user.name in conf["Admins"]:
        restart()

      elif cmd == 'join':
       if user.name in conf["Admins"]:
        self.joinRoom(args)

      elif cmd == 'part':
       if user.name in conf["Admins"]:
        partcommandisused = True
        self.leaveRoom(args)

      elif cmd == "eval":
       if user.name in conf["Admins"]:
        try:
         room.message(eval(args))
        except Exception as err:
         room.message('<b>Err:</b> ' + str(err), True)
         print(traceback.format_exc())
         logging.error("[" + curtime() + "] eval of {args} failed".format(args=args))
         
      elif cmd == 'say':
       if echo == 0:
        room.message(args)
       elif echo == 1:
        if user.name in conf["Admins"]:
         room.message(args)
       elif echo == 2:
         print("!say is disabled.")

      elif cmd == 'quiet':		#Command that the bot wont respond to any users issuing a command
       if user.name in conf["Admins"]:
        room.setSilent(True)
        quiet = 1

      elif cmd == 'enable':
       if user.name in conf["Admins"]:
        room.setSilent(False)
        quiet = 0

      elif cmd == 'hug':
       room.message('*hugs {user}*'.format(user=user.name))

      elif cmd == 'ping':
       room.message('Pong')

      elif cmd == '8ball':
       if args is None or args.isspace(): #A "this or that" statement in one if statement
        room.message("I need a question")
       else:
        rand = random.choice(open('8ball.txt', 'r').readlines())
        room.message(rand)
       

      elif cmd == 'google':
       searcharg = str(args.replace(" ", "+"))
       searchlink = "http://www.google.com/#q="+searcharg
       room.message(searchlink)

      elif cmd == 'roll.2':
       di1 = str(random.randrange(0, 9))
       di2 = str(random.randrange(0, 9))
       tot = di1 + di2
       room.message('You rolled ' + di1 +' '+ di2)

      elif cmd == 'flipcoin':
       rand = ['Heads', 'Tails']
       room.message(random.choice(rand))   

      elif cmd == "lusers":
       lst = ""
       lst = "<u>Users</u>:"
       for list in room.usernames:
        lst = lst + "<b>"+str(list)+"</b>"+", "
       room.message(lst, True)

      elif cmd == "otp":
       u1 = user.name
       u2 = random.choice(room.usernames)
       if u2 == u1:
        room.message(u1+" x... Never mind..")  #Selfcest, huehuehue
       else:
        room.message(u1+" x "+u2)

      elif cmd == 'calc':  #Remove old calc function
       room.message("This command is unsafe")

      elif cmd == 'shiny':
       shi = random.randint(1,65535)
       if shi <= 8:
        room.message('You got shiny!')
       else:
        room.message('Nope')


      elif cmd.startswith("goslate."):
       try:
        lang = cmd.split(".", 1)[1]
        trans = slate(args, lang).encode("utf-8").decode("utf-8")
        room.message(trans)
       except Exception as e:
        synmsg = "<b>Syntax</b>: !goslate.language Text here (where language is the abbreviation like 'ru')"
        room.message(synmsg, True)
        print(traceback.format_exc())

      elif cmd == "fontcolor":
       if user.name in conf["Admins"]:
        try:
         self.setFontColor(args)
        except:
         room.message("Wrong")

      elif cmd == "setfont":
       if user.name in conf["Admins"]:
        self.setFontColor(settings.fontcolor)
        self.setNameColor(settings.namecolor)
        self.setFontSize(settings.fontsize)
        room.message("Done")

      elif cmd.startswith("echo."):
       sw = cmd.split(".", 1)[1]
       if user.name in conf["Admins"]:
        if sw == "on":
         echo = 0
         room.message("!say command is now usable by all users")
        elif sw == "botadmin":
         echo = 1
         room.message("!say command is now botadmin only")
        elif sw == "off":
         echo = 2
         room.message("!say command is disabled.")
        else:
         room.message("Switches are: on, botadmin, and off")

      elif cmd.startswith("derpi."):   #Derpibooru command
       sw = cmd.split(".", 1)[1]
       if sw == "info":
         room.message("The !derpi.* command is a function that gets the stats off a derpibooru image using JSON, the available commands are: !derpi.img <image num ID> (Note: !derpi.img needs a moment to grab the stats), !derpi.tag <tag name>")


       elif sw == "spoiler":
        s1 = str(args.replace(" ", "+"))
        s1 = str(s1.replace(":", "-colon-"))
        tagct = derpi.tagsp(args)
        if tagct is None:
          room.message("No spoiler image for tag <b>{args}</b>".format(args=args), True)
        else:
          room.message("Spoiler image for tag <b>{arg}</b>: {spoilerurl}".format(arg=args,spoilerurl=tagct), True)

      elif cmd == "fontsize":
       if user.name in conf["Admins"]:
        try:
         self.setFontSize(args)
        except:
         room.message("Wrong")

      elif cmd == "namecolor":
       if user.name in conf["Admins"]:
        try:
         self.setNameColor(args)
        except:
         room.message("Wrong")

      elif cmd == "reverse":
       rev = str(args[::-1])
       room.message(rev)


      elif cmd == "pony":
       if room.name in conf['ExplicitRooms']:
        try:
         apikey = conf["derpi_APIKey"]
        except KeyError:
         apikey = None
       else:
        apikey = None
        
       if args is None or args.isspace():
        searchstring = derpi.randimg(None, apikey)
        room.message(searchstring, True)
       else:
        searchstring = derpi.randimg(args, apikey)
        room.message(searchstring, True)
        
      elif cmd == "quoteadd": #Probably dosen't work.
       if user.name in conf["Admins"]:
        with open('quotes.txt', 'a') as qfile:
         qfile.write(args)
         room.message("Added quote ("+args+") to file.")

      elif cmd == "greetmsg":  #so many if/else statements
       if user.name in conf["Admins"]:
        global greetmsg

        if args == "off":
          if greetmsg == False:
            room.message("It's already disabled")
          else:
            greetmsg = False
            room.message("Greet messages are now disabled")
        elif args == "on":
          if greetmsg == True:
            room.message("It's already enabled")
          else:
            greetmsg = True
            room.message("Greet messages are now enabled")
       else:
        room.message("Permission denied")

      elif cmd == "howbig":
       lines = str(len(open('pinchybot.py').readlines()))
       size = os.stat("pinchybot.py")
       room.message("The PinchyBot script is {size} bytes in size, and {lines} lines long".format(size=str(size.st_size),lines=lines))

      elif cmd == "uptime":
       u = str(uptime())
       room.message("Uptime: "+u)

      elif cmd == "fpix":
       link = "http://fp.chatango.com/profileimg/%s/%s/%s/full.jpg" % (args[0], args[1], args)
       room.message(link)

      elif cmd.startswith("timer"):
        try:
         timetuple = (room, int(args), user.name)
         thread.start_new_thread(ttimer, (timetuple) )
        except:
         print(traceback.format_exc())
         room.message("You did it wrong")

      elif cmd == "tag":
       null = ['null']
       s1 = str(args.replace(" ", "+"))
       s1 = str(s1.replace(":", "%3A"))
       s1 = str(s1.replace(",", "%2C"))
       tagct = derpi.tagsearch(args)
       searchlink = "https://derpibooru.org/search?utf8=?&sbq="+s1
       if tagct is None:
        emsg = "Tag <b>"+args+"</b>? That dosen't exist!"
        room.message(emsg, True)
       else:
        msg = searchlink+" Tag <b>"+args+"</b> has "+tagct+" images"
        room.message(msg, True)


      elif cmd == "wz":
       if args == None or args.isspace():
        msg = wz.info_string(None, True, user.name, conf["WZ-APIKey"])
        room.message(msg, True)
       else:
        msg = wz.info_string(args, False, user.name, conf["WZ-APIKey"])
        room.message(msg, True)

      elif cmd.startswith ("wz."):
       sw = cmd.split(".", 1)[1]
       if sw == "add":
        if args == None or args.isspace():
         room.message("You need to provide a location")
        else:
         wz.adduser(user.name, args)
         room.message("Your info has been added/updated in the database")
       elif sw == "remove":
        wz.rmuser(user.name)
        room.message("Your info has been removed from the database")

      elif cmd == "gimg":
       if room.name in conf['ExplicitRooms']:
        room.message(gimg.search(args))
       else:
        room.message("No")

      elif cmd == "tempconv.":
       sw = cmd.split(".", 1)[1]
       res = tempconv(sw, float(args))
       room.message(res)

      elif cmd == "cd":
       event = json.load(open("cd.json", "r"))
       timestamp = datetime.datetime.fromtimestamp(event['ts']).strftime('%Y-%m-%d %H:%M')
       if time.time() >= event['ts']:
        room.message("Time is already up ({tstamp})".format(tstamp=timestamp))
       else:
        timeremain = str(timedelta(seconds=int(event['ts'] - time.time())))
        room.message("Time remaining for <b>{evname}</b> is: {tremain} ({tstamp} {tz})".format(evname=event['EventName'],tremain=timeremain,tstamp=timestamp,tz=gettimezone()), True)

      elif cmd == "version":
       room.message("PinchyBot {ver} on Python {pyver}".format(ver=version_string,pyver=".".join(map(str, sys.version_info[:3]))))

      elif cmd == "cmdlist":
       room.message("http://pastebin.com/H3ktv6VT")
       
      elif cmd == 'dice': #Fixed that it can take numbers higher than 9
       try:
        darray = args.split("d", 1)[0:] #Returns an array such as ['2', '6']
        r1 = roll(int(darray[1]), int(darray[0]))
        room.message("{u} rolled {c}d{s}: ({r1}) = {tot}".format(u=user.name,s=darray[1],c=darray[0],r1=r1[0],tot=str(r1[1])))
       except:
        room.message("Usage example: $roll 2d6")
        print(traceback.format_exc())
        
      elif cmd == 'bt':
       if user.name in conf["Admins"]:
        with open("blacklist.txt", "a") as f:
         f.write(" {arg}".format(arg=args))
         room.message("Added user <u>{user}</u> to blacklist".format(user=args), True)
         
      elif cmd == 'systime':
       if user.name in conf["Admins"]:
        room.message(curtime())
        
      elif cmd.startswith("ponycd."):
       sw = cmd.split(".", 1)[1]
       if sw == "next":
        room.message(ponycountdown.nextep(), True)
       elif sw == "search":
        room.message(ponycountdown.epsearch(args), True)
        
      elif cmd == 'seen':
       if args == user.name:
        room.message("Are you looking at a mirror?")
       else:
        res = seendb.search(args, room.name, False)
        if res == None:
         room.message("I have not seen {u}".format(u=args))
        else:
         room.message("I last saw {u} on {r} at {t} {tz}".format(u=res[0],r=res[2],t=res[1], tz=gettimezone()))

       
################################################################
#Start of raw commands, merely a word without the command prefix
################################################################
     if unescaped_message.startswith("the game"):
      dish = random.randint(1, 9)
      if dish == 3:
       room.message("QUIET!")
      else:
       print("No.")

     elif unescaped_message.startswith("wat"):
      wat = random.randint(1, 20)
      if wat == 5:
       room.message("Wat.")
      else:
       print("No.")
       
     elif unescaped_message.startswith("ayy"):
      room.message("lmao")
################################################################
#Start of URL parsing
################################################################

     elif url:
      if user.name == conf["Name"].lower():
       print("Not parsing own URL")
      elif any(url.group(0).startswith(item) for item in conf["IgnoredURLs"]):
       print("Ignored URL")
      else:
       if re.match("(https?://(www.)?((derpibooru[.]org)|(derpiboo[.]ru))\S+)", url.group(0)): #Deripbooru URLs
        derpipattern = "(https?://(www.)?((derpibooru[.]org)|(derpiboo[.]ru))(/images/)?/?(?P<id>[0-9]*))"
        reg = re.compile(derpipattern)
        num = reg.search(url.group(0))
        statstr = derpi.stats_string(num.group("id"))
        multi_message(room, [statstr[0], statstr[1]])

       elif re.match("(https?://(www.)?((youtube[.]com)|(youtu[.]be))\S+)", url.group(0)): #Youtube URLs
        ytpattern = "(https://(www[.])?(?P<domain>(youtube[.]com)|(youtu[.]be))\S+)"
        reg = re.compile(ytpattern)
        yt_url = reg.search(url.group(0))
        if yt_url.group("domain") == "youtube.com":
         id = yt_url.group(0).split("/watch?v=", 1)[1]
         msg = yt.stats_string(id, conf["YT-APIKey"])
         room.message(msg, True)
         #function here
        elif yt_url.group("domain") == "youtu.be":
         id = yt_url.group(0).split(".be/", 1)[1]
         msg = yt.stats_string(id, conf["YT-APIKey"])
         room.message(msg, True)
        
       elif re.match("(https?://(www.)?fimfiction[.]net\S+)", url.group(0)): #FiMFiction URLs
        msg = fimfiction.statstring(url.group(0))
        room.message(msg, True)

       else:	#Any URLs that aren't ignored. The 'www' issue could pose a problem though
        title = urlparse(url.group(0))
        room.message(title, True)
################################################################
#End of URL parsing
################################################################
#Throw an exception without exiting if something happens
    except:
     print(traceback.format_exc())


################################################################       
#end of group chat commands
################################################################

  def onFloodBan(self, room):   #This is why i set the bot's testing room to slow mode
    print("You are flood banned in "+room.name)
    
    
  def onPMConnect(self, pm):
   print("Connected to PM")

    
  def onPMDisconnect(self, pm): #Should automatically reconnect upon disconnect
   print("Disconnected from PM")
   pm._connect()

  def onPMMessage(self, pm, user, body):
    global partcommandisused
    self.safePrint('['+curtime()+'] (PM) ' + user.name + ': ' + body) # '[HH:MM:SS](PM) username: message string'
    if body[0] == "$":     #Command prefix

      data = body[1:].split(" ", 1)

      if len(data) > 1:

        cmd, args = data[0], data[1]

      else:

        cmd, args = data[0], " "

################################################################
#start of PM commands
################################################################

      if cmd == "hi":
       pm.message(user, "Hai!")

      elif cmd == "info":
       pm.message(user, "I am a chatango bot coded in python, i was created by chaoticrift/crimsontail0 ( http://chaoticrift.chatango.com/ or http://crimsontail0.chatango.com/ ). The command list is here: http://pastebin.com/H3ktv6VT")

      elif cmd == "join":
       if user.name in conf["Admins"]:
        self.joinRoom(args)
        pm.message(user, "Joined "+args)
       else:
        pm.message(user, "Permission denied")

      elif cmd == "part":
       if user.name in conf["Admins"]:
        partcommandisused = True
        self.leaveRoom(args)
        pm.message(user, "Left "+args)
       else:
        pm.message(user, "Permission denied")

      elif cmd == "pony":
       if args is None or args.isspace():
        rand = derpi.randimg(None, False)
       else:
        rand = derpi.randimg(args, False)
       pm.message(user, rand)

      elif cmd == "howbig":
       lines = str(len(open('pinchybot.py').readlines()))
       size = os.stat("pinchybot.py")
       pm.message(user, "The PinchyBot script is {size} bytes in size, and {lines} lines long".format(size=str(size.st_size),lines=lines))

      elif cmd == '8ball':
       rand = ['Yes', 'No', 'Outlook so so', 'Absolutely', 'My sources say no', 'Yes definitely', 'Very doubtful', 'Most likely', 'Forget about it', 'Are you kidding?', 'Go for it', 'Not now', 'Looking good', 'Who knows', 'A definite yes', 'You will have to wait', 'Yes, in my due time', 'I have my doubts']
       pm.message(user, random.choice(rand))

#      elif cmd == 'bestpony':
#       poni = bestpone()
#       pm.message(user, poni)

      elif cmd == 'ping':
       pm.message(user, 'Pong')

      elif cmd == 'uptime':
       u = str(uptime())
       pm.message(user, "Uptime: "+u)
       
      elif cmd == "reverse":
       rev = str(args[::-1])
       pm.message(user, rev)

      elif cmd == "eval":
       if user.name in conf["Admins"]:
        try:
         logging.info("[" + curtime() + "] eval command used by " + user.name + ", trying to eval " + args)
         pm.message(user, eval(args))
        except Exception as err:
         pm.message(user, 'Err: ' + str(err))
       else:
         pm.message(user, "Permission denied")

      elif cmd == "version":
       pm.message(user, "PinchyBot {ver} on Python {pyver}".format(ver=version_string,pyver=".".join(map(str, sys.version_info[:3]))))
       
       


if __name__ == "__main__":  #Settings in another file
  #Initial PID printing for verbosity
  print("PID: {pid}".format(pid=str(os.getpid())))
  print("PPID: {ppid}".format(ppid=str(os.getppid())))
  try:
   cmdprefix = conf["CommandPrefix"]
  except KeyError:
   print("CommandPrefix not defined in config file, going with default prefix")
   cmdprefix = "$"
  seendb = seen.Seen()
  PinchyBot.easy_start(conf["Rooms"], conf["Name"], conf["Pass"])
