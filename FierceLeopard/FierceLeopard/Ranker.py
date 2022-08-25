import os

from .Logger import *
from .Utils import *

from .Leaderboard import Leaderboard
from .Entry import Entry

class AppRanker:
  def __init__(self, app_id):
    self.Logger = Logger()

    self.app_id = app_id
    self.leaderboard_number = None
    
    self.data = []
    self.nicknames = {}
    self.steam_ids = {}

  def LoadNicknames(self, filename : str):
    self.nicknames = LoadJson(filename, self.Logger)
    
  def LoadSteamIDs(self, filename : str):
    self.steam_ids = LoadJson(filename, self.Logger)

  def LoadLeaderboard(self, lbname : str):
    lb = Leaderboard(self.app_id, lbname, self.Logger)
    url = lb.GetUrl()

    if not url:
      return

    self.leaderboard_number = url.split('/')[6]
      
    for name in self.steam_ids:
      if name not in self.nicknames:
        self.nicknames[name] = name

      entry = lb.GetEntry(self.steam_ids[name])

      if entry:
        entry.name = self.nicknames[name]
        self.Logger.Info(f"Found entry on Steam Leaderboards: {name}")
      else:
        self.Logger.Warn(f"Could not find entry {name} with id {self.steam_ids[name]}")
        continue

      self.ReplaceOrAppend(entry)
      
  def LoadFile(self, filename : str):
    file = LoadJson(filename, self.Logger)
    
    if not file:
      self.Logger.Warn(f"Could not load file {filename}")
      return None

    self.LoadDict(file, filename)
  
  def LoadDict(self, file : dict, filename : str = "dict"):
    for name in file:
      if name not in self.nicknames:
        self.nicknames[name] = name
      
      entry = Entry(self.nicknames[name], file[name], "Unknown")
      self.Logger.Info(f"Found entry in {filename}: {name} ")
      self.ReplaceOrAppend(entry)
      
  def ReplaceOrAppend(self, entry):
    for data in self.data:
      if entry.name == data.name:
        self.data[self.data.index(data)] = entry
        return
    
    self.data.append(entry)

  def GetResult(self):
    data = SortEntries(self.data)
    place = 0
    result = ""
    previous = Entry("Previous", "0.0", "Unknown")

    for key in data:
      if not previous.score == key.score:
        place += 1
        
      page = f"#{place} - {key.name}: {key.time}\n"
      
      previous.score = key.score
      result = result + page
      
    if not result: 
      result = self.Logger.GetWarnings()
      
    return result