import requests
from bs4 import BeautifulSoup
import typing

class LeaderboardGroup():
    def __init__(self, app_id):
        xml = requests.get(f"https://steamcommunity.com/stats/{app_id}/leaderboards/?xml=1")
        _bs = BeautifulSoup(xml.content, features="lxml")
        self.leaderboards = []
        self.app_id = app_id
        for leaderboard in _bs.find_all("leaderboard"):
            self.leaderboards.append(ProtoLeaderboard(leaderboard, app_id))

    def __repr__(self):
        return f"<LeaderboardGroup for {self.app_id} with {len(self.leaderboards)} leaderboards>"

    def get(self, name=None, *, lbid=None, display_name=None) -> typing.Optional["Leaderboard"]:
        if bool(lbid) + bool(name) + bool(display_name) > 1:
            raise ValueError("You can only find a leaderboard by 1 parameter.")
        if lbid is not None:
            if not isinstance(lbid, int):
                raise ValueError("lbid must be an int")
            for leaderboard in self.leaderboards:
              if leaderboard.lbid == lbid:
                  return leaderboard.full()
        elif name is not None:
            if not isinstance(name, str):
                raise ValueError("name must be a str")
            for leaderboard in self.leaderboards:
              if str(leaderboard.name) == name:
                  return leaderboard.full()
        elif display_name is not None:
            if not isinstance(display_name, str):
                raise ValueError("display_name must be a str")
            for leaderboard in self.leaderboards:
              if str(leaderboard.display_name) == display_name:
                  return leaderboard.full()
        return None

class ProtoLeaderboard:
    def __init__(self, soup, app_id):
        self.url = soup.url.text
        self.lbid = int(soup.lbid.text)
        self.name = soup.find("name").text
        self.display_name = soup.display_name.text
        self.entries = int(soup.entries.text)
        self.sort_method = int(soup.sortmethod.text)
        self.display_type = int(soup.displaytype.text)
        self.app_id = app_id\

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
            self.display_type = protoleaderboard.display_type
            self.app_id = protoleaderboard.app_id

            self.all_entries = []
            xml = requests.get(self.url)
            _bs = BeautifulSoup(xml.content, features="lxml")
            for entry in _bs.entries:
              self.all_entries.append(entry)

    def __repr__(self):
      pass

    def find_entry(self, steam_id=None, *, rank=None):
        if bool(steam_id) + bool(rank) > 1:
            raise ValueError("You can only find an entry by 1 parameter.")
        if steam_id is not None:
            if not isinstance(steam_id, int):
                raise ValueError("steam_id must be a int")
            for entry in self.all_entries:
              if int(entry.steamid.text) == steam_id:
                  return entry
            else:
                return None
        elif rank is not None:
            if not isinstance(rank, int):
                raise ValueError("steam_id must be an int")
            try:
                return self.all_entries[rank - 1]
            except IndexError:
                return None