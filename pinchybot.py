#!/usr/bin/python3.4


#PinchyBot for chatango
""""
Depends:
lxml
requests
pytz
goslate
"""
#Configuration is stored in a JSON file: "Name" string, "Pass" string, "Rooms" string array, "FontColor" string, "NameColor" string, and "FontSize" integer


################################
#Imports
################################
import ch
import string
import os
import random
import time
import sys
import datetime
import logging
import binascii
import re
from random import randint
import lxml.html
from xml.dom import minidom
import requests
import urllib.request
import _thread as thread
import json
from datetime import timedelta
import decimal
import hashlib
import traceback
import goslate
from mod import derpi, fimfiction, yt, gimg, wz, ponycountdown   #Because python 3 hates doing a "from foo import *" even though a __init__.py is present
import signal
from functools import reduce
from PIL import Image
from pytz import reference

################################################################
#Major.Minor.Micro
################################################################
version_string = "1.8.6"

################################################################
#Some global variables
################################################################
conf = json.load(open("settings.json", "r"))

echo = 0

total = 0

quiet = 0

logging.basicConfig(filename='logs/PinchyBot.log',level=logging.WARNING)

upt = time.time() #Grab current unix time upon execution



def sighandle(signal, frame):
 print("Caught SIGINT, exiting")
 sys.exit(0)

 
signal.signal(signal.SIGINT, sighandle)


def urlparse(url):    #URL parsing for title. Needs lxml
     f = requests.get(url)
     if f.status_code != 200:
      return str(f.status_code)
     else:
      s = lxml.html.fromstring(f.content) #lxml wants a consistently undecoded file, so f.content does it
      title = '[ '+s.find(".//title").text+" ]"
      return title
     
def readablesize(i):
 if i >= 1048576:
  size = float(i / 1048576)
  return "{s} MB".format(s=str("%.2f" % size))
 elif i >= 1024:
  size = float(i / 1024)
  return "{s} KB".format(s=str("%.2f" % size))
 else:
  return "{s} Bytes".format(s=str(i))
     
def imageparse(url):
  u = requests.get(url, stream=True, timeout=10)
  if u.status_code != 200:
   return ("Err: "+str(u.status_code), "N/A", "N/A")
  else:
   s = Image.open(u.raw)
   fsize = readablesize(int(u.headers["content-length"]))
   info = (fsize, s.size[0], s.size[1])
   return info

def slate(tran, lang): #I think they changed the translation API?
    gs = goslate.Goslate()
    tr = gs.translate(tran, lang)
    return tr


def readAdmin(user): #Boolean values are better in this case, and on similar defs
 if user in conf["Admins"]:
  return True
 else:
  return False

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

#def readRoom(room):					
#	bestand = open('arooms.txt', 'r')
#	for line in bestand:
#		if room in line:
#			rstatus = True
#			return rstatus
#		else:
#			rstatus = False
#			return rstatus

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


#def imgspec(url):
#    mime = ['.jpg', '.png', '.gif']
#    i = urllib2.urlopen(url)
#    return i.info()

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



################################################################
#Main Pinchybot Class, this is where the events are called
################################################################

class PinchyBot(ch.RoomManager):  #Main class




  def onConnect(self, room):
    
    print("Connected to "+room.name)
    self.setFontColor(conf["FontColor"])
    self.setNameColor(conf["NameColor"])
    self.setFontSize(conf["FontSize"])

 

  def onReconnect(self, room):

    print("Reconnected to "+room.name)

  def onConnectFail(self, room):
      print("Failed to connect to "+room.name+ ", trying to reconnect..")
      room.reconnect()

 

  def onDisconnect(self, room):   #Wouldn't reconnect to the room unless you restart the script
    ctime = curtime()
    print("[" + ctime + "] Parted "+room.name+" (Disconnect)")
    
    self.joinRoom(room.name)

  def onFloodWarning(self, room):
    room.setSilent(True)
    print("Flood warning for "+room.name+"!")



  def onJoin(self, room, user):
      ctime = curtime()
      self.safePrint("[{ts}] {user} joined {room}".format(ts=ctime,user=user.name,room=room.name))
      if conf['Greet'] == True:
       room.setSilent(False)
       room.message("{user} has joined, hi!".format(user=user.name))
      else:
       print("Greet omitted")

  def onLeave(self, room, user):
      ctime = curtime()
      self.safePrint("[{ts}] {user} left {room}".format(ts=ctime,user=user.name,room=room.name))
    
 
  def onMessage(self, room, user, message):
    global echo
    global quiet
     

    rstatus = blist(user.name) #Checks if a user is whitelisted
    if rstatus == True:
     room.setSilent(True)
     print("User in blacklist")
    elif quiet == 1:
     room.setSilent(True)
    else:
     room.setSilent(False)
    ctime = curtime()
    ts = message.body
    
    self.safePrint("[" + ctime + "] (" + room.name + ") "+user.name + ': ' + message.body)
    try: #Try statement over the bot's commands, unicode works however, but can crash after sending special characters such as Russian letters.
     urlpattern = "(https?://\S+)"
     regex = re.compile(urlpattern)
     url = regex.search(message.body)
	
     if message.body[0] == "$":     #Command prefix, it can be changed, but it must only be one character long

      data = message.body[1:].split(" ", 1)

      if len(data) > 1: #To treat the second word to EOL as args, eg: "$eval" is the command, and "foo.bar()" is the argument parameter, if only command is issued, argument variable will be null

       cmd, args = data[0], data[1]

      else:

        cmd, args = data[0], None

