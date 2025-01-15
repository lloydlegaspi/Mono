import re

def is_letter(char):
    return bool(re.match(r'[A-Za-z]', char))

def is_digit(char):
    return bool(re.match(r'\d', char))

def is_space(char):
    return bool(re.match(r'[ \t\n\r\v]', char))

def is_operator(char):
    return bool(re.match(r'[+\-*/~^%=><!&|]', char))

def is_special_symbol(char):
    return bool(re.match(r'[.,?:;()\[\]{}\\\"\'\_]', char))

def is_invalid_symbol(char):
    return bool(re.match(r'[$#@`{}]', char))