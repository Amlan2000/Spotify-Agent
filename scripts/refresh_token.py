import base64
import os
import random
import string
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPES= os.getenv("SCOPES")


def random_string(n=16):
    """Generate a random string of fixed length."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

state = random_string()

auth_url=("https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
    {
        "response_type":"code",
        "client_id":CLIENT_ID,
        "scope":SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state":state,
    }
))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        code = params.get("code",[None])[0]
        if not code:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed")
            return
        
        token_url = "https://accounts.spotify.com/api/token"
        auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        data = {
            "grant_type":"authorization_code",
            "code":code,
            "redirect_uri": REDIRECT_URI,
        }

        headers = {"Authorization":f"Basic {auth_header}"}
        r = requests.post(token_url,data=data,headers=headers)
        r.raise_for_status()
        tokens = r.json()
        refresh_token = tokens["refresh_token"]

        self.send_response(200)
        self.end_headers()
        msg = f"Your refresh token is : \n \n {refresh_token}\n\n Copy this into your .env as SPOTIFY_REFRESH_TOKEN"
        self.wfile.write(msg.encode())
        print(msg)


def main():
    print("Open this URL to authorize:")
    print(auth_url)
    server= HTTPServer(("127.0.0.1",8080),Handler)
    server.handle_request()


if __name__=="__main__":
    main()