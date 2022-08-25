import os
import json

import requests
from bs4 import BeautifulSoup

from .Logger import *

def LoadJson(path):
  data = {}

  if os.path.exists(path):
    with open(path, "r") as f:
      data = json.load(f)
  else:
    Logger.Warn(f"File {path} does not exist!")
  
  return data 

def DumpJson(path, js):
  with open(path, "w") as f:
      json.dump(js, f, indent=2)

def SortEntries(data):
  swapped = True
  while swapped:
    swapped = False 
    for i in range(len(data) - 1):
      if data[i].score > data[i + 1].score:
        data[i], data[i + 1] = data[i + 1], data[i]
        swapped = True
  return data

def LoadUrl(url):
  res = requests.get(url)

  try:
    soup = BeautifulSoup(res.content, features="xml")
  except:
    Logger.Warn(f"Could not load url {url}")
    return None

  return soup