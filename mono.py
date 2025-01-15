import streamlit as st
from Lexer.tokens import *
import pandas as pd
from Lexer.lexer import Lexer

st.set_page_config(layout="wide", page_title="Mono Lexer", page_icon="📄")

def initialize_session_state():
    """Initialize session state variables."""
    st.session_state.setdefault("file_content", "")
    st.session_state.setdefault("lexer_output", "")
    st.session_state.setdefault("errors", [])

initialize_session_state()

def format_errors(errors):
    """Format errors into a readable string."""
    return "No errors found." if not errors else "\n".join(err.as_string() for err in errors if err)

def run_lexer(filename, text):
    """Run the lexer to generate tokens and errors."""
    lexer = Lexer(filename, text)
    return lexer.make_tokens()

def lexical_analysis(filename, content):
    """Perform lexical analysis and return results."""
    tokens, errors = run_lexer(filename, content)

    token_data = [
        {"Lexeme": tok.value, "Token": tok.type} for tok in tokens
        if isinstance(tok, Token)
    ]

    error_output = format_errors(errors)
    return token_data, error_output

@st.dialog("Open File", width="small")
def open_file_dialog():
    """Modal dialog for Open File functionality."""
    uploaded_file = st.file_uploader("Upload a .mono file", type=["mono"], label_visibility="collapsed")
    
    if uploaded_file:
        st.session_state["file_content"] = uploaded_file.read().decode("utf-8")
        st.success(f"File uploaded successfully: {uploaded_file.name}")
        
        st.rerun() 
    else:
        st.info("Please upload a file to continue.")

@st.dialog("Save As", width="small")
def save_file_dialog():
    """Modal dialog for Save As functionality."""
    filename_input = st.text_input("Enter Filename (without extension)", "unnamed", key="filename_input")
    
    save_button, cancel_button, col3 = st.columns([1, 1, 3])

    with save_button:
        save_path = f"{filename_input}.mono"
        if st.download_button(
            label="Save",
            data=st.session_state["file_content"],  
            file_name=save_path,
            mime="text/plain", 
            use_container_width=True
        ):
            st.session_state["file_saved"] = save_path  

    with cancel_button:
        if st.button("Cancel", use_container_width=True):
            st.rerun() 

    if "file_saved" in st.session_state:
        st.success(f"File saved as {st.session_state['file_saved']}")
        del st.session_state["file_saved"] 

    
col1, col2= st.columns([6, 2])
with col1:
    col3, col4, col5= st.columns([5, 3, 5])
    with col4:
        st.image('assets/img/mono_logo.png', width=300)

    code_editor = st.text_area("**Mono Editor**", value=st.session_state["file_content"], height=400)

    if code_editor != st.session_state["file_content"]:
        st.session_state["file_content"] = code_editor

    col5, col6, col7, col8 = st.columns([1, 1, 6, 1])

    with col5:
        if st.button("Open File", use_container_width=True, help="Open a .mono file", type="primary"):
            open_file_dialog()

    with col6:
        if st.button("Save As", use_container_width=True, help="Save the file as a .mono file", type="primary"):
            save_file_dialog() 

    with col8:
        if st.button("Clear", use_container_width=True, help="Clear the editor content", type="primary"):
            st.session_state["file_content"] = "" 
            st.rerun() 

with col2:
    with st.container(border=True, height=520):
        if st.button("Run Lexer", use_container_width=True, type="primary", help="Run the lexer on the code"):
            content = st.session_state["file_content"].strip()
            if content:
                token_data, error_output = lexical_analysis("unnamed", content)
                st.session_state["errors"] = error_output

                st.write("Errors:")
                st.text(error_output)

                if token_data:
                    st.write("Lexical Analysis Output:")
                    st.dataframe(pd.DataFrame(token_data), use_container_width=True, hide_index=True)
            else:
                st.warning("No content to analyze. Please write or upload a .mono file.")