################################################################
#Start of commands
################################################################

      if cmd == 'whoami':
       status = readAdmin(user.name)
       if status == True:
        room.message('Bot admin')
       else:
        room.message('A puny user :3')

      elif cmd == 'join':
       status = readAdmin(user.name)
       if status == True:
        self.joinRoom(args)

      elif cmd == 'part':
       status = readAdmin(user.name)
       if status == True:
        self.leaveRoom(args)

      elif cmd == "eval":
       if readAdmin(user.name) == True:
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
        if readAdmin(user.name) == True :
         room.message(args)
       elif echo == 2:
         print("!say is disabled.")

      elif cmd == 'quiet':		#Command that the bot wont respond to any users issuing a command
       status = readAdmin(user.name)
       if status == True:
        room.setSilent(True)
        quiet = 1

      elif cmd == 'enable':
       status = readAdmin(user.name)
       if status == True:
        room.setSilent(False)
        quiet = 0

      elif cmd == 'hug':
       room.message('*hugs {user}*'.format(user=user.name))

#      elif cmd == 'bestpony':
#       poni = random.choice(open('bestpony.txt', 'r').readlines())
#       room.message(poni)

#      elif cmd == 'diabetes': # !pony probably makes this obsolete
#       dia = random.choice(open('diabetes.txt', 'r').readlines())
#       room.message(dia)

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
       status = readAdmin(user.name)
       if status == True:
        try:
         self.setFontColor(args)
        except:
         room.message("Wrong")

      elif cmd == "setfont":
       status = readAdmin(user.name)
       if status == True:
        self.setFontColor(settings.fontcolor)
        self.setNameColor(settings.namecolor)
        self.setFontSize(settings.fontsize)
        room.message("Done")


#      elif cmd == "restart": #Creates child process along with a second connection.
#       status = readAdmin(user.name)
#       if status == True:
#        room.message("Restarting..")
#        pid = str(os.getpid())
#        room.disconnect()
#        os.system("./rstart.sh "+pid)

      elif cmd.startswith("echo."):
       sw = cmd.split(".", 1)[1]
       status = readAdmin(user.name)
       if status == True:
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
       status = readAdmin(user.name)
       if status == True:
        try:
         self.setFontSize(args)
        except:
         room.message("Wrong")

      elif cmd == "namecolor":
       status = readAdmin(user.name)
       if status == True:
        try:
         self.setNameColor(args)
        except:
         room.message("Wrong")

      elif cmd == "reverse":
       rev = str(args[::-1])
       room.message(rev)


      elif cmd == "pony":
       if args is None or args.isspace():
        rand = derpi.randimg(None, False)
        room.message(rand)
       else:
        rand = derpi.randimg(args, False)
        room.message(rand)

