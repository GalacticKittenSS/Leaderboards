import os

import requests
from bs4 import BeautifulSoup

from .Logger import *
from .Utils import *

from .Entry import SteamEntry

class Leaderboard:
  def __init__(self, app_id, lbname):
    self.url = self.LoadUrl(app_id, lbname)
  
  def LoadUrl(self, app_id, lbname):
    url = f"https://steamcommunity.com/stats/{app_id}/leaderboards/{lbname}?xml=1"
    soup = LoadUrl(url)

    if not soup:
      return

    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == lbname:
        return leaderboard.url.text

    Logger.Warn(f"Leaderboard {lbname} was not found")
    return
  
  def GetEntry(self, steam_id):
    res = requests.get(self.url + f"&steamid={steam_id}")
    soup = BeautifulSoup(res.content, features="xml")

    for entry in soup.find_all("entry"):
      if entry.steamid.text == str(steam_id):
        return SteamEntry(entry)
    
    return None

  def GetUrl(self, *, steam_id=0):
    url = self.url

    if steam_id != 0:
      url = url + f"&steamid={steam_id}"

    return url
