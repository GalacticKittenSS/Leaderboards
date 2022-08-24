from datetime import datetime

Warnings = []

def Info(text):
    now = datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [INFO   ] {text}")

def Warn(text):
    now = datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [WARNING] {text}")
    Warnings.append(text)

def Error(text):
    now = datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] [ERROR  ] {text}")

def GetWarnings():
    result = f"__Found {len(Warnings)} Warnings:__"
    
    for w in Warnings:
        result = result + "\n" + w

    Warnings.clear()
    return result
