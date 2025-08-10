
import json
import requests
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from streamlit import user
import traceback
import sys

from prompts.prompts import get_mood_prompt





def create_playlist(sp,name):
    user_id = get_current_user_id(sp)
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    payload= json.dumps({"name":name, "public":False})
    r = requests.post(url,headers=sp.headers(),data=payload)
    r.raise_for_status()
    return r.json()["id"]

def add_tracks_to_playlist(sp,playlist_id,uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    r = requests.post(url, headers=sp.headers(), json={"uris": uris})
    r.raise_for_status()

def get_current_user_id(sp):
    r=requests.get("https://api.spotify.com/v1/me",headers=sp.headers())
    r.raise_for_status()
    return r.json()["id"]

def fetch_user_playlists(sp,user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    r = requests.get(url,headers=sp.headers())
    r.raise_for_status()
    return r.json()["items"]

def fetch_artist_genre(sp,artist_name):
    search_url="https://api.spotify.com/v1/search"
    params = {"q":artist_name, "type":"artist","limit":1}
    r = requests.get(search_url,headers=sp.headers(),params=params)
    r.raise_for_status()
    artists = r.json().get("artists",{}).get("items",[])
    if artists and artists[0].get("genres"):
        return ",".join(artists[0]["genres"])
    return ""


def get_audio_moods(user_query, tracks_info):
    llm = ChatOllama(model="llama3", temperature=0)

    custom_moods = {
        'peaceful', 'melancholic', 'nostalgic', 'angry', 'confident', 'dreamy', 
        'workout', 'study', 'driving', 'rainy', 'sunny', 'midnight', 'morning', 
        'party', 'intimate', 'heartbreak', 'celebration', 'happy'
    }

    # track_descriptions = "\n".join(
    #     [f"{t['name']} by {t['primary_artist']}" for t in tracks_info]
    # )

    try:
        prompt_template = PromptTemplate(
            input_variables=["user_query", "moods", "tracks"],
            template=get_mood_prompt()
        )

        prompt = prompt_template.format(
            user_query=user_query,
            moods=", ".join(custom_moods),
            tracks=tracks_info
        )

        print("\n Tracks length: ", len(tracks_info))

        response = llm.invoke(prompt)
        print("Raw response:", response)

        result_text = response.content if hasattr(response, "content") else response

        classification = json.loads(result_text)
        print("\nClassification:", classification)

        user_mood = classification.get("user_mood")
        classified_tracks = classification.get("classified_tracks")

        track_URIs = [t["uri"] for t in classified_tracks]

        print(f"\n user_mood: {user_mood}")
        print(f"track_URIs: {track_URIs}")

        return track_URIs, user_mood

    except Exception as e:
        print(f"\n❌ {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)  # Ensures it stops so you see the error in terminal