import discord
from discord.ext import commands

from dependencies import storage
import itertools

class CustomHelp(commands.DefaultHelpCommand):
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

    
  async def send_pages(self, channel = None, message = None, pages = False):
    try:
      destination = self.get_destination()

      for page in self.paginator.pages:
        storage.current_sorted_commands = page
        embed = discord.Embed(title="Help", description=page)
        message = await destination.send(embed=embed)
        storage.current_help_message.append(message)
        storage.current_help_commands.append(page)
        storage.current_help_index.append(-1)
      
        await message.add_reaction("⏮️")
        await message.add_reaction("⏭️")
    except:
      destination = storage.client.get_channel(channel.id)
      if pages:
        page = storage.current_sorted_commands
        embed = discord.Embed(title="Help", description=page)
        await message.edit(embed=embed)

      for page in self.paginator.pages:
        embed = discord.Embed(title="Help", description=page)
        await message.edit(embed=embed)
          
  async def send_bot_help(self, mapping):
    sorted = await super().filter_commands(storage.client.commands, sort=True)
    sorted = itertools.groupby(sorted)

    storage.current_help_commands = []

    for command, category in sorted:
      storage.current_help_commands.append(command)
    await super().send_bot_help(mapping)
  
  async def send_cog_help(self, cog):
    await super().send_cog_help(cog)
    
  async def send_group_help(self, group):
    await super().send_group_help(group)
    
  async def send_next_help(self, channel, message, page=False, command = None):
    if page:
      await self.send_pages(channel=channel, message=message, pages=True)
    else:
      self.add_command_formatting(command)
      self.paginator.close_page()
      await self.send_pages(channel=channel, message=message)


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