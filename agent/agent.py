from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType
from tools.playlist_tools import create_playlist_by_artist, create_playlist_by_genre,create_playlist_by_mood, delete_playlist
from prompts.prompts import get_spotify_system_prompt
from langchain.memory import ConversationBufferMemory

def get_agent():
    llm = ChatOllama(
        model="llama3",
        temperature=0.5
    )

    tools = [create_playlist_by_artist, create_playlist_by_genre,create_playlist_by_mood, delete_playlist]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    system_prompt = get_spotify_system_prompt()

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        system_message=system_prompt
    )

    return agent