""""
      elif cmd.startswith("dex."):   #Pokedex
       sw = cmd.split(".", 1)[1]
       if sw == 'name':
        try:
         urllib2.urlopen("http://pokemondb.net/pokedex/"+args)
         ps = "http://pokemondb.net/pokedex/"+args
         psp = "http://img.pokemondb.net/artwork/"+args+".jpg"
         room.message(psp+" "+ps)
        except:
         room.message("Dosen't exist (Don't use caps)")

       elif sw == 'img':
        try:
         urllib2.urlopen("http://img.pokemondb.net/artwork/"+args+".jpg")
         psp = "http://img.pokemondb.net/artwork/"+args+".jpg"
         room.message(psp)
        except:
         room.message("Dosen't exist (Don't use caps)")
       elif sw == 'gen1':
         room.message("#001-#151")
       elif sw == 'gen2':
         room.message("#152-#251")
       elif sw == 'gen3':
         room.message("#252-#386")
       elif sw == 'gen4':
         room.message("#387-#493")
       elif sw == 'gen5':
         room.message("#494-#649")
       elif sw == 'gen6':
         room.message("#650-#718")
""""


      elif cmd == "quoteadd": #Probably dosen't work.
       status = readAdmin(user.name)
       if status == True:
        with open('quotes.txt', 'a') as qfile:
         qfile.write(args)
         room.message("Added quote ("+args+") to file.")

      elif cmd == "greetmsg":  #so many if/else statements
       status = readAdmin(user.name)
       if status == True:
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

#      elif cmd == "quote":
#       qmsg = random.choice(open('quotes.txt', 'r').readlines())
#       room.message(qmsg)

#      elif cmd == "sauce":
#       rstatus = readRoom(room.name)
#       if rstatus == True:
#        sauce = random.choice(open('sauce.txt', 'r').readlines())
#        room.message(sauce)

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

      elif cmd.startswith("timer."):
       sw = cmd.split(".", 1)[1]
       if sw == 's':
        def ttimer( dur, u):
         count = 0
         while True:
          time.sleep(1)
          count += 1
          if count == dur:
           print("Timeup")
           room.message("Timeup for {u}".format(u=user.name))
           break
        try:
         if int(args) <= 0:
          room.message("Number needs to be higher than 0")
         elif int(args) > 172800:
          room.message("Upper limit is 172800")
         else:
          thread.start_new_thread(ttimer, (int(args), user.name ) )
          room.message("Timer started for %s seconds for %s" % (args, user.name))
          
        except:
         room.message("You did it wrong")

       elif sw == 'm':
        def ttimer( dur, u):
         count = 0
         while True:
          time.sleep(60)
          count += 1
          if count == dur:
           print("Timeup")
           room.message("Timeup for %s!" % (u))
           break
        try:
         if int(args) <= 0:
          room.message("Number needs to be higher than 0")
         elif int(args) > 2880:
          room.message("Upper limit is 2880")
         else:
          thread.start_new_thread(ttimer, (int(args), user.name ) )
          room.message("Timer started for %s minutes for %s" % (args, user.name))
          
        except:
         room.message("You did it wrong")

       elif sw == 'h':
        def ttimer( dur, u):
         count = 0
         while True:
          time.sleep(3600)
          count += 1
          if count == dur:
           print("Timeup")
           room.message("Timeup for %s!" % (u))
           break
        try:
         if int(args) <= 0:
          room.message("Number needs to be higher than 0")
         elif int(args) > 48:
          room.message("Upper limit is 48")
         else:
          thread.start_new_thread(ttimer, (int(args), user.name ) )
          room.message("Timer started for %s hours for %s" % (args, user.name))
          
        except:
         room.message("You did it wrong")



      elif cmd.startswith("help."):
       sw = cmd.split(".", 1)[1]
       hcmd = ['main', 'derpi', 'dex']
       if sw not in hcmd:
        room.message("Syntax: !help.directive (Available directives are: main, derpi, dex)")
       elif sw == 'main':
        room.message("General commands: !hug, !bestpony, !diabetes, !ping, !8ball, !dice, !google, !flipcoin, !lusers, !otp, !shiny")
       elif sw == 'derpi':
        room.message("The !derpi.* command is a function to print stats of an image from derpibooru. (See !derpi.info for available commands)")
        room.message("URLs matching http://derpiboo.ru/ or http://derpibooru.org/ with the image page will automatically be parsed.")
       elif sw == 'dex':
        room.message("National Pokedex. This function links an image of the pokemon, plus the link to its info. The available commands are !dex.name <name of pokemon> (Exclude the brackets and do not use caps), !dex.img <name> (This goes for alternate forms such as Shaymin's Sky forme (shaymin-sky)", True)




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
       try:
        jso = json.load(open("wz-data.json", "r"))
        msg = wz.wstring(jso["users"][user.name]["zip"], jso["users"][user.name]["metric"])
        room.message(msg, True)
       except Exception as e:
        print("nope ("+str(e)+")")
        room.message("I don't have your weather data stored, ask the owner if you want your data stored, otherwise use !wz.zip <zip code>")

      elif cmd.startswith ("wz."):
       sw = cmd.split(".", 1)[1]
       if sw == "zip":
        try:
         msg = wz.info_string(args)
         room.message(msg, True)
        except:
         room.message("I need a zip code")

        

      elif cmd == 'metric':
       met = UserMetric(user.name)
       if met == 1:
        room.message("Your setting is currently set to Metric. Ask the bot owner if you want to change this setting.")
       else:
        room.message("Your setting is currently set to Imperial(Default setting), ask the bot owner if you want to change this setting.")

      elif cmd == "gimg":
       room.message(gimg.search(args))

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
       status = readAdmin(user.name)
       if status == True:
        with open("blacklist.txt", "a") as f:
         f.write(" {arg}".format(arg=args))
         room.message("Added user <u>{user}</u> to blacklist".format(user=args), True)
         
      elif cmd == 'systime':
       status = readAdmin(user.name)
       if status == True:
        room.message(curtime())
        
      elif cmd.startswith("ponycd."):
       sw = cmd.split(".", 1)[1]
       if sw == "next":
        room.message(ponycountdown.nextep(), True)
       elif sw == "search":
        room.message(ponycountdown.epsearch(args), True)

      
       
