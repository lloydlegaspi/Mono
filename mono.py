import streamlit as st
from Lexer.tokens import *
from shell import *
import pandas as pd

# Set page layout to wide
st.set_page_config(layout="wide")

# Initialize session state
if "file_content" not in st.session_state:
    st.session_state["file_content"] = ""
if "lexer_output" not in st.session_state:
    st.session_state["lexer_output"] = ""

if "show_filename_input" not in st.session_state:
    st.session_state["show_filename_input"] = False 

def handle_errors(errors):
    # If errors is None, set it to an empty list to avoid iteration over NoneType
    if errors is None:
        errors = []
    
    error_output = ""
    for err in errors:
        if err is not None:  # Ensure we don't try to call as_string() on None
            error_output += err.as_string() + "\n"
    return error_output

def run_lex(filename, content):
    """Run lexical analysis and handle errors."""
    lexer_result, lexer_error = run_lexer(filename, content)
    lexer_output = print_tokens(filename, lexer_result) + "\n" + "_" * 35 + "\n\n"
    token_data = []

    if isinstance(lexer_result, list) and all(isinstance(tok, Token) for tok in lexer_result):
        lexer_output = print_tokens(filename, lexer_result) + "\n" + "_" * 35 + "\n\n"
        lexer_output += handle_errors(lexer_error)
        token_data = [{"Lexeme": tok.value, "Token": tok.type} for tok in lexer_result]
    
    return lexer_output, token_data


# Define the dialog function for the Open File functionality
@st.dialog("Open File", width="small")
def open_file_dialog():
    """Modal dialog for Open File functionality."""
    # Open file dialog
    uploaded_file = st.file_uploader("Upload a .mono file", type=["mono"], label_visibility="collapsed")
    
    if uploaded_file:
        # Store file content in session state
        st.session_state["file_content"] = uploaded_file.read().decode("utf-8")
        st.success(f"File uploaded successfully: {uploaded_file.name}")
        
        st.rerun()  # Rerun the app to reflect the uploaded file content
    else:
        st.info("Please upload a file to continue.")

# Define the dialog function using st.dialog
@st.dialog("Save As", width="small")
def save_file_dialog():
    """Modal dialog for Save As functionality."""
    filename_input = st.text_input("Enter Filename (without extension)", "unnamed", key="filename_input")
    
    save_button, cancel_button, col3 = st.columns([1, 1, 3])

    with save_button:
        # Create a download button instead of a regular button
        save_path = f"{filename_input}.mono"
        if st.download_button(
            label="Save",
            data=st.session_state["file_content"],  # The file content to be downloaded
            file_name=save_path,  # Filename for the download
            mime="text/plain", 
            use_container_width=True
        ):
            st.session_state["file_saved"] = save_path  # Store the save path in session state

    with cancel_button:
        if st.button("Cancel", use_container_width=True):
            st.rerun()  # Close the dialog by rerunning the app

    # Display the success message outside the modal
    if "file_saved" in st.session_state:
        st.success(f"File saved as {st.session_state['file_saved']}")
        del st.session_state["file_saved"]  # Clear the session state flag after showing the message

    
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
        # Save Button below the editor
        if st.button("Save As", use_container_width=True, help="Save the file as a .mono file", type="primary"):
            save_file_dialog()  # Trigger the save file dialog

    with col8:
        # Clear Button below the editor
        if st.button("Clear", use_container_width=True, help="Clear the editor content", type="primary"):
            st.session_state["file_content"] = ""  # Reset the content
            st.rerun()  # Rerun the app to reflect the cleared content

with col2:
    with st.container(border=True, height=520):
        if st.button("Run Lexer", use_container_width=True, type="primary", help="Run the lexer on the code"):
            content = st.session_state["file_content"].strip()
            if content:
                lexer_output, token_data = run_lex("unnamed", content)
                st.write(lexer_output, token_data)
                st.session_state["lexer_output"] = lexer_output
                st.session_state["symbol_table"] = token_data

                # Display token data as a table
                if token_data:
                    df = pd.DataFrame(token_data)
                    df['Lexeme'] = df['Lexeme'].astype(str)
                    
                    st.write("Lexical Analysis Output:")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
            else:
                st.warning("No content to analyze. Please write or upload a .mono file.")


