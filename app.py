import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GROQ_API_KEY environment variable.")

client = Groq(api_key=api_key)
#The "system" role is used to set context, behavior, or instructions for the conversation.
conversation_history = [
    {
        "role": "system",
        "content": "You are an english teacher. Correct mistakes in given sentences."
    }
]

def talk(query):
    # This sends the entire conversation history, which includes the initial context 
    # from the system role, any previous user messages, and the bot’s responses.
    conversation_history.append({
        "role": "user", 
        "content": query
    })
    #This sends the entire conversation history, which includes the initial context 
    #from the system role, any previous user messages, and the bot’s responses.
    chat_completion = client.chat.completions.create(
        
        messages=conversation_history,
        model="llama-3.1-8b-instant",
    )
    bot_response = chat_completion.choices[0].message.content
     # The model knows that this message comes from the assistant, so it uses it to keep
     # clarity in the conversation n ensure it’s responding properly to the user’s inputs.
    conversation_history.append({
        "role": "assistant", 
        "content": bot_response
    })

    print("Bot: ", bot_response)


while True:
    query = input("USER_: ")
    if query.lower() == "exit":
        break
    else:
        talk(query)