################################################################
#Start of raw commands, merely a word without the command prefix
################################################################
     if message.body.startswith("the game"):
      dish = random.randint(1, 9)
      if dish == 3:
       room.message("QUIET!")
      else:
       print("No.")

     elif message.body.startswith("wat"):
      wat = random.randint(1, 20)
      if wat == 5:
       room.message("Wat.")
      else:
       print("No.")
################################################################
#Start of URL parsing
################################################################

      elif url:
      if user.name == conf["Name"].lower():
       print("Not parsing own URL")
      else:
      #HTTPS start
       if re.match("(https://\S+)", url.group(0)):
        print("URL: {url}".format(url=url.group(0)))

        if re.match("(https://derpibooru[.]org\S+)", url.group(0)):
         num = url.group(0).split("g/", 1)[1]
         num = num.split("?")[0]
         msg = derpi.stats_string(num)
         if msg is None:
          room.message("Dosen't exist?")
         else:
          room.message(msg[0], True)
          room.message(msg[1], True)

        elif re.match("(https://derpiboo[.]ru\S+)", url.group(0)):
         num = url.group(0).split("u/", 1)[1]
         num = num.split("?")[0]
         msg = derpi.stats_string(num)
         if msg is None:
          room.message("Dosen't exist?")
         else:
          room.message(msg[0], True)
          room.message(msg[1], True)

        elif re.match("(https://www[.]youtube[.]com\S+)", url.group(0)):
         try:
          vid = message.body.split("watch?v=", 1)[1]
          string = yt.stats_string(vid)
          room.message(string, True) 
         except:
          print(traceback.format_exc())
          
        elif re.match("(https://youtu[.]be\S+)", url.group(0)):
         try:
          vid = message.body.split(".be/", 1)[1]
          string = yt.stats_string(vid)
          room.message(string, True) 
         except:
          print(traceback.format_exc())

        elif url.group(0).startswith ("https://img.pokemondb.net/artwork/"):
         ignoreurl()

        elif url.group(0).endswith (".jpg"):
         imginfo = imageparse(url.group(0))
         room.message("JPG image, {size}, {w} x {h}".format(size=imginfo[0],w=imginfo[1],h=imginfo[2]))

        elif url.group(0).endswith (".png"):
         imginfo = imageparse(url.group(0))
         room.message("PNG image, {size}, {w} x {h}".format(size=imginfo[0],w=imginfo[1],h=imginfo[2]))
        elif url.group(0).endswith (".gif"):
         imginfo = imageparse(url.group(0))
         room.message("GIF image, {size}, {w} x {h}".format(size=imginfo[0],w=imginfo[1],h=imginfo[2]))

        else:	#Any URLs that aren't ignored. The 'www' issue could pose a problem though
         title = urlparse(url.group(0))
         room.message(title, True)

#end of https url parsing
	
