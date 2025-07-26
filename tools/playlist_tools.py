from langchain.tools import tool
from services.spotify_client import SpotifyClient
import requests
import json


sp=SpotifyClient()

@tool("create_playlist_by_artist")
def create_playlist_by_artist(artist_name:str) -> str:
    """
    Creates a new Spotify playlist from liked songs of a specefic artist.
    
    Args:
    artist_name: Name of the artist to filter liked songs

    Returns:
    Returns the playlist name.

    """

    try:
        liked_songs = sp.get_liked_songs()
        filtered = [song for song in liked_songs if artist_name.lower() in song["primary_artist"].lower()]
        if not filtered:
            return f"No songs found for artist: {artist_name}"
        
        playlist_name = f"{artist_name} favourites"

        playlist_id = create_playlist(playlist_name)
        add_tracks_to_playlist(playlist_id,[song["uri"] for song in filtered])

        return f"Playlist '{playlist_name}' created with {len(filtered)} songs."
    
    except Exception as e:
        return f"Error creating playlist by artist {artist_name}: {str(e)}"


@tool("create_playlist_by_genre")
def create_playlist_by_genre(genre_name:str) -> str:
    """
    Creates a new Spotify playlist from liked songs of a specefic genere.

    Args:
    genre_name: Name of the genre to filter liked songs

    Returns:
    Returns the playlist name.

    """
    try:
        liked_songs = sp.get_liked_songs()
        filtered=[]

        for song in liked_songs:
            # Use Spotify track endpoint to get genre (requires artist info)
            song_genre = fetch_artist_genre(song["artists"][0])
            if genre_name.lower() in song_genre.lower():
                filtered.append(song)
        
        if not filtered:
            return f"No Songs found for genre: {genre_name}"
        
        playlist_name = f"{genre_name} Vibes"
        playlist_id = create_playlist(playlist_name)
        add_tracks_to_playlist(playlist_id,[song["uri"] for song in filtered])

        return f"Playlist '{playlist_name}' created with {len(filtered)} songs."
    except Exception as e:
        return f"Error creating playlist by genre {genre_name}: {str(e)}"



@tool("delete_playlist")
def delete_playlist(playlist_name:str)->str:
    """
    Deletes a playlist by name (only from the authenticated account).

    Args:
    playlist_name: Name of the playlist to be deleted

    Returns:
    Returns the message after playlist being deleted.
    """

    user_id = get_current_user_id()
    playlists = fetch_user_playlists(user_id)
    for playlist in playlists:
        if playlist_name.lower() == playlist["name"].lower():
            url = f"https://api.spotify.com/v1/playlists/{playlist['id']}/followers"
            r = requests.delete(url, headers=sp.headers())
            return f"Playlist '{playlist_name}' deleted."
        
    return f"No playlist found with name: {playlist_name}"







def create_playlist(name):
    user_id = get_current_user_id()
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    payload= json.dumps({"name":name, "public":False})
    r = requests.post(url,headers=sp.headers(),data=payload)
    r.raise_for_status()
    return r.json()["id"]

def add_tracks_to_playlist(playlist_id,uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    r = requests.post(url,headers = sp.headers(), data = json.dumps({"uris":uris}))
    r.raise_for_status()

def get_current_user_id():
    r=requests.get("https://api.spotify.com/v1/me",headers=sp.headers())
    r.raise_for_status()
    return r.json()["id"]

def fetch_user_playlists(user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    r = requests.get(url,headers=sp.headers())
    r.raise_for_status()
    return r.json()["items"]

def fetch_artist_genre(artist_name):
    search_url="https://api.spotify.com/v1/search"
    params = {"q":artist_name, "type":"artist","limit":1}
    r = requests.get(search_url,headers=sp.headers(),params=params)
    r.raise_for_status()
    artists = r.json().get("artists",{}).get("items",[])
    if artists and artists[0].get("genres"):
        return ",".join(artists[0]["genres"])
    return ""


