import os

from dotenv import load_dotenv
load_dotenv()

#Bot Token
#You need to setup a .env file with the bot key
BotKey = os.getenv("BOT_KEY")

#holds bot client
Client = ""

MapsDirectory = "Maps/"
SettingsDirectory = "Settings/"

MapsPath = f"{MapsDirectory}Maps.json"
NicknamesPath = f"{SettingsDirectory}nicknames.json"
IDsPath = f"{SettingsDirectory}steam_ids.json"

#Maps names sorted into categories
Categories = ["singleplayer",  "AMC", "glitchless", "inbounds", "OOB", "sla", "inboundNoSla"]

NonNative = [
    "singleplayer", "sp_a1_intro1", "sp_a1_intro2", "sp_a1_intro7", "sp_a1_wakeup", 
    "sp_a2_laser_intro", "sp_a2_catapult_intro", "sp_a2_bts6", "sp_a2_core", 
    "sp_a3_00", "sp_a4_intro", "sp_a4_finale1", 
    "AMC", "glitchless", "inbounds", "OOB", "sla", "inboundNoSla"
]

Coop = [
    "mp_coop_doors", "mp_coop_race_2", "mp_coop_laser_2", 
    "mp_coop_rat_maze", "mp_coop_laser_crusher", "mp_coop_teambts" "mp_coop_fling_3",
    "mp_coop_infinifling_train", "mp_coop_come_along", 
    "mp_coop_fling_1", "mp_coop_catapult_1", "mp_coop_multifling_1", 
    "mp_coop_fling_crushers", "mp_coop_fan", "mp_coop_wall_intro", 
    "mp_coop_wall_2", "mp_coop_catapult_wall_intro", "mp_coop_wall_block", "mp_coop_catapult_2", 
    "mp_coop_turret_walls", "mp_coop_turret_ball", "mp_coop_wall_5", "mp_coop_tbeam_redirect", 
    "mp_coop_tbeam_drill","mp_coop_tbeam_catch_grind_1", "mp_coop_tbeam_laser_1", "mp_coop_tbeam_polarity", 
    "mp_coop_tbeam_polarity2", "mp_coop_tbeam_polarity3", "mp_coop_tbeam_maze", "mp_coop_tbeam_end", 
    "mp_coop_paint_come_along", "mp_coop_paint_redirect", "mp_coop_paint_bridge", "mp_coop_paint_walljumps", 
    "mp_coop_paint_speed_fling", "mp_coop_paint_red_racer", "mp_coop_paint_speed_catch", "mp_coop_paint_longjump_intro", 
    "mp_coop_separation_1", "mp_coop_tripleaxis", "mp_coop_catapult_catch", "mp_coop_2paints_1bridge", 
    "mp_coop_paint_conversion", "mp_coop_bridge_catch", "mp_coop_laser_tbeam", "mp_coop_paint_rat_maze", 
    "mp_coop_paint_crazy_box"
]