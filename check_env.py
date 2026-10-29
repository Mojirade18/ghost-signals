# check_env.py - shows what .env contains WITHOUT revealing the key.
import os
from dotenv import load_dotenv

load_dotenv(".env")
key = os.getenv("AI_API_KEY") or ""

print("URL   :", os.getenv("AI_BASE_URL"))
print("MODEL :", os.getenv("AI_MODEL"))
print("KEY starts with:", key[:4])
print("KEY length     :", len(key))
print("has space/quote:", any(c in key for c in [" ", '"', "'"]))