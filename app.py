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
        section[data-testid="stSidebar"] {
            background-color: #001f3f !important;
        }
        section[data-testid="stSidebar"] * {
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
    You are an expert academic content creator.

    Create 5 well-structured multiple-choice questions (MCQs) based on the provided semester outline.

    Guidelines:
    - Each question must have four options (A to D).
    - Ensure only one correct answer per question.
    - Highlight the correct answer at the end of each question using this format: **Correct Answer: B**
    - Cover diverse topics from the outline and make questions conceptually meaningful.

    Semester Outline:
    {text}
    """
    response = model.generate_content(prompt)
    return clean_response(response.text)

def generate_assignment(text, model):
    prompt = f"""
    You are an academic coordinator.

    Based on the following semester outline, create a detailed assignment brief including:
    - Assignment Title
    - Objectives (2 to 3)
    - Assignment Tasks (2 to 4 bullet points)
    - Submission Guidelines
    - Word Limit

    Ensure that the tasks align with key topics in the outline and require critical thinking and analysis.

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
        st.success("✅ Text extracted from PDF successfully!")

    outline_text = st.session_state.outline_text

    if ask_question_checked:
        user_question = st.text_input("❓ Enter your question:")
        if user_question:
            with st.spinner("Generating answer..."):
                answer = ask_question(outline_text, user_question, model)
            st.markdown("### Answer")
            st.markdown(answer)

    if generate_assignment_checked:
        if st.button("📝 Generate Assignment"):
            with st.spinner("Creating assignment..."):
                assignment = generate_assignment(outline_text, model)
            st.markdown("### Assignment")
            st.markdown(assignment)
            st.download_button("⬇️ Download Assignment as PDF", data=text_to_pdf(assignment), file_name="assignment.pdf")

    if generate_quiz_checked:
        if st.button("🧠 Generate Quiz"):
            with st.spinner("Creating quiz..."):
                quiz = generate_quiz(outline_text, model)
            st.markdown("### Quiz")
            st.markdown(quiz)
            st.download_button("⬇️ Download Quiz as PDF", data=text_to_pdf(quiz), file_name="quiz.pdf")

else:
    st.info("Please upload a PDF and enter your Gemini API key to proceed.")
    
