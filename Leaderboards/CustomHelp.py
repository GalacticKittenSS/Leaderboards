import discord
from discord.ext import commands

import os
import json
import itertools

import Storage

class HelpView(discord.ui.View):
  def __init__(self, custom_help, allCommands):
    self.HelpClass = custom_help
    self.Index = -1
    self.Commands = custom_help.next_commands
    self.AllCommands = allCommands
    super().__init__()
    
  async def ChangeIndex(self, interaction):
    if interaction.user.id == Storage.Client.user.id:
      return

    if self.Index >= len(self.Commands):
      self.Index = 0
    
    if self.Index < 0:
      self.Index = len(self.Commands) - 1
    
    all = None
    if not (self.Index < len(self.Commands) - 1 and self.Index >= 0):
      all = self.AllCommands
    
    command = None
    if (not all):
      command=self.Commands[self.Index]
    
    await self.HelpClass.send_next_help(channel=interaction.channel, message=interaction.message, allCommands=all, command=command)

  @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, emoji="⏮️")
  async def Previous(self, interaction, button):
    self.Index -= 1
    await self.ChangeIndex(interaction)
  
  @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, emoji="⏭️")
  async def Next(self, interaction, button):
    self.Index += 1
    await self.ChangeIndex(interaction)

class Help(commands.DefaultHelpCommand):
  next_commands = []

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

  async def send_pages(self, channel = None, message = None, allCommands=None):
    if not allCommands:
      if not channel:
        channel = self.get_destination()

      for page in self.paginator.pages:
        embed = discord.Embed(title="Help", description=page)
        
        if not message:
          message = await channel.send(embed=embed, view=HelpView(self, page))
      
        await message.edit(embed=embed)
      
    elif message:
      embed = discord.Embed(title="Help", description=allCommands)
      await message.edit(embed=embed)
  
    self.paginator.clear()
          
  async def send_bot_help(self, mapping):
    sorted = await super().filter_commands(Storage.Client.commands, sort=True)
    sorted = itertools.groupby(sorted)

    self.next_commands = []
    for command, category in sorted:
      self.next_commands.append(command)

    await super().send_bot_help(mapping)
  
  async def send_cog_help(self, cog):
    await super().send_cog_help(cog)
    
  async def send_group_help(self, group):
    await super().send_group_help(group)
    
  async def send_next_help(self, channel, message, allCommands=None, command=None):
    if not allCommands:
        self.add_command_formatting(command)
        self.paginator.close_page()
    
    await self.send_pages(channel, message, allCommands)

  async def send_command_help(self, command):
    self.add_command_formatting(command)
    self.paginator.close_page()
    await self.send_pages()

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