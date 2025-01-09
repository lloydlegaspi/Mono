from Lexer.lexer import Lexer
from Lexer.tokens import *
import sys

def debug_lexer():
    while True:
        text = input("lexer > ")
        if text.strip() == "": continue
        result, error, _ = run_lexer("<stdin>", text)

        if error:
            try:
                for err in error:
                    print(err.as_string())
            except(TypeError):
                print(error.as_string())
        elif result:
            output_to_symbolTable(result)
            result.pop()
            print(repr(result))


def run_lexer(fn, text):
    # Lexer
    lexer = Lexer(fn, text)
    symboltable, error = lexer.make_tokens()

    return symboltable, error

def print_tokens(fn, tokens):
    text = ''
    text += f'{"TOKENS": >25}                LEXEMES\n'
    text += '________________________________\n\n'
    text += tok_to_str(tokens)

    return text

# Run File Command
def run_file(filename):
    if filename:
        if filename.lower().endswith('.mono'):
            try:
                with open(filename, 'r') as f:
                    text = f.read()
                
                result, error = run_lexer(filename, text)

                if result:
                    print(print_tokens(filename, result))
                if error:
                    try:
                        for err in error:
                            print(err.as_string())
                    except TypeError:
                        print(error.as_string())
            except FileNotFoundError:
                print("File does not exist!")
        else:
            print("Invalid file name extension!")


# Shell Commands
OPTIONS = {'-f', '-file', '-c', 'cli'}
lowercasedArgs = [arg.lower() for arg in sys.argv]

if __name__ == '__main__':
    if '-cli' in lowercasedArgs or '-c' in lowercasedArgs:
        while True:
            text = input("mono > ")

            result, error = run_lexer("<stdin>", text)

            if error:
                print(error.as_string())
            elif result:
                output_to_symbolTable(result)
                result.pop()
                print(result)
    elif '-file' in lowercasedArgs or '-f' in lowercasedArgs:
        if '-f' in lowercasedArgs:
            flagidx = lowercasedArgs.index('-f') 
        elif '-file' in lowercasedArgs:
            flagidx = lowercasedArgs.index('-file')
        try:
            run_file(sys.argv[flagidx + 1])
        except IndexError:
            print("No file name argument is found!")
    else:
        try:
            print(sys.argv)
            if len(sys.argv) <= 2:
                print(f'Unknown option: {sys.argv[1]}')
                print('usage: python shell.py [option] ... [-cli | -c] | ([-file | -f] [arg])')
            elif len(sys.argv) >= 3:
                print(f'SyntaxError: No valid option found!')
                print('usage: python shell.py [option] ... [-cli | -c] | ([-file | -f] [arg])')
        except IndexError:
            print('No valid argument found!')