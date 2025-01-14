import os
import streamlit as st
from groq import Groq

# Set up the API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GROQ_API_KEY environment variable.")

client = Groq(api_key=api_key)

# Initialize session state for conversation history and user input
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = [
        {
            "role": "system",
            "content": "You are an English teacher. Correct mistakes in given sentences."
        }
    ]

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# Chatbot function
def talk(query):
    st.session_state["conversation_history"].append({
        "role": "user", 
        "content": query
    })
    chat_completion = client.chat.completions.create(
        messages=st.session_state["conversation_history"],
        model="llama-3.1-8b-instant",
    )
    bot_response = chat_completion.choices[0].message.content
    st.session_state["conversation_history"].append({
        "role": "assistant", 
        "content": bot_response
    })
    return bot_response

# Streamlit UI
st.set_page_config(page_title="English Teacher Chatbot", layout="wide")
st.title("📝 English Teacher Chatbot")

# Sidebar for instructions and settings
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat History"):
        # Clear conversation history and reset to initial state
        st.session_state["conversation_history"] = [
            {
                "role": "system",
                "content": "You are an English teacher. Correct mistakes in given sentences."
            }
        ]
        st.session_state["user_input"] = ""  # Clear input box
        st.success("Chat history cleared!")

    st.markdown("### How to Use")
    st.markdown("1. Type your sentence in the input box.\n2. Press 'Send' to get corrections.\n3. View the conversation history below.")

# Main chat UI
user_input = st.text_area(
    "Your Message:", 
    value=st.session_state["user_input"], 
    placeholder="Type your sentence here...",
    key="user_input"
)

if st.button("Send"):
    if user_input.strip():  # Ensure input is not empty
        response = talk(user_input)
        st.write(f"Bot: {response}")
        try:
            st.session_state["user_input"] = ""  # Clear input box
            st.experimental_rerun()  # Rerun the app to update the conversation
        except Exception as e:
            print(f"dumb error: {e}")

    else:
        st.warning("Please type a message before sending!")

# Display conversation in a chat-bubble style
st.subheader("Conversation")
for msg in st.session_state["conversation_history"][1:]:  # Skip the "system" message
    if msg["role"] == "user":
        st.markdown(f"**🧑‍🎓 You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and Groq API.*")
