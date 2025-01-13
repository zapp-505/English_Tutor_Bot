import os
import streamlit as st
from groq import Groq

# Set up the API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GROQ_API_KEY environment variable.")

client = Groq(api_key=api_key)

# Initialize conversation history
conversation_history = [
    {
        "role": "system",
        "content": "You are an English teacher. Correct mistakes in given sentences."
    }
]

def talk(query):
    # Append user query to the conversation history
    conversation_history.append({
        "role": "user", 
        "content": query
    })

    # Get the chatbot response
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="llama-3.1-8b-instant",
    )
    bot_response = chat_completion.choices[0].message.content

    # Append assistant's response to the conversation history
    conversation_history.append({
        "role": "assistant", 
        "content": bot_response
    })

    return bot_response

# Streamlit interface
st.title("English Teacher Chatbot")

# Text input for user query
user_input = st.text_input("Ask a question:")

# Display the conversation
if user_input:
    response = talk(user_input)
    st.write(f"**Bot:** {response}")


