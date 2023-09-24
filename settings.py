from dotenv import dotenv_values
env = dotenv_values(".env")

def getenv(key):
    return env.get(key)