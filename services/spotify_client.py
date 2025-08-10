import requests
from services.auth import get_access_token


class SpotifyClient:
    
    def __init__(self):
        self.base="https://api.spotify.com/v1"
        self.access_token=get_access_token()

    def headers(self):
        return {
            "Authorization":f"Bearer {self.access_token}",
            "Content-Type":"application/json",
        }
    
    def get_liked_songs(self,limit=50,max_pages=1):
        url = f"{self.base}/me/tracks?limit={limit}"
        songs=[]

        for _ in range(max_pages):     
            res=requests.get(url,headers=self.headers())
            res.raise_for_status()
            data=res.json()
            for item in data["items"]:
                track= item["track"]
                songs.append(
                    {
                        "id":track["id"],
                        "uri":track["uri"],
                        "name":track["name"],
                        "artists":[a["name"] for a in track["artists"]],
                        "primary_artist":track["artists"][0]["name"],

                    }
                )
        
            url = data.get("next")
            if not url:
                break
        
        return songs

