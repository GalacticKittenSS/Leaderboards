import requests
from bs4 import BeautifulSoup

class LeaderboardGroup():
    def __init__(self, app_id, name):
        xml = requests.get(f"https://steamcommunity.com/stats/{app_id}/leaderboards/?xml=1")
        _bs = BeautifulSoup(xml.content, features="lxml")
        self.app_id = app_id
        for leaderboard in _bs.find_all("leaderboard"):
          if leaderboard.find("name").text == name:
            self.leaderboard = ProtoLeaderboard(leaderboard, app_id)

    def __repr__(self):
        return f"<LeaderboardGroup for {self.app_id} with {len(self.leaderboards)} leaderboards>"

    def get(self):
      return self.leaderboard.full()

class ProtoLeaderboard:
    def __init__(self, soup, app_id):
        self.url = soup.url.text
        self.lbid = int(soup.lbid.text)
        self.name = soup.find("name").text
        self.display_name = soup.display_name.text
        self.entries = int(soup.entries.text)
        self.sort_method = int(soup.sortmethod.text)
        self.display_type = int(soup.displaytype.text)
        self.app_id = app_id

    def full(self) -> "Leaderboard":
        return Leaderboard(protoleaderboard=self)

class Leaderboard:
    def __init__(self, app_id=None, lbid=None, *, protoleaderboard=None):
        if protoleaderboard:
            self.url = protoleaderboard.url
            self.lbid = protoleaderboard.lbid
            self.name = protoleaderboard.name
            self.display_name = protoleaderboard.display_name
            self.entry_number = protoleaderboard.entries
            self.sort_method = protoleaderboard.sort_method
            self.app_id = protoleaderboard.app_id
            
            xml = requests.get(self.url)
            _bs = BeautifulSoup(xml.content, features="lxml")
            self.all_entries = _bs.entries

    def __repr__(self):
      pass

    def find_entry(self, steam_id=None, *, rank=None):
        if bool(steam_id) + bool(rank) > 1:
            raise ValueError("You can only find an entry by 1 parameter.")
        if steam_id is not None:
            if not isinstance(steam_id, int):
                raise ValueError("Steam id must be a int")
            for entry in self.all_entries:
              if int(entry.steamid.text) == steam_id:
                  return entry
            else:
                return None
        elif rank is not None:
            if not isinstance(rank, int):
                raise ValueError("Rank must be an int")
            try:
                return self.all_entries[rank - 1]
            except IndexError:
                return None