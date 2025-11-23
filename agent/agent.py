from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType
from tools.playlist_tools import  delete_playlist, smart_create_playlist
from prompts.prompts import get_spotify_system_prompt
from langchain.memory import ConversationBufferMemory

def get_agent():
    llm = ChatOllama(
        model="llama3",
        temperature=0.5
    )

    tools = [smart_create_playlist,delete_playlist]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    system_prompt = get_spotify_system_prompt()

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        system_message=system_prompt
    )

    return agent