import os
import json

import Storage
import Logger

NoSettingsMessage = "Please Setup Bot to Continue!\n%setup [prefix you wish to use] [roles that can change others data]"
RequiredRolesMessage = "You do not have any of the required roles!"

async def GetSettings(guild_id : int, ctx = None, error = True):
    if not os.path.exists(f'Settings/{guild_id}.json'):
        if ctx and error:
            await ctx.send(NoSettingsMessage)
        
        return False

    with open(f'{Storage.SettingsDirectory}{guild_id}.json', 'r') as f:
        return json.load(f)

async def FindSettings(guild_id : int, ctx = None):
    pathExists = os.path.exists(f'{Storage.SettingsDirectory}{guild_id}.json')
    if not pathExists and ctx:
        await ctx.send(NoSettingsMessage)
    
    return pathExists

def LoadJson(path):
    data = {}

    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        Logger.Error(f"File {path} does not exist!")
    
    return data 

def LoadJsonForGuild(path, guild_id : int):
    data = LoadJson(path)
    if not data:
      return {}

    if not str(guild_id) in data:
      Logger.Error(f"Guild ID was not found in file {path}")
      return {}
    
    return data[str(guild_id)]

def DumpJson(path, js):
    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))

    with open(path, "w") as f:
        json.dump(js, f, indent=2)      

async def UserHasRequiredRoles(required_roles, user, ctx):
    found = False
    for user_role in user.roles:
        if str(user_role) in required_roles:
            found = True
            break

    if not found:
        await ctx.send(RequiredRolesMessage)
    
    return found

def FindValueInArray(val, arr):
    if val not in arr:
        for key in arr:
            if arr[key] == val:
                val = key
                break

    return val
