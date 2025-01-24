from .char_validators import *
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

    def advance(self):
        """
        Advances the position pointer to the next character in the input text.
        """
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def peek_next_char(self):
        """
        Peeks at the next character in the input text without advancing the position pointer.
        """
        try:
            char = self.text[self.pos.idx + 1] if self.pos.idx < len(self.text) else None
        except IndexError:
            char = ''
        return char if char is not None else ''

# ---- FIRST SCANNING METHOD ----

    def scan_tokens(self):
        """
        Scans the input text character by character and converts it into tokens.

        Returns:
            list: A list of tokens.
            list: A list of errors.
        """
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
                result = self.generate_identifier_token()
                (tokens if isinstance(result, Token) else errors).append(result)

            # Scans arithmetic operators: +, -, *, /, ~, ^, %, invalid relational symbols such as !, &, |, &&, and ||, and assignment operator and relational lexemes
            elif is_operator(char):
                result = self.generate_operator_token()
                (tokens if isinstance(result, Token) else errors).append(result)
                
            # Scans single-line comments
            elif char == '#':
                result = self.generate_comment_token()
                (tokens if isinstance(result, Token) else errors).append(result)
           
            # Scan for numbers only if the dot is followed by a digit
            elif is_digit(char) or (char == '.' and is_digit(self.peek_next_char())):
                result = self.generate_number_token()
                (tokens if isinstance(result, Token) else errors).append(result)
                
            # Scans for string literals and multi-line docstrings
            elif char == '"':
                result = self.generate_string_or_docstring_token()
                (tokens if isinstance(result, Token) else errors).append(result)
                
            # Scans for special symbols such as ., ,, [, ], (, ), and newline character
            elif is_special_symbol(char):
                tokens.append(self.generate_special_symbol_token())
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

