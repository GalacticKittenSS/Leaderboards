import os
import json

NoSettingsMessage = "Please Setup Bot to Continue!\n%setup [prefix you wish to use] [roles that can change others data]"
RequiredRolesMessage = "You do not have any of the required roles!"

async def GetSettings(guild_id : int, ctx = None, error = True):
    if not os.path.exists(f'Settings/{guild_id}.json'):
        if ctx and error:
            await ctx.send(NoSettingsMessage)
        
        return False

    with open(f'Settings/{guild_id}.json', 'r') as f:
        return json.load(f)

async def FindSettings(guild_id : int, ctx = None):
    pathExists = os.path.exists(f'Settings/{guild_id}.json')
    if not pathExists and ctx:
        await ctx.send(NoSettingsMessage)
    
    return pathExists

def GetJson(path):
    js = {}

    if os.path.exists(path):
        with open(path, "r") as f:
            js = json.load(f)

    return js 

def DumpJson(path, js):
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
