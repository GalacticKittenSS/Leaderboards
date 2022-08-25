import discord
from discord.ext import commands

import os
import json
import itertools

import Storage

class HelpView(discord.ui.View):
  def __init__(self, custom_help, command_list, page):
    self.HelpClass = custom_help
    self.Commands = command_list
    self.OriginalPage = page
    self.Index = -1
    super().__init__()
    
  async def UpdatePage(self, interaction):
    if interaction.user.id == Storage.Client.user.id:
      return

    if self.Index >= len(self.Commands):
      self.Index = -1
    
    if self.Index < -1:
      self.Index = len(self.Commands) - 1
    
    page = self.OriginalPage
    title = "Help"
    if self.Index < len(self.Commands) and self.Index >= 0:
      page = self.HelpClass.get_command_page(
        channel=interaction.channel, message=interaction.message, 
        command=self.Commands[self.Index]
      )
      title = self.Commands[self.Index].name
    
    embed = discord.Embed(title=title, description=page)
    await interaction.response.edit_message(embed=embed)
    
  @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, emoji="⏮️")
  async def Previous(self, interaction, button):
    self.Index -= 1
    await self.UpdatePage(interaction)
  
  @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, emoji="⏭️")
  async def Next(self, interaction, button):
    self.Index += 1
    await self.UpdatePage(interaction)

class Help(commands.DefaultHelpCommand):
  async def send_pages(self):
    command_list = await self.filter_commands(Storage.Client.commands, sort=True)
    
    destination = self.get_destination()
    for page in self.paginator.pages:
      embed = discord.Embed(title="Help", description=page)
      message = await destination.send(content="Showing Help...", embed=embed, view=HelpView(self, command_list, page))
      
    self.paginator.clear()
  
  def get_command_signature(self, command):
    alias = super().get_command_signature(command)
    return '%s %s' % (alias, command.signature)

  def get_command_page(self, channel, message, command=None):
    self.add_command_formatting(command)
    self.paginator.close_page()
    
    page = self.paginator.pages[0]

    self.paginator.clear()
    return page