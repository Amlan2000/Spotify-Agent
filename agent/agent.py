from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType
from tools.playlist_tools import create_playlist_by_artist, create_playlist_by_genre, delete_playlist

def get_agent():
    llm = ChatOllama(
        model="llama3",
        temperature=0
    )

    tools = [create_playlist_by_artist, create_playlist_by_genre, delete_playlist]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent
