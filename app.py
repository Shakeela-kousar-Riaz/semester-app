import streamlit as st
import PyPDF2
import google.generativeai as genai
import re

# ====== CUSTOM STYLE AND BACKGROUND ======
def set_bg_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgYCf7zQFjCI8WO8Y5XFuGpes5GuCXbyIQEA&s");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }

        .block-container {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }

        h1, h2, h3, h4, h5, h6, p, div, span, label, textarea {
            color: black !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #0b1e35;
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        .stFileUploader > div:first-child,
        .stFileUploader div div {
            color: white !important;
        }

        button {
            color: white !important;
            font-weight: bold;
        }

        .stTextInput {
            width: 80%;
        }

        .centered-bottom {
            display: flex;
            justify-content: center;
            margin-top: 3rem;
        }

        /* Chat Bubbles */
        .chat-bubble-user {
            background-color: #1877f2;
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            margin: 10px auto 10px 0;
            text-align: left;
            white-space: pre-wrap;
        }

        .chat-bubble-ai {
            background-color: #f1f0f0;
            color: black;
            padding: 10px 15px;
            border-radius: 15px;
            width: 100%;
            margin: 10px 0 10px 0;
            text-align: left;
            white-space: pre-wrap;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stTextInput,
        section[data-testid="stSidebar"] .stFileUploader,
        section[data-testid="stSidebar"] .stSelectbox {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
import streamlit as st 
import PyPDF2
import google.generativeai as genai
import re

# ====== CUSTOM STYLE AND BACKGROUND ======
def set_bg_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgYCf7zQFjCI8WO8Y5XFuGpes5GuCXbyIQEA&s");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }

        .block-container {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }

        h1, h2, h3, h4, h5, h6, p, div, span, label, textarea {
            color: black !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #0b1e35;
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        .stFileUploader > div:first-child,
        .stFileUploader div div {
            color: white !important;
        }

        button {
            color: white !important;
            font-weight: bold;
        }

        .stTextInput {
            width: 80%;
        }

        .centered-bottom {
            display: flex;
            justify-content: center;
            margin-top: 3rem;
        }

        /* Chat Bubbles */
        .chat-bubble-user {
            background-color: #1877f2;
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            margin: 10px auto 10px 0;
            text-align: left;
            white-space: pre-wrap;
        }

        .chat-bubble-ai {
            background-color: #f1f0f0;
            color: black;
            padding: 10px 15px;
            border-radius: 15px;
            width: 100%;
            margin: 10px 0 10px 0;
            text-align: left;
            white-space: pre-wrap;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stTextInput,
        section[data-testid="stSidebar"] .stFileUploader,
        section[data-testid="stSidebar"] .stSelectbox {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_image()

# ====== TEXT EXTRACTION FUNCTION ======
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text.strip()

# ====== CLEANUP FUNCTION ======
def clean_response(text):
    cleaned = re.sub(r'\n{3,}', '\n\n', text)  # Collapse more than 2 newlines
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Collapse multiple spaces/tabs
    return cleaned.strip()

# ====== GEMINI HANDLERS ======
def generate_quiz(text, model):
    prompt = f"""
    From the following outline, generate 5 multiple-choice questions.
    Provide options (A to D) and mark the correct answer at the end of each question.

    Outline:
    {text}
    """
    response = model.generate_content(prompt)
    return clean_response(response.text)

def generate_assignment(text, model):
    prompt = f"""
    Based on the following semester outline, generate a detailed assignment prompt with title, objectives, and tasks.

    Outline:
    {text}
    """
    response = model.generate_content(prompt)
    return clean_response(response.text)

def ask_question(outline_text, user_query, model):
    prompt = f"Here is the semester outline:\n\n{outline_text}\n\nNow answer this user query: {user_query}"
    response = model.generate_content(prompt)
    return clean_response(response.text)

# ====== SIDEBAR UI ======
st.sidebar.title("🧭 Semester Controls")
api_key = st.sidebar.text_input("🔑 Enter your Gemini API Key", type="password")
uploaded_file = st.sidebar.file_uploader("📄 Upload Semester Outline (PDF only)", type=["pdf"])

st.sidebar.markdown("🚀 **Select Action(s)**")
ask_question_checked = st.sidebar.checkbox("Ask a Question")
generate_assignment_checked = st.sidebar.checkbox("Generate Assignment")
generate_quiz_checked = st.sidebar.checkbox("Generate Quiz")

# ====== MAIN DISPLAY ======
st.title("📘 Semester Assistant (Gemini AI)")
st.write("Interact with your uploaded semester outline using AI-powered Q&A, assignments, and quiz generation.")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    with st.spinner("🔍 Extracting text from uploaded file..."):
        extracted_text = extract_text_from_pdf(uploaded_file)

    st.success("✅ Outline processed!")

    st.markdown('<div class="centered-bottom">', unsafe_allow_html=True)
    query = st.text_input("✏️ Enter your input:")
    st.markdown('</div>', unsafe_allow_html=True)

    if query:
        with st.spinner("💬 Getting response from Gemini..."):
            if ask_question_checked:
                response = ask_question(extracted_text, query, model)
                st.session_state.conversation_history.insert(0, (f"[Ask a Question] {query}", response))

            if generate_assignment_checked:
                response = generate_assignment(extracted_text, model)
                st.session_state.conversation_history.insert(0, (f"[Generate Assignment] {query}", response))

            if generate_quiz_checked:
                response = generate_quiz(extracted_text, model)
                st.session_state.conversation_history.insert(0, (f"[Generate Quiz] {query}", response))

    if st.session_state.conversation_history:
        st.markdown("### 🗨️ Chat History")
        for user_input, ai_response in st.session_state.conversation_history:
            st.markdown(f'<div class="chat-bubble-user">{user_input}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bubble-ai">{ai_response}</div>', unsafe_allow_html=True)

elif not uploaded_file:
    st.info("👈 Please upload a PDF file from the sidebar.")
elif not api_key:
    st.warning("🔐 Please enter your Gemini API key to proceed.")
