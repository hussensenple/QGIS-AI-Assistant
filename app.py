import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page Configuration
st.set_page_config(page_title="🐍 QGIS Script Helper", page_icon="🐍", layout="wide")
st.title("🐍 QGIS PyQGIS Assistant")
st.caption("Your personal AI assistant for generating modern PyQGIS scripts")

# Default System Prompt based on Lab requirements
DEFAULT_SYSTEM_PROMPT = """You are an expert in QGIS Python scripting (PyQGIS).
When generating scripts:
1. Use the modern PyQGIS API (qgis.core, qgis.processing).
2. Use processing.run() for analysis operations whenever possible.
3. Always include error handling for missing layers.
4. Include a docstring and inline comments.
5. Output ONLY the Python code, no markdown fences, no explanation.
"""

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Secure API Key input - auto-fills from .env if available
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        value=os.environ.get("GOOGLE_API_KEY", ""),
        help="Enter your API key or set it in the .env file"
    )
    
    # Model Selection [Requirement from Lab]
    model_id = st.selectbox(
        "Select Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        help="Flash is faster, Pro is more capable for complex logic."
    )
    
    # Temperature Control [Requirement from Lab]
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.2, 0.1)
    
    st.divider()
    
    # System Prompt Customization
    system_prompt = st.text_area("System Instruction", value=DEFAULT_SYSTEM_PROMPT, height=200)

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask for a QGIS script (e.g., 'Buffer layer by 100m')"):
    if not api_key:
        st.error("⚠️ Please provide a Gemini API Key in the sidebar.")
        st.stop()

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_id,
        system_instruction=system_prompt
    )

    # Prepare history for Gemini
    gemini_history = []
    for msg in st.session_state.messages[:-1]:
        role = 'model' if msg['role'] == 'assistant' else 'user'
        gemini_history.append({'role': role, 'parts': [msg['content']]})

    # Generate Response with Streaming [Requirement from Lab]
    try:
        chat = model.start_chat(history=gemini_history)
        with st.chat_message("assistant"):
            response = chat.send_message(
                prompt, 
                stream=True,
                generation_config={"temperature": temperature}
            )
            full_response = st.write_stream(chunk.text for chunk in response)
        
        # Save assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")