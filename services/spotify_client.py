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
    


    def get_devices(self):
        url = f"{self.base}/me/player/devices"
        r = requests.get(url, headers=self.headers())
        r.raise_for_status()
        return r.json().get("devices", [])

    def get_preferred_device_id(self):
        devices = self.get_devices()
        if not devices:
            return None
        # prefer active
        for d in devices:
            if d.get("is_active"):
                return d.get("id")
        # fallback default
        return devices[0].get("id")

    def start_playback(self, playlist_uri=None, uris=None, device_id=None, position_ms=None):
        """
        Start or resume playback on a device.
        Args:
          playlist_uri: e.g. "spotify:playlist:{playlist_id}"
          uris: list of track URIs
          device_id: optional
          position_ms: optional
        """
        url = f"{self.base}/me/player/play"
        if device_id:
            url += f"?device_id={device_id}"
        payload = {}
        if playlist_uri:
            payload["context_uri"] = playlist_uri
        elif uris:
            payload["uris"] = uris
        if position_ms is not None:
            payload["position_ms"] = position_ms

        r = requests.put(url, headers=self.headers(), json=payload)
        r.raise_for_status()
        return r.status_code

    def transfer_playback(self, device_id: str, play: bool = True):
        url = f"{self.base}/me/player"
        payload = {
            "device_ids": [device_id],
            "play": play
        }

        r = requests.put(url, headers=self.headers(), json=payload)

        if r.status_code not in [200, 202, 204]:
            raise Exception(f"Error transferring playback: {r.status_code}, {r.text}")

        return "Playback transferred successfully"
