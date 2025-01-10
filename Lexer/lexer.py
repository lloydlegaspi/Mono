from .check import *
from errors.base_error import *
from errors.lexer_errors import *
from .position import Position
from .tokens import *

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    # Scan Character Method
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    # Look-Ahead Method
    def nextState(self):
        try:
            char = self.text[self.pos.idx + 1] if self.pos.idx < len(self.text) else None
        except IndexError:
            char = ''
        return char if char is not None else ''
    
    # Look-Behind Method
    def backtrack(self):
        try:
            char = self.text[self.pos.idx - 1] if self.pos.idx > 0 else None
        except IndexError:
            char = ''     
        return char if char is not None else ''

    # Tokenization Method
    def make_tokens(self):
        tokens = []
        errors = []

        while self.current_char != None:
            char = self.current_char
            
            # Skips through whitespaces
            if isWhitespace(char):
                self.advance()

            # Scans constants, keywords, reserved words, noise words, logical, and identifiers
            elif isAlphabet(char) or char == '_':
                result = self.make_identifier()
                if isinstance(result, Token): 
                    tokens.append(result)
                elif isinstance(result, Error):
                    errors.append(result)

            # Scans arithmetic operators: +, -, *, /, ~, ^, %, invalid relational symbols such as !, &, |, &&, and ||, and assignment operator and relational lexemes
            elif isOperator(char):
                result = self.make_operator()
                if isinstance(result, Token):
                    tokens.append(result)
                elif isinstance(result, Error):
                    errors.append(result)
                
            # Handles comments
            elif char == '#':
                result = self.make_comments()
                if isinstance(result, Token):
                    tokens.append(result)
                elif isinstance(result, Error):
                    errors.append(result)
                
            # Scans for number and decimal lexemes
            elif isDigits(char) or char == '.':
                result = self.make_number()
                if isinstance(result, Token):
                    tokens.append(result)
                elif isinstance(result, Error):
                    errors.append(result)
                
            # Scans for string literals and multi-line docstrings
            elif char == '"':
                result = self.make_string_or_docstring()
                if isinstance(result, Token):
                    tokens.append(result)
                elif isinstance(result, Error):
                    errors.append(result)
                
            # Scans for special symbols such as ., ,, [, ], (, ), and newline character
            elif isSpecialSymbol(char):
                tokens.append(self.make_specialSymbol())
                self.advance()

            # Returns an error when an invalid character is scanned
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                errors.append(IllegalCharError(pos_start, self.pos.copy(), f"'{char}'"))
        
        # End of File
        tokens.append(Token('TT_EOF', TT_EOF, pos_start=self.pos.copy()))
        if errors:
            return tokens, errors
        else:
            return tokens, None


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
            details = f'"{lexeme}", Consider using "Or" instead.'
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
        if quotes == '"' and self.nextState() == '"':  # Detect the start of a multi-line docstring
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

        while self.current_char != None and (isAlphabet(self.current_char) or isDigits(self.current_char) or isWhitespace(self.current_char) or isUntracked(self.current_char) or self.current_char == '_' or self.current_char == '.'):
            temptchar = self.nextState()

            if isWhitespace(self.current_char):
                break
            elif num_str and self.current_char == '_' and temptchar == '_' or isValid == False:
                isValid = False
                num_str += self.current_char
            elif isAlphabet(self.current_char) or isUntracked(self.current_char):
                isValid = False
                num_str += self.current_char
            elif (not num_str and isDigits(self.current_char)) and isAlphabet(temptchar) and not isWhitespace(temptchar):
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


    def make_specialSymbol(self):
        if isSpecialSymbol(self.current_char):
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

        while self.current_char != None and (isAlphabet(self.current_char) or isDigits(self.current_char) or isWhitespace(self.current_char) or isUntracked(self.current_char) or self.current_char == '_'):
            # Whitespaces
            if isWhitespace(self.current_char):
                break

            # and = 'AND'
            elif self.current_char == 'a' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'n':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'd':
                        lexeme += self.current_char
                        tokentype = TT_AND
                        self.advance()


            # bool
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

            # const = RESERVED_WORD
            elif self.current_char == 'c' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'o':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'n':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 's':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 't':
                                lexeme += self.current_char
                                tokentype = TT_RESERVED_WORD
                                self.advance()
                        

            # def, default, do
            elif self.current_char == 'd' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                # def = RESERVED_WORD
                if self.current_char == 'e':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'f':
                        lexeme += self.current_char
                        tokentype = TT_KEYWORD
                        self.advance()
                        
                        # default = RESERVED_WORD
                        if self.current_char == 'a':
                            lexeme += self.current_char
                            tokentype = TT_IDENTIFIER
                            self.advance()
                            if self.current_char == 'u':
                                lexeme += self.current_char
                                self.advance()
                                if self.current_char == 'l':
                                    lexeme += self.current_char
                                    self.advance()
                                    if self.current_char == 't':
                                        lexeme += self.current_char
                                        tokentype = TT_RESERVED_WORD
                                        self.advance()
       
                                    
                # do = NOISE_WORD
                elif self.current_char == 'o':
                    lexeme += self.current_char
                    tokentype = TT_NOISE_WORD
                    self.advance()
                                    
                                    
            # elif, else, end, entity, except, exit, exp
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
                        
                    # entity = RESERVED_WORD
                    elif self.current_char == 't':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'i':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 't':
                                lexeme += self.current_char
                                self.advance()
                                if self.current_char == 'y':
                                    lexeme += self.current_char
                                    tokentype = TT_RESERVED_WORD
                                    self.advance()
                                    
                # except = KEYWORD
                elif self.current_char == 'x':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'c':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'p':
                                lexeme += self.current_char
                                self.advance()
                                if self.current_char == 't':
                                    lexeme += self.current_char
                                    tokentype = TT_KEYWORD
                                    self.advance()
                    
                    # exit = RESERVED_WORD
                    elif self.current_char == 'i':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 't':
                            lexeme += self.current_char
                            tokentype = TT_RESERVED_WORD
                            self.advance()
                            if (isWhitespace(self.nextState()) or self.nextState() == None) and self.fn != "<stdin>":
                                return ReferenceError(pos_start, self.pos.copy(), 'Usage of a reserved word.')
                            elif isWhitespace(self.nextState()) or self.nextState() == None:
                                exit()
                
                    # exp = RESERVED_WORD
                    elif self.current_char == 'p':
                        lexeme += self.current_char
                        tokentype = TT_RESERVED_WORD
                        self.advance()

            # false, , float, for                                  
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
                                
                # for = KEYWORD
                elif self.current_char == 'o':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'r':
                        lexeme += self.current_char
                        tokentype = TT_KEYWORD
                        self.advance()

            # get, give
            elif self.current_char == 'g' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # get = KEYWORD
                if self.current_char == 'e':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 't':
                        lexeme += self.current_char
                        tokentype = TT_KEYWORD
                        self.advance()
                        
                # give = KEYWORD
                elif self.current_char == 'i':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'v':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
            
            # halt, hide
            elif self.current_char == 'h' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # halt = KEYWORD
                if self.current_char == 'a':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'l':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 't':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
                            
                # hide = KEYWORD
                elif self.current_char == 'i':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'd':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
                            
            # if, int, imp
            elif self.current_char == 'i' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # if = KEYWORD
                if self.current_char == 'f':
                    lexeme += self.current_char
                    tokentype = TT_KEYWORD
                    self.advance()
                    
                # int = DATA_TYPE
                elif self.current_char == 'n':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 't':
                        lexeme += self.current_char
                        tokentype = TT_DATA_TYPE
                        self.advance()
                    
                # imp = RESERVED_WORD
                elif self.current_char == 'm':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'p':
                        lexeme += self.current_char
                        tokentype = TT_RESERVED_WORD
                        self.advance()
                    

            # new, none, not
            elif self.current_char == 'n' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # new = KEYWORD
                if self.current_char == 'e':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'w':
                        lexeme += self.current_char
                        tokentype = TT_KEYWORD
                        self.advance()
                        
                # none = RESERVED_WORD
                elif self.current_char == 'o':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'n':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            lexeme += self.current_char
                            tokentype = TT_RESERVED_WORD
                            self.advance()
                    
                    # not = 'NOT'
                    elif self.current_char == 't':
                            lexeme += self.current_char
                            tokentype = TT_NOT
                            self.advance()
  

            # or = 'OR'
            elif self.current_char == 'o' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'r':
                    lexeme += self.current_char
                    tokentype = TT_OR
                    self.advance()
                    
            # package = RESERVED_WORD
            elif self.current_char == 'p' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                if self.current_char == 'a':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'c':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'k':
                            lexeme += self.current_char
                            self.advance()
                            if self.current_char == 'a':
                                lexeme += self.current_char
                                self.advance()
                                if self.current_char == 'g':
                                    lexeme += self.current_char
                                    self.advance()  
                                    if self.current_char == 'e':
                                        lexeme += self.current_char
                                        tokentype = TT_RESERVED_WORD
                                        self.advance()
                                               
            # show, skip, start, str, sync
            elif self.current_char == 's' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                
                # show = KEYWORD
                if self.current_char == 'h':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'o':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'w':
                            lexeme += self.current_char
                            tokentype = TT_KEYWORD
                            self.advance()
                            
                # skip = KEYWORD
                elif self.current_char == 'k':
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
                
                # sync = RESERVED_WORD
                elif self.current_char == 'y':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'n':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'c':
                            lexeme += self.current_char
                            tokentype = TT_RESERVED_WORD
                            self.advance()


            # this, true, try, type
            elif self.current_char == 't' and len(lexeme) == 0:
                lexeme += self.current_char
                self.advance()
                        
                # this = KEYWORD
                if self.current_char == 'h':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'i':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 's':
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
                        
                # type = RESERVED_WORD
                elif self.current_char == 'y':
                    lexeme += self.current_char
                    self.advance()
                    if self.current_char == 'p':
                        lexeme += self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            lexeme += self.current_char
                            tokentype = TT_RESERVED_WORD
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