#start of http url parsing

       elif re.match("(http://\S+)", url.group(0)):
        print("URL: {url}".format(url=url.group(0)))

        if re.match("(http://derpibooru[.]org\S+)", url.group(0)):  #Starting here is URLs the bot will ignore, this includes image URLs
         num = url.group(0).split("g/", 1)[1]
         num = num.split("?")[0]
         msg = derpi.stats_string(num)
         if msg is None:
          room.message("Dosen't exist?")
         else:
          room.message(msg[0], True)
          room.message(msg[1], True)

        elif re.match("(http://derpiboo[.]ru\S+)", url.group(0)):
         num = url.group(0).split("u/", 1)[1]
         num = num.split("?")[0]
         msg = derpi.stats_string(num)
         if msg is None:
          room.message("Dosen't exist?")
         else:
          room.message(msg[0], True)
          room.message(msg[1], True)
          
        elif re.match("(http://www[.]fimfiction[.]net\S+)", url.group(0)):
         try:
          msgstr = fimfiction.statstring(url.group(0))
          room.message(msgstr, True)
         except:
          print(traceback.format_exc())


        elif re.match("(http://www[.]youtube[.]com\S+)", url.group(0)):
         try:
          vid = url.group(0).split("watch?v=", 1)[1]
          string = yt.stats_string(vid)
          room.message(string, True) 
         except:
          print("derp")
          
        elif re.match("(http://youtu[.]be\S+)", url.group(0)):
         try:
          vid = message.body.split(".be/", 1)[1]
          string = yt.stats_string(vid)
          room.message(string, True) 
         except:
          print(traceback.format_exc())
          
        elif url.group(0).endswith (".jpg"):
         imginfo = imageparse(url.group(0))
         room.message("JPG image, {size}, {w} x {h}".format(size=imginfo[0],w=imginfo[1],h=imginfo[2]))

        elif url.group(0).endswith (".png"):
         imginfo = imageparse(url.group(0))
         room.message("PNG image, {size}, {w} x {h}".format(size=imginfo[0],w=imginfo[1],h=imginfo[2]))
        elif url.group(0).endswith (".gif"):
         imginfo = imageparse(url.group(0))
         room.message("GIF image, {size}, {w} x {h}".format(size=imginfo[0],w=imginfo[1],h=imginfo[2]))
        else:
         title = urlparse(url.group(0))
         room.message(title, True)
################################################################
#End of URL parsing
################################################################

    except:
     print(traceback.format_exc())


################################################################       
#end of group chat commands
################################################################

  def onFloodBan(self, room):   #This is why i set the bot's testing room to slow mode
    print("You are flood banned in "+room.name)

  def onPMMessage(self, pm, user, body):
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
       status = readAdmin(user.name)
       if status == True:
        self.joinRoom(args)
        pm.message(user, "Joined "+args)
       else:
        pm.message(user, "Permission denied")

      elif cmd == "part":
       status = readAdmin(user.name)
       if status == True:
        self.leaveRoom(args)
        pm.message(user, "Left "+args)
       else:
        pm.message(user, "Permission denied")

      elif cmd == "pony":
       if args is None or args.isspace():
        rand = derpi.randimg(None)
       else:
        rand = derpi.randimg(args)
       pm.message(user, rand)

      elif cmd == "howbig":
       lines = str(len(open('pinchybot.py').readlines()))
       size = os.stat("pinchybot.py")
       pm.message(user, "The PinchyBot script is {size} bytes in size, and {lines} lines long".format(size=str(size.st_size),lines=lines))

      elif cmd == '8ball':
       rand = ['Yes', 'No', 'Outlook so so', 'Absolutely', 'My sources say no', 'Yes definitely', 'Very doubtful', 'Most likely', 'Forget about it', 'Are you kidding?', 'Go for it', 'Not now', 'Looking good', 'Who knows', 'A definite yes', 'You will have to wait', 'Yes, in my due time', 'I have my doubts']
       pm.message(user, random.choice(rand))

      elif cmd == 'bestpony':
       poni = bestpone()
       pm.message(user, poni)

      elif cmd == 'ping':
       pm.message(user, 'Pong')

      elif cmd == 'uptime':
       u = str(uptime())
       pm.message(user, "Uptime: "+u)
       
      elif cmd == "reverse":
       rev = str(args[::-1])
       pm.message(user, rev)

      elif cmd == "eval":
       status = readAdmin(user.name)
       if status == True:
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
  PinchyBot.easy_start(conf["Rooms"], conf["Name"], conf["Pass"])

