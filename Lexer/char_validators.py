def found_char():
    return True

def not_found_char():
    return False

alpha_dict = {
    "a":found_char,
    "b":found_char,
    "c":found_char,
    "d":found_char,
    "e":found_char,
    "f":found_char,
    "g":found_char,
    "h":found_char,
    "i":found_char,
    "j":found_char,
    "k":found_char,
    "l":found_char,
    "m":found_char,
    "n":found_char,
    "o":found_char,
    "p":found_char,
    "q":found_char,
    "r":found_char,
    "s":found_char,
    "t":found_char,
    "u":found_char,
    "v":found_char,
    "w":found_char,
    "x":found_char,
    "y":found_char,
    "z":found_char,
    "A":found_char,
    "B":found_char,
    "C":found_char,
    "D":found_char,
    "E":found_char,
    "F":found_char,
    "G":found_char,
    "H":found_char,
    "I":found_char,
    "J":found_char,
    "K":found_char,
    "L":found_char,
    "M":found_char,
    "N":found_char,
    "O":found_char,
    "P":found_char,
    "Q":found_char,
    "R":found_char,
    "S":found_char,
    "T":found_char,
    "U":found_char,
    "V":found_char,
    "W":found_char,
    "X":found_char,
    "Y":found_char,
    "Z":found_char
}

digits_dict = {
    "0":found_char,
    "1":found_char,
    "2":found_char,
    "3":found_char,
    "4":found_char,
    "5":found_char,
    "6":found_char,
    "7":found_char,
    "8":found_char,
    "9":found_char
}

whitespaces_dict = {
    "":found_char,
    " ":found_char,
    "\t":found_char,
    "\v":found_char,
    "\r":found_char
}

operators_dict = {
    "+":found_char,
    "-":found_char,
    "*":found_char,
    "/":found_char,
    "~":found_char,
    "^":found_char,
    "%":found_char,
    "=":found_char,
    ">":found_char,
    "<":found_char,
    "!":found_char,
    "&":found_char,
    "|":found_char
}

special_symbol_dict = {
    ".":found_char,
    ",":found_char,
    "?":found_char,
    ":":found_char,
    ";":found_char,
    "(":found_char,
    ")":found_char,
    "[":found_char,
    "]":found_char,
    "\\":found_char,
    '"':found_char,
    "'":found_char,
    "_":found_char,
    "\n":found_char
}

invalid_symbols_dict = {
    "$":found_char,
    "#":found_char,
    "@":found_char,
    "":found_char,
    "}":found_char,
    "{":found_char
}

escape_chars_dict = {
    "n": "\n",
    "t": "\t",
    '"': '"',
    "\\": "\\"
}

def is_letter(char):
    func = alpha_dict.get(char, not_found_char)
    return func()

def is_digit(char):
    func = digits_dict.get(char, not_found_char)
    return func()

def is_space(char):
    func = whitespaces_dict.get(char, not_found_char)
    return func()

def is_operator(char):
    func = operators_dict.get(char, not_found_char)
    return func()

def is_special_symbol(char):
    func = special_symbol_dict.get(char, not_found_char)
    return func()

def is_invalid_symbol(char):
    func = invalid_symbols_dict.get(char, not_found_char)
    return func()

def is_in_char_set(char):
    func1 = alpha_dict.get(char, not_found_char)
    func2 = digits_dict.get(char, not_found_char)
    func3 = whitespaces_dict.get(char, not_found_char)
    func4 = operators_dict.get(char, not_found_char)
    func5 = special_symbol_dict.get(char, not_found_char)
    
    if func1():
        return func1()
    elif func2():
        return func2()
    elif func3():
        return func3()
    elif func4():
        return func4()
    elif func5():
        return func5()
    else:
        return False