# ---- SECOND SCANNING METHOD ----
    def generate_operator_token(self):
        """
        Handles arithmetic operators, invalid relational symbols, and assignment operators.
        
        Returns: 
            Token: The token containing the operator value.
        """
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
            elif self.current_char == '=':
                tokentype = TT_DIVIDE_ASSIGN
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
        
    def generate_comment_token(self):
        """
        Handles single-line comments, extracting the value and returning a token.

        Returns:
            Token: The token containing the comment value.
        """
        pos_start = self.pos.copy()
        comment_str = '#'
        self.advance()

        while self.current_char != '\n' and self.current_char is not None:
            comment_str += self.current_char
            self.advance()

        return Token(TT_COMMENT, comment_str, pos_start, self.pos.copy())
   
    def generate_string_or_docstring_token(self):
        """
        Handles string literals and multi-line docstrings, extracting the value and returning a token.
        
        Returns:
            Token: The token containing the string value.
        """
        string_value = ''
        quotes = self.current_char
        pos_start = self.pos.copy()

        # Check if it's the start of a multi-line docstring
        if quotes == '"' and self.peek_next_char() == '"':
            self.advance()  
            self.advance()  
            return self.make_multiline_string(pos_start)  

        if quotes == '"':  
            self.advance() 

            if self.current_char == '"': 
                self.advance()  
                return Token(TT_STRING, string_value, pos_start=pos_start, pos_end=self.pos.copy()) 

            # Handle string content and escape sequences
            while self.current_char != '"' and self.current_char is not None:
                if self.current_char == '\\':  
                    self.advance()  
                    if self.current_char in ['"', '\\']:  
                        string_value += self.current_char
                    else:
                        string_value += '\\'  
                else:
                    string_value += self.current_char
                self.advance()

            if self.current_char == '"':  
                self.advance()  
                return Token(TT_STRING, string_value, pos_start=pos_start, pos_end=self.pos.copy())

            return Error(pos_start, self.pos.copy(), 'Unterminated string literal', 'String is not properly closed')

        return None



    def make_multiline_string(self, pos_start):
        """
        Handles multi-line docstrings, extracting the value and returning a token.
        
        Returns:
            Token: The token containing the multi-line string value.
        """
        string_value = '"""'  
        self.advance()  

        # Capture the content between the triple quotes
        while self.current_char != None:
            if self.current_char == '"':  
                self.advance()
                if self.current_char == '"':  
                    self.advance()
                    if self.current_char == '"':  
                        self.advance()
                        string_value += '"""' 
                        return Token(TT_DOCSTRING, string_value, pos_start=pos_start, pos_end=self.pos.copy()) 
                    else:
                        string_value += '"'  
                else:
                    string_value += '"'  
            else:
                string_value += self.current_char
                self.advance()

        return Error(pos_start, self.pos.copy(), 'Unterminated multi-line string literal', 'Multi-line string is not properly closed')


    def generate_number_token(self):
        """
        Handles integer and float numbers, extracting the value and returning a token.
        
        Returns:
            Token: The token containing the number value.
        """
        pos_start = self.pos.copy()
        num_str = ''
        dot_count = 0
        is_valid = True
        id_identifier = False
            
        while self.current_char != None and (is_letter(self.current_char) or is_digit(self.current_char) or is_space(self.current_char) or is_invalid_symbol(self.current_char) or self.current_char == '_' or self.current_char == '.'):
            temptchar = self.peek_next_char()

            if is_space(self.current_char):
                break
            
            # Handle cases where the number starts with an underscore
            elif num_str and self.current_char == '_' and temptchar == '_' or   is_valid == False: 
                is_valid = False
                num_str += self.current_char
                
            elif is_letter(self.current_char) or is_invalid_symbol(self.current_char):
                is_valid = False
                num_str += self.current_char
            
            elif (not num_str and is_digit(self.current_char)) and is_letter(temptchar) and not is_space(temptchar):
                id_identifier = True
                num_str += self.current_char
            
            # Handle the dot in the number
            elif self.current_char == '.':
                if dot_count == 1:
                    dot_count += 1
                dot_count += 1
                num_str += '.'
            else:
                if self.current_char != '_':
                    num_str += self.current_char
            self.advance()

        # Error handling for invalid numbers
        if dot_count == 0 and   is_valid == True and id_identifier == False:
            return Token(TT_INTEGER, int(num_str), pos_start, self.pos.copy())
        elif dot_count == 2 and is_valid == True:
            return LexicalError(pos_start, self.pos.copy(), f'{num_str}')
        elif id_identifier:
            return IllegalIdentifierError(pos_start, self.pos.copy(), f'{num_str}')
        elif    is_valid == False:
            return IllegalNumberError(pos_start, self.pos.copy(), f'{num_str}')
        elif num_str == '.':
            return Token(TT_DOT, num_str, pos_start, self.pos.copy())
        else:
            try:
                return Token(TT_FLOAT, float(num_str), pos_start, self.pos.copy())
            except ValueError:
                return InvalidDecimalError(pos_start, self.pos.copy(), "Invalid Decimal")


    def generate_special_symbol_token(self):
        """
        Handles special symbols such as ., ,, [, ], (, ), and newline character.
        
        Returns:
            Token: The token containing the special symbol value.
        """
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
                return Token(TT_NEWLINE, '\\n', self.pos.copy())
    
    
    def generate_identifier_token(self):
        """
        Handles keywords, reserved words, noise words, boolean values, data types, and identifiers.
        
        Returns:
            Token: The token containing the identifier value.
        """
        lexeme = ''
        tokentype = TT_IDENTIFIER
        pos_start = self.pos.copy()

        while self.current_char != None and (is_letter(self.current_char) or is_digit(self.current_char) or is_space(self.current_char) or is_invalid_symbol(self.current_char) or self.current_char == '_'):
            # Whitespaces
            if is_space(self.current_char):
                break

            # and, any, as
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
                    # any = 'ANY'
                    elif self.current_char == 'y':
                        lexeme += self.current_char
                        tokentype = TT_KEYWORD
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
        
        # Determine the type of identifier after building the lexeme
        if lexeme.isupper() and lexeme.startswith('_'):
            tokentype = TT_PRIV_CONST_IDENTIFIER
        elif lexeme.isupper():
            tokentype = TT_CONST_IDENTIFIER
        elif lexeme.startswith('_'):
            tokentype = TT_PRIV_IDENTIFIER

        return Token(tokentype, lexeme, pos_start, self.pos.copy())

