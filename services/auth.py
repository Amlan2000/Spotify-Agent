import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN=os.getenv("SPOTIFY_REFRESH_TOKEN")

def get_access_token() -> str:
    token_url="https://accounts.spotify.com/api/token"
    auth_header= base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    data={
        "grant_type":"refresh_token",
        "refresh_token":REFRESH_TOKEN,
    }

    print("Token request data:", data)  # Debug print

    headers={"Authorization":f"Basic {auth_header}"}
    r=requests.post(token_url,data=data,headers=headers)
    print("Token response:", r.text)    # Debug print

    r.raise_for_status()
    return r.json()["access_token"]