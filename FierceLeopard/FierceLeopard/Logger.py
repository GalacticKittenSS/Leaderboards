from datetime import datetime

class Logger:
  Warnings = []

  def Info(self, text):
    now = datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [FierceLeopard] [INFO   ] {text}")

  def Warn(self, text):
    now = datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [FierceLeopard] [WARNING] {text}")
    self.Warnings.append(text)

  def Error(self, text):
    now = datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [FierceLeopard] [ERROR  ] {text}")

  def GetWarnings(self):
    result = f"__Found {len(self.Warnings)} Warnings:__"
    
    for w in self.Warnings:
      result = result + "\n" + w

    self.Warnings.clear()
    return result
