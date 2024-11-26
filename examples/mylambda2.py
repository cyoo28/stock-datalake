import os

def handler(event, contex):
    message = os.getenv("MESSAGE")
    print(message)
