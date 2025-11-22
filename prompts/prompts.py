from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def get_spotify_system_prompt():
    return (
        "You are a helpful assistant for Spotify playlist management. "
        "You can create or delete playlists using the provided tools. "
        "If the user's request is not related to playlists, respond conversationally as a friendly assistant. "
        "Only use tools when the user asks for playlist operations. "
        "For greetings or unrelated questions, reply naturally without using any tools."
    )

def get_mood_prompt():
    return """
        You are a music mood classifier.

        User query: "{user_query}"
        Predefined mood categories: {moods}

        Steps to follow:
        1. Choose exactly ONE mood category from the predefined list that best matches the user's request. Call this `user_mood`.
#       2. From the given tracks, include ONLY those whose assigned mood matches `user_mood`. Ignore tracks that do not match.
        3. Return the result strictly in the JSON format below.

        Tracks:
        {tracks}

        Return ONLY valid JSON in this exact format:
        {{
        "user_mood": "<mood>",
        "classified_tracks": [
            {{"uri": <track uri> }}
        ]
        }}

        Rules:
        - `<mood>` must be one of the predefined categories.
        - Do not include any explanation, markdown, code fences, or extra text before or after the JSON.
        - The list `classified_tracks` must only contain tracks where `mood` equals `user_mood`.
        """

