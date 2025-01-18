import os
import streamlit as st
from groq import Groq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader

# Set up the API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GROQ_API_KEY environment variable.")

client = Groq(api_key=api_key)

# Load and index documents
def load_and_index_documents():
    loader = PyPDFDirectoryLoader("./documents")  # Path to your document directory
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = text_splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = [
        {
            "role": "system",
            "content": "You are an English teacher. Correct mistakes in given sentences."
        }
    ]

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = load_and_index_documents()

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# Function to retrieve relevant context
def retrieve_context(query):
    retriever = st.session_state.vectorstore.as_retriever()
    relevant_docs = retriever.get_relevant_documents(query)
    return relevant_docs

# Chatbot function
def talk(query):
    relevant_docs = retrieve_context(query)
    context = "\n".join([doc.page_content for doc in relevant_docs])

    st.session_state["conversation_history"].append({
        "role": "user", 
        "content": query
    })
    prompt_with_context = f"""
You are an English teacher. Use the following context to help correct mistakes in the sentence:
{context}

User: {query}
"""
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an English teacher."},
            {"role": "user", "content": prompt_with_context},
        ],
        model="llama-3.1-8b-instant",
    )
    bot_response = chat_completion.choices[0].message.content

    st.session_state["conversation_history"].append({
        "role": "assistant", 
        "content": bot_response
    })
    return bot_response

# Streamlit UI
st.set_page_config(page_title="English Teacher Chatbot with RAG", layout="wide")
st.title("📝 English Teacher Chatbot with RAG")

# Sidebar for instructions and settings
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat History"):
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

# User input
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

        # Clear the input box by resetting `st.session_state["user_input"]`
        try:
            st.session_state["user_input"] = ""  # Reset input field

            # Display retrieved context
            st.subheader("Retrieved Context")
            relevant_docs = retrieve_context(user_input)
            for i, doc in enumerate(relevant_docs):
                st.write(f"**Document {i+1}:**")
                st.write(doc.page_content)
                st.write("---")
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
st.markdown("*Built with Streamlit, LangChain, and Groq API.*")
