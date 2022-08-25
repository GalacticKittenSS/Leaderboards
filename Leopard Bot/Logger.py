from datetime import datetime

def Info(text):
  now = datetime.now()
  print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [Leopard Bot] [INFO   ] {text}")

def Warn(text):
  now = datetime.now()
  print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [Leopard Bot] [WARNING] {text}")
    
def Error(text):
  now = datetime.now()
  print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [Leopard Bot] [ERROR  ] {text}")

def GetWarnings():
  result = f"__Found {len(Warnings)} Warnings:__"
  
  for w in Warnings:
    result = result + "\n" + w

  return result
