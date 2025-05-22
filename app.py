import streamlit as st
import PyPDF2
import google.generativeai as genai
import re
from fpdf import FPDF

# ====== CUSTOM STYLE AND BACKGROUND ======
def set_bg_image():
    st.markdown(
        """
        <style>
        
        /* All text in the main area */
        .stMarkdown p, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
        .stText, .stHeading, .stSubheader, .stCaption {
            color: black !important;
        }
        /* Keep original background styles */
        .stApp {
            background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgYCf7zQFjCI8WO8Y5XFuGpes5GuCXbyIQEA&s");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }

        /* Keep original container styles */
        .block-container {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }

        /* UPDATED UPLOAD BOX STYLING - Changed to match space theme */
        div[data-testid="stFileUploader"] {
            background: linear-gradient(135deg, rgba(13, 27, 42, 0.9), rgba(27, 38, 59, 0.8)) !important;
            border: 2px dashed rgba(100, 149, 237, 0.6) !important;
            border-radius: 12px !important;
            padding: 25px !important;
            transition: all 0.3s ease !important;
            margin-bottom: 20px !important;
            backdrop-filter: blur(10px) !important;
        }

        div[data-testid="stFileUploader"]:hover {
            border-color: rgba(135, 206, 250, 0.8) !important;
            background: linear-gradient(135deg, rgba(13, 27, 42, 0.95), rgba(27, 38, 59, 0.85)) !important;
            box-shadow: 0 8px 25px rgba(100, 149, 237, 0.3) !important;
            transform: translateY(-2px) !important;
        }

        /* Target all inner elements of file uploader */
        div[data-testid="stFileUploader"] * {
            background-color: transparent !important;
        }

        /* Specific targeting for the white drag area */
        div[data-testid="stFileUploader"] > section {
            background: transparent !important;
        }

        div[data-testid="stFileUploader"] > section > div {
            background: rgba(13, 27, 42, 0.3) !important;
            border-radius: 8px !important;
            border: 1px dashed rgba(100, 149, 237, 0.4) !important;
        }

        div[data-testid="stFileUploader"] > section > div > div {
            background: transparent !important;
        }

        /* Upload button styling */
        div[data-testid="stFileUploader"] > section > div > div > button {
            background: linear-gradient(135deg, #4a6fa5, #5a7fb5) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(74, 111, 165, 0.4) !important;
        }

        div[data-testid="stFileUploader"] > section > div > div > button:hover {
            background: linear-gradient(135deg, #3a56b1, #4a66c1) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(74, 111, 165, 0.6) !important;
        }

        /* Text styling */
        div[data-testid="stFileUploader"] > label > p {
            color: rgba(255, 255, 255, 0.95) !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            margin-bottom: 15px !important;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
        }

        div[data-testid="stFileUploader"] > section > div > div > div > small {
            color: rgba(255, 255, 255, 0.8) !important;
            font-size: 13px !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
        }

        /* Style all text elements inside uploader */
        div[data-testid="stFileUploader"] > section > div > div > div,
        div[data-testid="stFileUploader"] > section > div > div > div > div,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] p {
            color: rgba(255, 255, 255, 0.9) !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
        }

        /* Keep all other original styles below */
        section[data-testid="stSidebar"] {
            background-color: #001f3f !important;
        }
        section[data-testid="stSidebar"] * {
            color: white !important;
        }
        .stDownloadButton {
            margin-top: 1rem;
        }
        .chat-bubble-user {
            background-color: #1877f2;
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            margin: 10px auto 10px 0;
            text-align: left;
            white-space: pre-wrap;
            word-wrap: break-word;
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
            word-wrap: break-word;
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
        text += page.extract_text()
    return text.strip()

# ====== CLEANUP FUNCTION ======
def clean_response(text):
    cleaned = re.sub(r'\n{3,}', '\n\n', text)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    return cleaned.strip()

# ====== GEMINI HANDLERS ======
def generate_quiz(text, model):
    prompt = f"""
    You are an experienced academic instructor.

    Based on the following semester outline, create a set of **5 multiple-choice questions** that assess conceptual understanding and critical thinking.

    - Each question should have four answer options labeled A to D.
    - Clearly indicate the correct answer at the end of each question.
    - Ensure the questions are relevant to the topics in the outline.

    Semester Outline:
    {text}
    """
    response = model.generate_content(prompt)
    return clean_response(response.text)
    

def generate_assignment(text, model):
    prompt = f"""
    You are an academic content creator.

    Using the following semester outline, generate a **well-structured and professional assignment**. The assignment should be suitable for university-level students and include:

    - A clear and concise **assignment title**
    - A brief **background or introduction** (2-3 lines)
    - Well-defined **objectives or learning outcomes**
    - **Detailed instructions** for the tasks to be completed
    - Any assumptions, requirements, or formatting guidelines

    Ensure the language is academic and formal. The assignment should reflect the depth and scope of the topics mentioned in the outline.

    Semester Outline:
    {text}
    """
    response = model.generate_content(prompt)
    return clean_response(response.text)
    

def ask_question(outline_text, user_query, model):
    prompt = f"Here is the semester outline:\n\n{outline_text}\n\nNow answer this user query: {user_query}"
    response = model.generate_content(prompt)
    return clean_response(response.text)

# ====== PDF CREATION ======
def text_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest='S').encode('latin1')

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

if "outline_text" not in st.session_state:
    st.session_state.outline_text = ""

if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    if not st.session_state.outline_text:
        with st.spinner("🔍 Extracting text from uploaded file..."):
            st.session_state.outline_text = extract_text_from_pdf(uploaded_file)
        st.success("✅ Outline processed!")

    query = st.text_input("✏️ Enter your input:").strip()

    if query and (ask_question_checked or generate_assignment_checked or generate_quiz_checked):
        with st.spinner("💬 Getting response from Gemini..."):
            if ask_question_checked:
                qna_resp = ask_question(st.session_state.outline_text, query, model)
                st.session_state.conversation_history.insert(0, (f"[Ask a Question] {query}", qna_resp))

            if generate_assignment_checked:
                assignment_resp = generate_assignment(st.session_state.outline_text, model)
                st.session_state.conversation_history.insert(0, (f"[Assignment] {query}", assignment_resp))
                assignment_pdf = text_to_pdf(assignment_resp)
                st.download_button("📅 Download Assignment PDF", assignment_pdf, file_name="assignment.pdf", mime="application/pdf")

            if generate_quiz_checked:
                quiz_resp = generate_quiz(st.session_state.outline_text, model)
                st.session_state.conversation_history.insert(0, (f"[Quiz] {query}", quiz_resp))
                quiz_pdf = text_to_pdf(quiz_resp)
                st.download_button("📝 Download Quiz PDF", quiz_pdf, file_name="quiz.pdf", mime="application/pdf")

    elif query and not (ask_question_checked or generate_assignment_checked or generate_quiz_checked):
        st.warning("☑️ Please select at least one action from the sidebar.")

    if st.session_state.conversation_history:
        st.markdown("### 💬 Chat History")
        for user_input, ai_response in st.session_state.conversation_history:
            st.markdown(f'<div class="chat-bubble-user">{user_input}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bubble-ai">{ai_response}</div>', unsafe_allow_html=True)

elif not uploaded_file:
    st.info("👈 Please upload a PDF file from the sidebar.")
elif not api_key:
    st.warning("🔒 Please enter your Gemini API key to proceed.")
