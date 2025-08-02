from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def get_spotify_system_prompt():
    return (
        "You are a helpful assistant for Spotify playlist management. "
        "You can create or delete playlists using the provided tools. "
        "If the user's request is not related to playlists, respond conversationally as a friendly assistant. "
        "Only use tools when the user asks for playlist operations. "
        "For greetings or unrelated questions, reply naturally without using any tools."
    )