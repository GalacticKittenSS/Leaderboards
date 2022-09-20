import logging

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
Warnings = []

def Setup(level, fmt : str, datefmt : str = "%Y-%m-%d %H:%M:%S", filename : str = None):
  formatter = logging.Formatter(fmt, datefmt)

  logger = logging.getLogger()
  logger.setLevel(level)

  if filename:
    fileHandler = logging.FileHandler(filename)
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(level)
    logger.addHandler(fileHandler)

  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(formatter)
  consoleHandler.setLevel(level)
  logger.addHandler(consoleHandler)

def Debug(text):
  logging.debug(text)

def Info(text):
  logging.info(text)

def Warn(text):
  logging.warning(text)
  Warnings.append(text)

def Error(text):
  logging.error(text)

def Critical(text):
  logging.critical(text)
  raise Exception(text)

def GetWarnings():
  result = f"__Found {len(Warnings)} Warnings:__"
  
  for w in Warnings:
    result = result + "\n" + w

  Warnings.clear()
  return result
