class Entry:
  def __init__(self, name, score, rank):
    self.name = name
    self.score = score.replace(".", "")
    self.rank = rank
    self.time = score 

  def ConvertScore(self, score):
    secs, ms = score[:len(score) - 2], score[len(score) - 2:]
    minutes = int(secs) // 60
    seconds = int(secs) % 60
  
    if seconds < 10:
      seconds = f"0{seconds}"
  
    if minutes != 0:
      result = f"{minutes}:{seconds}"
    else:
      result = f"{seconds}"
    
    tm = f"{result}.{ms}"

    return tm

class SteamEntry(Entry):
  def __init__(self, entry):
    self.steam_id = entry.steamid.text
    self.score = entry.score.text
    self.time = self.ConvertScore(self.score)
    self.rank = entry.rank.text
    self.name = self.steam_id