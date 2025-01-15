from .check import *
from errors.base_error import *
from errors.lexer_errors import *
from .position import Position
from .tokens import *

class Lexer:
    """
    The Lexer class tokenizes the input text character by character and converts it into tokens.
    It also reports errors and warnings.
    """
    def __init__(self, fn, text):
        self.fn = fn # filename
        self.text = text # input text
        self.pos = Position(-1, 0, -1, fn, text) # position pointer
        self.current_char = None # current character
        self.advance()

    # Advances the position pointer
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    # Returns the next character
    def next_state(self):
        try:
            char = self.text[self.pos.idx + 1] if self.pos.idx < len(self.text) else None
        except IndexError:
            char = ''
        return char if char is not None else ''

    # Tokenizes the input text
    def make_tokens(self):
        tokens = []
        errors = []

        # Scans the input text character by character
        while self.current_char != None:
            char = self.current_char
            
            # Skips whitespaces
            if is_space(char):
                self.advance()

            # Scans keywords, reserved words, noise words, boolean values, data types, and identifiers
            elif is_letter(char) or char == '_':
                result = self.make_identifier()
                (tokens if isinstance(result, Token) else errors).append(result)

            # Scans arithmetic operators: +, -, *, /, ~, ^, %, invalid relational symbols such as !, &, |, &&, and ||, and assignment operator and relational lexemes
            elif is_operator(char):
                result = self.make_operator()
                (tokens if isinstance(result, Token) else errors).append(result)
                
            # Scans single-line comments
            elif char == '#':
                result = self.make_comments()
                (tokens if isinstance(result, Token) else errors).append(result)
                
            # Scans for number and decimal lexemes
            elif is_digit(char) or char == '.':
                result = self.make_number()
                (tokens if isinstance(result, Token) else errors).append(result)
                
            # Scans for string literals and multi-line docstrings
            elif char == '"':
                result = self.make_string_or_docstring()
                (tokens if isinstance(result, Token) else errors).append(result)
                
            # Scans for special symbols such as ., ,, [, ], (, ), and newline character
            elif is_special_symbol(char):
                tokens.append(self.make_special_symbol())
                self.advance()

            # Returns an error when an invalid character is scanned
            else:
                pos_start = self.pos.copy()
                self.advance()
                errors.append(IllegalCharError(pos_start, self.pos.copy(),
                                               f"Illegal character '{char}' at line {pos_start.ln + 1}, column {pos_start.col + 1}"))
        
        # End of File
        tokens.append(Token('TT_EOF', TT_EOF, pos_start=self.pos.copy()))
        return tokens, errors if errors else None


    def make_operator(self):
        tokentype = ''
        lexeme = ''
        details = ''
        isTok = False
        isErr = False
        pos_start = self.pos.copy()

        if self.current_char == '+':
            tokentype = TT_PLUS
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_PLUS_ASSIGN
                lexeme += self.current_char
                isTok = True
                self.advance()
            elif self.current_char == '+':
                tokentype = TT_INCREMENT
                lexeme += self.current_char
                isTok = True
                self.advance()
        elif self.current_char == '-':
            tokentype = TT_MINUS
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_MINUS_ASSIGN
                lexeme += self.current_char
                isTok = True
                self.advance()
            elif self.current_char == '-':
                tokentype = TT_DECREMENT
                lexeme += self.current_char
                isTok = True
                self.advance()
        elif self.current_char == '*':
            tokentype = TT_MULTIPLY
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                    tokentype = TT_MULTIPLY_ASSIGN
                    lexeme += self.current_char
                    isTok = True
                    self.advance()
            
        elif self.current_char == '/':
            tokentype = TT_DIVIDE
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '/':
                tokentype = TT_FLOOR_DIVIDE
                lexeme += self.current_char
                isTok = True
                self.advance()
                if self.current_char == '=':
                    tokentype = TT_FLOOR_DIVIDE_ASSIGN
                    lexeme += self.current_char
                    isTok = True
                    self.advance()
        elif self.current_char == '^':
            tokentype = TT_EXPONENT
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_EXPONENT_ASSIGN
                lexeme += self.current_char
                isTok = True
                self.advance()
        elif self.current_char == '%':
            tokentype = TT_MODULO
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_MODULO_ASSIGN
                lexeme += self.current_char
                isTok = True
                self.advance()
        elif self.current_char == '=':
            tokentype = TT_ASSIGNMENT
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_EQUAL
                lexeme += self.current_char
                isTok = True
                self.advance()
        elif self.current_char == '>':
            tokentype = TT_GREATER
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_GREATER_EQUAL
                lexeme += self.current_char
                isTok = True
                self.advance()
        elif self.current_char == '<':
            tokentype = TT_LESS
            lexeme += self.current_char
            isTok = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_LESS_EQUAL
                lexeme += self.current_char
                isTok = True
                self.advance()
        elif self.current_char == '!':
            lexeme += self.current_char
            details = f'"{lexeme}", Consider using "not" instead.'
            isErr = True
            self.advance()
            if self.current_char == '=':
                tokentype = TT_NOT_EQUAL
                lexeme += self.current_char
                isTok = True
                isErr = False
                self.advance()
        elif self.current_char == '&':
            lexeme += self.current_char
            details = f'"{lexeme}", Consider using "and" instead.'
            isErr = True
            self.advance()
            if self.current_char == '&':
                lexeme += self.current_char
                details = f'"{lexeme}", Consider using "and" instead.'
                isErr = True
                self.advance()
        elif self.current_char == '|':
            lexeme += self.current_char
            details = f'"{lexeme}", Consider using "or" instead.'
            isErr = True
            self.advance()
            if self.current_char == '|':
                lexeme += self.current_char
                details = f'"{lexeme}", Consider using "or" instead.'
                isErr = True
                self.advance()

        if isTok:
            return Token(tokentype, lexeme, pos_start, self.pos.copy())
        elif isErr:
            return InvalidRelationalSymbol(pos_start, self.pos.copy(), details)
        
    # Create Token for Single-Line Comments
    def make_comments(self):
        pos_start = self.pos.copy()
        comment_str = '#'
        self.advance()

        while self.current_char != '\n' and self.current_char is not None:
            comment_str += self.current_char
            self.advance()

        return Token(TT_COMMENT, comment_str, pos_start, self.pos.copy())
   
    def make_string_or_docstring(self):
        """
        Handles string literals and multi-line docstrings, extracting the value
        and determining whether it's a single-line or multi-line string.
        """
        string_value = ''
        quotes = self.current_char
        pos_start = self.pos.copy()

        # Check if it's the start of a multi-line docstring
        if quotes == '"' and self.next_state() == '"':  # Detect the start of a multi-line docstring
            self.advance()  # Skip the first quote
            self.advance()  # Skip the second quote
            return self.make_multiline_string(pos_start)  # Process the multi-line docstring

        if quotes == '"':  # Single-line string
            self.advance()  # Skip the initial quote

            # Check for an empty string ""
            if self.current_char == '"':  # If the next character is another quote, it's an empty string ""
                self.advance()  # Skip the closing quote
                return Token('TT_STRING', string_value, pos_start=pos_start, pos_end=self.pos.copy())  # Return empty string

            # Handle string content and escape sequences
            while self.current_char != '"' and self.current_char is not None:
                if self.current_char == '\\':  # Handle escape sequences
                    self.advance()  # Skip the backslash
                    if self.current_char in ['"', '\\']:  # Handle escape characters
                        string_value += self.current_char
                    else:
                        string_value += '\\'  # Just add the backslash if not a recognized escape sequence
                else:
                    string_value += self.current_char
                self.advance()

            if self.current_char == '"':  # End of string
                self.advance()  # Skip the closing quote
                return Token('TT_STRING', string_value, pos_start=pos_start, pos_end=self.pos.copy())

            return Error(pos_start, self.pos.copy(), 'Unterminated string literal', 'String is not properly closed')

        return None



    def make_multiline_string(self, pos_start):
        """
        Scans for a multi-line string (triple quotes) and handles escape sequences.
        """
        string_value = '"""'  # Include the starting triple quotes in the lexeme
        # Skip the first part of the triple quotes (""" at the start)
        self.advance()  # Skip the first quote

        # Capture the content between the triple quotes
        while self.current_char != None:
            if self.current_char == '"':  # Found one part of the closing quote
                self.advance()
                if self.current_char == '"':  # Check for closing triplets (""" or """)
                    self.advance()
                    if self.current_char == '"':  # Found the closing triplet
                        self.advance()
                        string_value += '"""'  # Add the closing triple quotes to the lexeme
                        return Token('TT_DOCSTRING', string_value, pos_start=pos_start, pos_end=self.pos.copy())  # Return the docstring
                    else:
                        string_value += '"'  # Add one quote and continue
                else:
                    string_value += '"'  # Add one quote and continue
            else:
                string_value += self.current_char
                self.advance()

        return Error(pos_start, self.pos.copy(), 'Unterminated multi-line string literal', 'Multi-line string is not properly closed')


    def make_number(self):
        pos_start = self.pos.copy()
        num_str = ''
        dot_count = 0
        isValid = True
        isIdentifier = False

        while self.current_char != None and (is_letter(self.current_char) or is_digit(self.current_char) or is_space(self.current_char) or is_invalid_symbol(self.current_char) or self.current_char == '_' or self.current_char == '.'):
            temptchar = self.next_state()

            if is_space(self.current_char):
                break
            elif num_str and self.current_char == '_' and temptchar == '_' or isValid == False:
                isValid = False
                num_str += self.current_char
            elif is_letter(self.current_char) or is_invalid_symbol(self.current_char):
                isValid = False
                num_str += self.current_char
            elif (not num_str and is_digit(self.current_char)) and is_letter(temptchar) and not is_space(temptchar):
                isIdentifier = True
                num_str += self.current_char
            elif self.current_char == '.':
                if dot_count == 1:
                    dot_count += 1
                dot_count += 1
                num_str += '.'
            else:
                if self.current_char != '_':
                    num_str += self.current_char
            self.advance()

        if dot_count == 0 and isValid == True and isIdentifier == False:
            return Token(TT_INTEGER, int(num_str), pos_start, self.pos.copy())
        elif dot_count == 2 and isValid == True:
            return LexicalError(pos_start, self.pos.copy(), f'{num_str}')
        elif isIdentifier:
            return IllegalIdentifierError(pos_start, self.pos.copy(), f'{num_str}')
        elif isValid == False:
            return IllegalNumberError(pos_start, self.pos.copy(), f'{num_str}')
        elif num_str == '.':
            return Token(TT_DOT, num_str, pos_start, self.pos.copy())
        else:
            try:
                return Token(TT_FLOAT, float(num_str), pos_start, self.pos.copy())
            except ValueError:
                return InvalidDecimalError(pos_start, self.pos.copy(), "Invalid Decimal")


    def make_special_symbol(self):
        if is_special_symbol(self.current_char):
            char = self.current_char
            if char == '.':
                return Token(TT_DOT, char, self.pos.copy())
            elif char == ',':
                return Token(TT_COMMA, char, self.pos.copy())
            elif char == '?':
                return Token(TT_QUESTION, char, self.pos.copy())
            elif char == ':':
                return Token(TT_COLON, char, self.pos.copy())
            elif char == ';':
                return Token(TT_SEMICOLON, char, self.pos.copy())
            elif char == '[':
                return Token(TT_LSQUARE, char, self.pos.copy())
            elif char == ']':
                return Token(TT_RSQUARE, char, self.pos.copy())
            elif char == '(':
                return Token(TT_LPAREN, char, self.pos.copy())
            elif char == ')':
                return Token(TT_RPAREN, char, self.pos.copy())
            elif char == '{':
                return Token(TT_LCURLY, char, self.pos.copy())
            elif char == '}':
                return Token(TT_RCURLY, char, self.pos.copy())
            elif char == '\n':
                return Token(TT_NEWLINE, char, self.pos.copy())
    
    
    # SCANNING METHODS
    def make_identifier(self):
        lexeme = ''
        tokentype = TT_IDENTIFIER
        pos_start = self.pos.copy()

        while self.current_char != None and (is_letter(self.current_char) or is_digit(self.current_char) or is_space(self.current_char) or is_invalid_symbol(self.current_char) or self.current_char == '_'):
            # Whitespaces
            if is_space(self.current_char):
                break

            # and, as
            elif self.current_char == 'a' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                # and = 'AND'
                if self.current_char == 'n':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'd':
                        lexeme += self.current_char
                        tokentype = TT_AND
                        self.advance()
                # as = KEYWORD
                elif self.current_char == 's':
                    lexeme += self.current_char
                    tokentype = TT_KEYWORD
                    self.advance()
                        


            # bool, break
            elif self.current_char == 'b' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # bool = DATA_TYPE
                if self.current_char == 'o':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'o':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'l':
                            lexeme += self.current_char
                            tokentype = TT_DATA_TYPE
                            self.advance()
                
                # break = KEYWORD
                elif self.current_char == 'r':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'e':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'a':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'k':
                                lexeme += self.current_char
                                tokentype = TT_KEYWORD
                                self.advance()

            # catch
            elif self.current_char == 'c' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # catch = KEYWORD
                if self.current_char == 'a':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 't':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'c':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'h':
                                lexeme += self.current_char
                                tokentype = TT_KEYWORD
                                self.advance()
                            
                        

            # dict, do
            elif self.current_char == 'd' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                # dict = KEYWORD
                if self.current_char == 'i':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'c':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 't':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
                                           
                # do = NOISE_WORD
                elif self.current_char == 'o':
                    lexeme += self.current_char
                    tokentype = TT_NOISE_WORD
                    self.advance()
                                    
                                    
            # elif, else, end, ensure
            elif self.current_char == 'e' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # elif = KEYWORD
                if self.current_char == 'l':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'i':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'f':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
                            
                    # else = KEYWORD
                    elif self.current_char == 's':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
                            
                # end = NOISE_WORD
                elif self.current_char == 'n':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'd':
                        lexeme += self.current_char
                        tokentype = TT_NOISE_WORD
                        self.advance()
                        
                    # ensure = KEYWORD
                    elif self.current_char == 's':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'u':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'r':
                                lexeme += self.current_char
                                self.advance()
                                if self.current_char == 'e':
                                    lexeme += self.current_char
                                    tokentype = TT_KEYWORD
                                    self.advance()
                                

            # false, float, fn, for                                  
            elif self.current_char == 'f' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # false = BOOL
                if self.current_char == 'a':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'l':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 's':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'e':
                                lexeme += self.current_char
                                tokentype = TT_BOOL
                                self.advance()
                
                # float = DATA_TYPE
                elif self.current_char == 'l':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'o':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'a':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 't':
                                lexeme += self.current_char
                                tokentype = TT_DATA_TYPE
                                self.advance()
                
                # fn = KEYWORD
                elif self.current_char == 'n':
                    lexeme += self.current_char
                    tokentype = TT_KEYWORD
                    self.advance()
                                
                # for = KEYWORD
                elif self.current_char == 'o':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'r':
                        lexeme += self.current_char
                        tokentype = TT_KEYWORD
                        self.advance()
                            
            # if, import, in, input, int
            elif self.current_char == 'i' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # if = KEYWORD
                if self.current_char == 'f':
                    lexeme += self.current_char
                    tokentype = TT_KEYWORD
                    self.advance()
                    
                # import = RESERVED_WORD
                elif self.current_char == 'm':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'p':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'o':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'r':
                                lexeme += self.current_char
                                self.advance()
                                if self.current_char == 't':
                                    lexeme += self.current_char
                                    tokentype = TT_RESERVED_WORD
                                    self.advance()
                
                # in = KEYWORD
                elif self.current_char == 'n':
                    lexeme += self.current_char
                    tokentype = TT_KEYWORD
                    self.advance()
        
                    # input = KEYWORD
                    if self.current_char == 'p':
                        lexeme += self.current_char
                        tokentype = TT_IDENTIFIER
                        self.advance()
                        if self.current_char == 'u':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 't':
                                lexeme += self.current_char
                                tokentype = TT_KEYWORD
                                self.advance()
                    
                    # int = DATA_TYPE
                    elif self.current_char == 't':
                        lexeme += self.current_char
                        tokentype = TT_DATA_TYPE
                        self.advance()
                        
                    

            # not, null
            elif self.current_char == 'n' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
            
                # not = 'NOT'
                if self.current_char == 'o':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 't':
                            lexeme += self.current_char
                            tokentype = TT_NOT
                            self.advance()
                            
                # null = 'NULL'
                elif self.current_char == 'u':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'l':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'l':
                            lexeme += self.current_char
                            tokentype = TT_RESERVED_WORD
                            self.advance()
  

            # or = 'OR'
            elif self.current_char == 'o' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'r':
                    lexeme += self.current_char
                    tokentype = TT_OR
                    self.advance()
                    
            # print = KEYWORD
            elif self.current_char == 'p' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'r':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'i':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'n':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 't':
                                lexeme += self.current_char
                                tokentype = TT_KEYWORD
                                self.advance()
            
            # return = KEYWORD
            elif self.current_char == 'r' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'e':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 't':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'u':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'r':
                                lexeme += self.current_char
                                self.advance()
                                if self.current_char == 'n':
                                    lexeme += self.current_char
                                    tokentype = TT_KEYWORD
                                    self.advance()
                                               
            # skip, start, str
            elif self.current_char == 's' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                                  
                # skip = KEYWORD
                if self.current_char == 'k':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'i':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'p':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
                
                # start = NOISE_WORD
                elif self.current_char == 't':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'a':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'r':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 't':
                                lexeme += self.current_char
                                tokentype = TT_NOISE_WORD
                                self.advance()
                    
                    # str = DATA_TYPE
                    elif self.current_char == 'r':
                        lexeme += self.current_char
                        tokentype = TT_DATA_TYPE
                        self.advance()


            # throw, true, try
            elif self.current_char == 't' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                        
                # throw = KEYWORD
                if self.current_char == 'h':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'r':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'o':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'w':
                                lexeme += self.current_char
                                tokentype = TT_KEYWORD
                                self.advance()
                            
                # true = BOOL
                elif self.current_char == 'r':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'u':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            lexeme += self.current_char
                            tokentype = TT_BOOL
                            self.advance()
                            
                    # try = KEYWORD
                    elif self.current_char == 'y':
                        lexeme += self.current_char
                        tokentype = TT_KEYWORD
                        self.advance()
                        

            # while = KEYWORD
            elif self.current_char == 'w' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'h':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'i':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'l':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char =='e':
                                lexeme += self.current_char
                                tokentype = TT_KEYWORD
                                self.advance()

            # Other identifiers
            else:
                lexeme += self.current_char
                tokentype = TT_IDENTIFIER
                self.advance()

        return Token(tokentype, lexeme, pos_start, self.pos.copy())

