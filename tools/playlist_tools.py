from langchain.tools import tool
from streamlit import user
from services.spotify_client import SpotifyClient
import requests

from services.tool_services import add_tracks_to_playlist, create_playlist, fetch_artist_genre, fetch_user_playlists, get_audio_moods, get_current_user_id


sp=SpotifyClient()

@tool("create_playlist_by_artist")
def create_playlist_by_artist(artist_name:str) -> str:
    """
    Creates a new Spotify playlist from liked songs of a specific artist.
    
    Args:
    artist_name: Name of the artist to filter liked songs

    Returns:
    Returns the playlist name.

    """

    try:
        liked_songs = sp.get_liked_songs()
        if not liked_songs:
            return "No liked songs found"
        
        filtered = [song for song in liked_songs if artist_name.lower() in song["primary_artist"].lower()]
        if not filtered:
            return f"No songs found for artist: {artist_name}"
        
        playlist_name = f"{artist_name} favourites"

        playlist_id = create_playlist(sp,playlist_name)
        add_tracks_to_playlist(sp,playlist_id,[song["uri"] for song in filtered])

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
        if not liked_songs:
            return "No liked songs found"
        
        filtered=[]

        for song in liked_songs:
            # Use Spotify track endpoint to get genre (requires artist info)
            song_genre = fetch_artist_genre(sp,song["primary_artist"])
            if genre_name.lower() in song_genre.lower():
                filtered.append(song)
        
        if not filtered:
            return f"No Songs found for genre: {genre_name}"
        
        playlist_name = f"{genre_name} Vibes"
        playlist_id = create_playlist(sp,playlist_name)
        add_tracks_to_playlist(sp,playlist_id,[song["uri"] for song in filtered])

        return f"Playlist '{playlist_name}' created with {len(filtered)} songs."
    except Exception as e:
        return f"Error creating playlist by genre {genre_name}: {str(e)}"


@tool("create_playlist_by_mood")
def create_playlist_by_mood(user_query:str):
    """
    Creates a new spotify playlist from liked songs based on mood.

    Args:
    user_query: mood to be identified from the user_query 

    Returns:
    Returns the message after playlist is being created.
    
    """

    try:

        
        liked_songs = sp.get_liked_songs()
        
        if not liked_songs:
            return "No liked songs found"
        
        # Get track name and artist
        tracks_info = [
        {
            'id': song.get('id'),
            'name': song.get('name'),
            'primary_artist': song.get('primary_artist'),
            'uri': song.get('uri') or f"spotify:track:{song.get('id')}"
        }
        for song in liked_songs
        if song.get('id')
        ]


        # Fetching audio id's of the songs which match the user mood
        track_URIs , user_mood = get_audio_moods(user_query, tracks_info)    
        
        if not  track_URIs:
            return f"No Songs found for mood: {user_mood}"
        
        playlist_name= f"This is my {user_mood} playlist"
        playlist_id = create_playlist(sp,playlist_name)

        track_URIs = [f"spotify:track:{tid}" for tid in track_URIs]
        
        add_tracks_to_playlist(sp,playlist_id,track_URIs)
    
        return f"Playlist '{playlist_name}' created with {len( track_URIs)} songs."
    except Exception as e:
        return f"Error creating playlist by mood {user_mood}: {str(e)}"
    



@tool("delete_playlist")
def delete_playlist(playlist_name:str)->str:
    """
    Deletes a playlist by name (only from the authenticated account).

    Args:
    playlist_name: Name of the playlist to be deleted

    Returns:
    Returns the message after playlist being deleted.
    """

    user_id = get_current_user_id(sp)
    playlists = fetch_user_playlists(sp,user_id)
    for playlist in playlists:
        if playlist_name.lower() == playlist["name"].lower():
            url = f"https://api.spotify.com/v1/playlists/{playlist['id']}/followers"
            r = requests.delete(url, headers=sp.headers())
            return f"Playlist '{playlist_name}' deleted."
        
    return f"No playlist found with name: {playlist_name}"


@tool("smart_create_playlist")
def smart_create_playlist( artist: str = None, genre: str = None, mood: str = None, count: int = None):
    """
    Create a playlist intelligently based on user intent.
    
    Args:
        artist: Filter by artist name (optional)
        genre: Filter by genre (optional)
        mood: Filter by mood detected from audio (optional)
        count: Max number of tracks in the playlist (optional)

     Returns:
        str: Playlist ID on success, error message on failure
    """

    try:
        liked_songs = sp.get_liked_songs()
        if not liked_songs:
            return "No liked songs found."
        
        if not artist and not genre and not mood:
            return "Request atleast needs to have an artist name or genre or mood to create a playlist."

        filtered = liked_songs

        # Artist filter
        if artist:
            artist_filtered = [
                song for song in liked_songs 
                if artist.lower() in song["primary_artist"].lower()
            ]
            filtered.extend(artist_filtered)

        # Genre filter
        if genre:
            genre_filtered = []
            for song in liked_songs:
                song_genre = fetch_artist_genre(sp, song["primary_artist"])
                if genre.lower() in song_genre.lower():
                    genre_filtered.append(song)
            filtered.extend(genre_filtered)

        # Mood filter
        if mood:
            track_uris, user_mood = get_audio_moods(mood, liked_songs)
            if track_uris:
                # Ensure all URIs have proper format
                mood_filtered = []
                for track_uri in track_uris:
                    if not track_uri.startswith("spotify:track:"):
                        track_uri = f"spotify:track:{track_uri}"
                    mood_filtered.append({"uri": track_uri})
                filtered.extend(mood_filtered)

        # Remove duplicates while preserving order
        seen_uris = set()
        unique_filtered = []
        for song in filtered:
            uri = song.get("uri") if isinstance(song, dict) else song.get("uri")
            if uri and uri not in seen_uris:
                seen_uris.add(uri)
                unique_filtered.append(song)
        
        filtered = unique_filtered

    
        if count:
            filtered = filtered[:count]

        if not filtered:
            return "No tracks matched your request."

        playlist_name = f"My {artist or ''} {genre or ''} {mood or ''} Playlist".strip()
        playlist_id = create_playlist(sp, playlist_name)

        uris = [
            song.get("uri") or song 
            for song in filtered
        ]

        print("uris: ", uris)
        add_tracks_to_playlist(sp, playlist_id, uris)

        return playlist_id

    except Exception as e:
        return f"Error: {str(e)}"
    


@tool("play_playlist")
def play_playlist(playlist_id: str):
    """
    Play a Spotify playlist on the user's active device.
    
    Args:
        playlist_id: The Spotify playlist ID (just the ID, not the full URI)
    
    Returns:
        str: Success or error message
    """
    try:
        # Remove any URI prefix if present
        if playlist_id.startswith("spotify:playlist:"):
            playlist_id = playlist_id.split(":")[-1]
        
        device_id = sp.get_preferred_device_id()
        
        if not device_id:
            return "ERROR: No active Spotify device found. Please open Spotify on a device first."
        
        sp.transfer_playback(device_id=device_id, play=True)
        sp.start_playback(playlist_uri=f"spotify:playlist:{playlist_id}", device_id=device_id)
        
        return f"✓ Now playing playlist on your Spotify device"
        
    except Exception as e:
        return f"ERROR: Could not play playlist - {str(e)}"
       
    