from Utils.arrows import *

# Base Error
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += '\n\n' + arrows(self.pos_start.ftext, self.pos_start, self.pos_end)
        return result