import streamlit as st
import PyPDF2
import json
import requests

# ------------------------------
# API Key
# ------------------------------
GROQ_API_KEY = "your_api_key"

# ------------------------------
# CUSTOM CSS FOR COLORS & CHAT BUBBLES
# ------------------------------
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background-color: #e6f2ff;  /* Light blue */
        color: #000000;
    }

    /* Sidebar background */
    .css-1d391kg {  
        background-color: #ffffff;  /* White */
    }

    /* Chat bubbles */
    .user-msg {
        background-color: #ffffff;
        color: #000000;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        text-align: right;
    }

    .ai-msg {
        background-color: #cce0ff;
        color: #000000;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        text-align: left;
    }

    /* Scrollable chat container */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
    }

    /* Make the text_input label black */
    div[data-baseweb="input"] > label {
        color: #000000 !important;
    }
    .stTextInput label {
        color: #000000 !important;
    }

    /* Make the 'Ask' button text white and add a dark background for visibility */
    .stButton form_submit_button {
        color: #ffffff !important;
        background-color: #000000 !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------
# PDF FUNCTIONS
# ------------------------------
def extract_text(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


def get_top_chunks(question, chunks, k=6):
    q_words = set(question.lower().split())
    scored = []

    for chunk in chunks:
        c_words = set(chunk.lower().split())
        score = len(q_words & c_words)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(reverse=True)
    return [chunk for _, chunk in scored[:k]]


def get_answer(question, chunks):
    top_chunks = get_top_chunks(question, chunks, k=6)

    if not top_chunks:
        return (
            "⚠️ I couldn’t find relevant information in the uploaded document.\n\n"
            "Try rephrasing your question or asking something more specific."
        )

    context = "\n\n---\n\n".join(top_chunks)

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a document-based assistant.\n"
                    "Answer ONLY using the provided context.\n"
                    "If the answer is not present, say:\n"
                    "'The uploaded document does not contain this information.'\n"
                    "Do NOT guess or use outside knowledge."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )

    data = response.json()

    if "error" in data:
        return f"❌ Groq Error: {data['error'].get('message', 'Unknown error')}"

    answer = data["choices"][0]["message"]["content"]
    return answer


# ------------------------------
# STREAMLIT UI
# ------------------------------
st.set_page_config(page_title="PDF Chat Assistant", layout="wide")
st.title("📚 PDF Chat Assistant")

st.sidebar.title("📄 PDF Settings")
uploaded_file = st.sidebar.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

st.sidebar.info(
    "ℹ️ Answers are generated strictly from the uploaded PDF.\n"
    "Results depend on how the question is phrased."
)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if uploaded_file:
    text = extract_text(uploaded_file)
    chunks = chunk_text(text)

    st.write("---")

    # Display chat history with bubbles
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f'<div class="user-msg">🧑‍💻 {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">🤖 {msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")

    # Input form at bottom
    with st.form("chat_form", clear_on_submit=True):
        user_question = st.text_input("Ask something about the uploaded PDF:")
        submitted = st.form_submit_button("Ask")

    if submitted and user_question.strip():
        with st.spinner("Thinking..."):
            answer = get_answer(user_question, chunks)

        # Append to history
        st.session_state.chat_history.append(("You", user_question))
        st.session_state.chat_history.append(("AI", answer))

        st.rerun()