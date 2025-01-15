# IDENTIFIER
TT_IDENTIFIER = 'IDENTIFIER'

# OPERATORS
TT_ASSIGNMENT = 'ASSIGNMENT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MULTIPLY = 'MULTIPLY'
TT_DIVIDE = 'DIVIDE'
TT_FLOOR_DIVIDE = 'FLOOR_DIVIDE'
TT_EXPONENT = 'EXPONENT'
TT_MODULO = 'MODULO'
TT_PLUS_ASSIGN = 'PLUS_ASSIGN'
TT_MINUS_ASSIGN = 'MINUS_ASSIGN'
TT_MULTIPLY_ASSIGN = 'MULTIPLY_ASSIGN'
TT_DIVIDE_ASSIGN = 'DIVIDE_ASSIGN'
TT_FLOOR_DIVIDE_ASSIGN = 'FLOOR_DIVIDE_ASSIGN'
TT_EXPONENT_ASSIGN = 'EXPONENT_ASSIGN'
TT_MODULO_ASSIGN = 'MODULO_ASSIGN'
TT_INCREMENT = 'INCREMENT'
TT_DECREMENT = 'DECREMENT'

# RELATIONAL
TT_GREATER = 'GREATER_THAN'
TT_LESS = 'LESS_THAN'
TT_GREATER_EQUAL = 'GREATER_EQUAL'
TT_LESS_EQUAL = 'LESS_EQUAL'
TT_EQUAL = 'EQUAL'
TT_NOT_EQUAL = 'NOT_EQUAL'

# LOGICAL
TT_NOT = 'NOT'
TT_AND = 'AND'
TT_OR = 'OR'

# CONSTANTS
TT_INTEGER = 'INTEGER'
TT_FLOAT = 'FLOAT'
TT_STRING= 'STRING'
TT_BOOL = 'BOOL'

# DATA TYPES
TT_DATA_TYPE = 'DATA_TYPE'

# KEYWORDS
TT_KEYWORD = 'KEYWORD'

# RESERVED WORDS
TT_RESERVED_WORD = 'RESERVED_WORD'

# NOISE WORDS
TT_NOISE_WORD = 'NOISE_WORD'

# COMMENTS
TT_COMMENT = 'COMMENT'
TT_DOCSTRING = 'DOCSTRING'

# SPECIAL SYMBOLS
TT_DOT = 'DOT'
TT_COMMA = 'COMMA'
TT_QUESTION = 'QUESTION_MARK'
TT_COLON = 'COLON'
TT_SEMICOLON = 'SEMICOLON'
TT_LSQUARE = 'LEFT_SQUARE'
TT_RSQUARE = 'RIGHT_SQUARE'
TT_LPAREN = 'LEFT_PAREN'
TT_RPAREN = 'RIGHT_PAREN'
TT_LCURLY = 'LEFT_CURLY'
TT_RCURLY = 'RIGHT_CURLY'
TT_BSLASH = 'BACK_SLASH'
TT_NEWLINE = 'NEWLINE'

# END OF FILE
TT_EOF = 'TT_EOF'

class Token:
    '''Stores the token type and value.'''
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __str__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
    def matches(self, type_, value):
        return self.type == type_ and self.value == value

