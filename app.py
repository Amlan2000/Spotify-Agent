from requests import session
import streamlit as st
from agent.agent import get_agent

st.set_page_config(page_title="Spotify Playlist Agent", page_icon="🎵")

st.title("🎵 Spotify Playlist Agent")
st.markdown("Ask me to create or delete playlists from your liked songs.")

# Get the agent
agent = get_agent()

#Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]

# User input
user_input = st.text_input("What would you like me to do?", placeholder="e.g. Create playlist of my liked pop songs")

# Handle submission
if user_input:
    with st.spinner("Thinking..."):
        try:
            # Add user message to chat history
            st.session_state.chat_history.append({"role":"user","content":user_input})
            # Run agent with chat_history
            response = agent.invoke(
                input=user_input,
                chat_history=st.session_state.chat_history
            ).get("output")
            # Add agent response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.success(response)
        except Exception as e:
            st.error(f"❌ Error: {e}")
