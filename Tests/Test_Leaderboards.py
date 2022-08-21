## For better results add more users into the data/steam_ids
import time

import Setup

import Logger
import SteamLeaderboards

Logger.Info("Beginning SteamLeaderboards Tests\n")

Guild_ID = 0
tests_dir = "Tests/Data/"
id_file = f"{tests_dir}steam_ids.json"
nickname_file = f"{tests_dir}nicknames.json"

## Check Mixed Leaderboards (Steam/Files)
tic = time.perf_counter()

Logger.Info("Initializing Leaderboard Group")
leaderboard = SteamLeaderboards.LeaderboardGroup(620, Guild_ID)

Logger.Info("Loading Files...")
leaderboard.LoadSteamIDs(id_file)
leaderboard.LoadNicknames(nickname_file)

Logger.Info("Leaderboard.CreateFromSteam...")
leaderboard.CreateFromSteam("challenge_besttime_sp_a1_intro4")
Logger.Info("Leaderboard.CreateFromFile...")
leaderboard.CreateFromFile(f"{tests_dir}sp_a1_intro4.json")

Logger.Info(f"https://board.portal2.sr/chamber/{leaderboard.SteamLeaderboardNumber()}")
Logger.Info(f"Took {(time.perf_counter() - tic):0.4} seconds with result...\n")
print(leaderboard.GetResult())

## Check Error Messages
Logger.Info("Checking Errors/Warnings...")
Error = SteamLeaderboards.LeaderboardGroup(12, 210)
Error.LoadSteamIDs("this/path/does/not.exist")
Error.LoadNicknames("this/path/does/not.exist")
Error.CreateFromSteam("this_leaderboard_does_not_exist")
Error.CreateFromFile("this/path/does/not.exist")

Logger.Info("Result...\n")
print(Error.GetResult())

print()