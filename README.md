<p align="center">
  <img src="assets/img/mono_logo.png" width = 30%/>
</p>

## Introduction

**Mono Programming Language: One Code. One Standard.**

Mono is a programming language designed for developers who value precision, uniformity, and order in their code. 
This project represents the Lexical Analyzer component of Mono, developed as part of the final project for COSC 303 - Principles of Programming Language.


## Prerequisites

To run Mono, you need Python 3.7 or later. Additionally, you'll need to install the required dependencies using `pip`.

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/lloydlegaspi/Mono.git
   cd Mono
   ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application
### Running with Streamlit GUI
1. Start the Streamlit app:

    ```bash
    streamlit run mono.py
    ```

2. This will launch the Streamlit interface in your default web browser. You can interact with the application using the provided graphical interface.

### Running from the Shell (CLI)
1. Run the Mono script directly from the command line:

    ```bash
    python shell.py
    ```
    
2. This will execute the application in the terminal. You will interact with the tool through the command line interface (CLI).

## File Structure
- .streamlit: Configuration files for the Streamlit app.
- Lexer: Contains the lexer logic for tokenizing Mono code.
- Utils: Utility functions for handling various operations.
- assets: Static files (such as images) for the application.
- errors: Error handling and reporting.
- mono.py: Main script for running the application.
- requirements.txt: List of dependencies required to run the project.
- test.mono: Example Mono code for testing.

## Contributors
In partial fulfillment of the course **COSC 303 - Principles of Programming Language**, the project is developed by **BSCS 3-5: Group 5**:

- Gavino, Migel D.
- Legaspi, John Lloyd S.
- Morcillos, Kyla Franchezka L.
- Quijano, Katherine P.
- Rolle, Xavier B.
- Romales, Justine Carl R.
- Valoria, Kyla Mae N.
