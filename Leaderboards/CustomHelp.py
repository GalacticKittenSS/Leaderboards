import discord
from discord.ext import commands

import os
import json
import itertools

import Storage

class Help(commands.DefaultHelpCommand):
  def __init__(self, **options):
    self.paginator = options.pop('paginator', None)
    
    if self.paginator is None:
      self.paginator = commands.help.Paginator()
      
    super().__init__(**options)
    self.paginator.__init__("", "")
    
  def add_command_formatting(self, command):
    if command.description:
     self.paginator.add_line(command.description, empty=True)
     
    signature = get_command_signature(command)
    self.paginator.add_line(signature, empty=True)
     
    if command.help:
      try:
        self.paginator.add_line(command.help, empty=True)
      except RuntimeError:
        for line in command.help.splitlines():
          self.paginator.add_line(line)
        self.paginator.add_line()

  async def send_pages(self, channel = None, message = None, allPages=False):
    if not allPages:
      destination = self.get_destination()
      
      file = { "Help": {}}
      if os.path.exists(f"Settings/{destination.guild.id}.json"):
        file = json.load(open(f"Settings/{destination.guild.id}.json", "r"))
      
      for page in self.paginator.pages:
          embed = discord.Embed(title="Help", description=page)
          
          if not message:
            message = await destination.send(embed=embed)
          
          await message.edit(embed=embed)
          
          Storage.current_sorted_commands = page
          Storage.current_help_commands.append(page)

          file["Help"]["Message"] = message.id
          file["Help"]["Channel"] = message.channel.id
          file["Help"]["Index"] = -1
  
          await message.add_reaction("⏮️")
          await message.add_reaction("⏭️")
          
      with open(f"Settings/{message.guild.id}.json", "w") as f:
        json.dump(file, f, indent=2)
    else:
        page = Storage.current_sorted_commands
        embed = discord.Embed(title="Help", description=page)
        await message.edit(embed=embed)
    
    self.paginator.clear()
          
  async def send_bot_help(self, mapping):
    sorted = await super().filter_commands(Storage.Client.commands, sort=True)
    sorted = itertools.groupby(sorted)

    Storage.current_help_commands = []

    for command, category in sorted:
      Storage.current_help_commands.append(command)

    await super().send_bot_help(mapping)
  
  async def send_cog_help(self, cog):
    await super().send_cog_help(cog)
    
  async def send_group_help(self, group):
    await super().send_group_help(group)
    
  async def send_next_help(self, channel, message, allPages=False, command = None):
    if not allPages:
        self.add_command_formatting(command)
        self.paginator.close_page()
    
    await self.send_pages(channel, message, allPages)

  async def send_command_help(self, command):
    self.add_command_formatting(command)
    self.paginator.close_page()
    await self.send_pages()

  async def reaction(self, client, payload):
    if not os.path.exists(f"Settings/{payload.guild_id}.json"):
      return
    
    file = json.load(open(f"Settings/{payload.guild_id}.json", "r"))

    if payload.user_id == client.user.id or payload.message_id != file["Help"]["Message"]:
        return

    channel = client.get_channel(file["Help"]["Channel"])
    message = await channel.fetch_message(file["Help"]["Message"])

    commands = Storage.current_help_commands
    index = file["Help"]["Index"]

    if payload.emoji.name == "⏭️":
        index += 1
    if payload.emoji.name == "⏮️":
        index -= 1

    if index == len(commands):
        index = 0
    
    if index == -1:
        index = len(commands) - 1

    await message.remove_reaction("⏭️", client.get_user(payload.user_id))
    await message.remove_reaction("⏮️", client.get_user(payload.user_id))

    file["Help"]["Index"] = index

    with open(f"Settings/{payload.guild_id}.json", "w") as f:
        json.dump(file, f, indent=2)

    all = False

    if index == len(commands) - 1:
        all = True

    await self.send_next_help(command=commands[index], channel=channel, message=message, allPages=all)

def get_command_signature(command):
    parent = command.parent
    entries = []
    while parent is not None:
        if not parent.signature or parent.invoke_without_command:
            entries.append(parent.name)
        else:
            entries.append(parent.name + ' ' + parent.signature)
        parent = parent.parent
    parent_sig = ' '.join(reversed(entries))

    if len(command.aliases) > 0:
        aliases = '|'.join(command.aliases)
        fmt = '[%s|%s]' % (command.name, aliases)
        if parent_sig:
            fmt = parent_sig + ' ' + fmt
        alias = fmt
    else:
        alias = command.name if not parent_sig else parent_sig + ' ' + command.name

    return '%s%s %s' % ("%", alias, command.signature)