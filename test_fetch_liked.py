from services.spotify_client import SpotifyClient

if __name__ == "__main__":
    sp = SpotifyClient()
    songs = sp.get_liked_songs()
    print(f"Fetched {len(songs)} liked songs")
    print("First 3:")
    for s in songs[:3]:
        print(s["name"], "-", s["primary_artist"])
