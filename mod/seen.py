import dataset
import time
import datetime


def curtime(): #Return string of current time in Y-m-D H:M:S format
    ts = time.time()
    st = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    return st

class Seen:

 def __init__(self):
  self.db = dataset.connect('sqlite:///SeenData.db')
  self.dbtable = self.db["SeenTable"]

 def savefile(self): #Use this upon exit
  print("Committing changes to database...")
  self.db.commit()

 def loadfile(self): #Might not be needed
  print("Loading database")
  self.db = dataset.connect('sqlite:///SeenData.db')
  self.dbtable = self.db["SeenTable"]

 def search(self, user, room, replace): #Search for user
  t = self.dbtable.find_one(Username=user)
  if replace == True:
   if t:
    #Update
    ID = t['id']
    self.dbtable.update(dict(id=ID, Username=user, Time=curtime(), Room=room), ['id'])
   else:
    #Place new row
    print("Nothing to replace, placing new row")
    self.dbtable.insert(dict(Username=user, Time=curtime(), Room=room))
  else:
   if t:
    res_tuple = (t['Username'], t['Time'], t['Room'])
    return res_tuple
   else:
    return None
   #Search and return
 
