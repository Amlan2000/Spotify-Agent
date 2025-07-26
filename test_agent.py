from agent.agent import get_agent

if __name__ == "__main__":
    agent = get_agent()
    response = agent.invoke("Create a playlist with all my liked songs from Papon.")
    print("Agent Response:", response)