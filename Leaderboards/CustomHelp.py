import discord
from discord.ext import commands

import os
import json
import itertools

import Storage
import Utils

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

  async def send_pages(self, channel = None, message = None, allCommands=False):
    if not allCommands:
      if not channel:
        channel = self.get_destination()

      file = Utils.LoadJson(f"{Storage.SettingsDirectory}{channel.guild.id}.json")
      if not file:
        file["Help"] = {}
      
      for page in self.paginator.pages:
        embed = discord.Embed(title="Help", description=page)
        
        if not message:
          message = await channel.send(embed=embed)
          file["Help"]["All_Commands_Message"] = page
         
        await message.edit(embed=embed)
      
      if message:
        file["Help"]["Message"] = message.id
        file["Help"]["Channel"] = message.channel.id
        file["Help"]["Index"] = -1

        await message.add_reaction("⏮️")
        await message.add_reaction("⏭️")
      
      Utils.DumpJson(f"{Storage.SettingsDirectory}{message.guild.id}.json", file)
    elif message:
      file = Utils.LoadJson(f"{Storage.SettingsDirectory}{message.guild.id}.json")
      if file:
        page = file["Help"]["All_Commands_Message"]
        embed = discord.Embed(title="Help", description=page)
        await message.edit(embed=embed)
  
    self.paginator.clear()
          
  async def send_bot_help(self, mapping):
    sorted = await super().filter_commands(Storage.Client.commands, sort=True)
    sorted = itertools.groupby(sorted)

    destination = self.get_destination()
    Storage.help_commands[destination.guild.id] = []
    for command, category in sorted:
      Storage.help_commands[destination.guild.id].append(command)

    await super().send_bot_help(mapping)
  
  async def send_cog_help(self, cog):
    await super().send_cog_help(cog)
    
  async def send_group_help(self, group):
    await super().send_group_help(group)
    
  async def send_next_help(self, channel, message, allCommands=False, command = None):
    if not allCommands:
        self.add_command_formatting(command)
        self.paginator.close_page()
    
    await self.send_pages(channel, message, allCommands)

  async def send_command_help(self, command):
    self.add_command_formatting(command)
    self.paginator.close_page()
    await self.send_pages()

  async def reaction(self, client, payload):
    file = Utils.LoadJson(f"Settings/{payload.guild_id}.json")
    if not file:
      return

    if payload.user_id == client.user.id or payload.message_id != file["Help"]["Message"]:
      return

    channel = client.get_channel(file["Help"]["Channel"])
    message = await channel.fetch_message(file["Help"]["Message"])

    commands = Storage.help_commands[message.guild.id]
    index = file["Help"]["Index"]

    if payload.emoji.name == "⏭️":
        index += 1
    if payload.emoji.name == "⏮️":
        index -= 1

    if index >= len(commands):
        index = 0
    
    if index < 0:
        index = len(commands) - 1

    await message.remove_reaction("⏭️", client.get_user(payload.user_id))
    await message.remove_reaction("⏮️", client.get_user(payload.user_id))

    file["Help"]["Index"] = index

    Utils.DumpJson(f"{Storage.SettingsDirectory}{payload.guild_id}.json", file)
    
    all = not (index < len(commands) - 1 and index >= 0)
    command = None
    if (not all):
      command=commands[index]
    await self.send_next_help(channel=channel, message=message, allCommands=all, command=command)

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