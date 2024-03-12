import re
from compiler.models import File

DIRECTIVE = "directive"
VARIABLE = "variable"
PROCEDURE = "procedure"
COMMENT = "comment"
ASSEMBLY = "assembly"

regex_patterns = {
    "ifdefine": "^#(if|ifdef|if defined|ifndef|if !defined)",
    "enddefine": "^#endif",
    "directive": "^#(define|include|pragma|error|warning|undef|line)",
    "line_comment": "^//",
    "block_line_comment": "^/\*(.*)\*/$",
    "block_comment": "^/\*",
    "end_block_comment": "\*/$",
    "procedure": "^(char|unsigned char|signed char|int|unsigned int|short|unsigned short|long|unsigned long|unsigned long long|float|double|long double|uint8_t|uint16_t|uint32_t|uint64_t|void)\s+\w+\s*\(",
    "variable": "^(char|unsigned char|signed char|int|unsigned int|short|unsigned short|long|unsigned long|unsigned long long|float|double|long double|uint8_t|uint16_t|uint32_t|uint64_t|void)\s+\w+\s*(=|[^\(])",
    "asm": "^(asm|__asm__)\s*(volatile|__volatile__)?\s*[\{]",
    "asm_round": "^(asm|__asm__)\s*(volatile|__volatile__)?\s*[\(]",
    "asm_floor_start": "^__asm",
    "asm_floor_end": "^__endasm\s*;"
}

class Parser:

    def __init__(self, lines, counter_start):
        self.lines = lines
        self.counter_start = counter_start
        self.counter = counter_start
        self.line_exists = True
        self.data = []
        self.section_name = None
        self.start_line = None
        self.end_line = None

    def __parse_line(self, line):
        for key, rx in regex_patterns.items():
            match = re.search(rx, line.strip())
            if match:
                return key, match
        return None, None
    
    def __append_data(self):
        self.data.append({
            "section_name": self.section_name,
            "start_line": self.start_line,
            "end_line": self.end_line
        })

    def __count_brackets(self, match, bracket_type):
        brackets = 0
        for bracket in match:
            if bracket == bracket_type:
                brackets+=1
            else:
                brackets-=1
        return brackets

    def parse_source_code(self):
        self.counter = self.counter_start
        iterator = iter(self.lines)

        line = next(iterator)
        self.counter += 1

        while self.line_exists:
            key, match = self.__parse_line(line)

            if key == "ifdefine":
                self.start_line = self.counter
                self.section_name = DIRECTIVE
                while key != "enddefine":
                    line = next(iterator)
                    self.counter += 1
                    key, match = self.__parse_line(line)
                self.end_line = self.counter
                self.__append_data()

            if key in [DIRECTIVE, VARIABLE]:
                self.start_line = self.counter
                self.section_name = key
                prev_key = key
                while key == prev_key:
                    line = next(iterator)
                    self.counter += 1
                    key, match = self.__parse_line(line)
                self.end_line = self.counter - 1
                self.__append_data()
                continue

            if key == "line_comment":
                self.start_line = self.counter
                self.section_name = COMMENT
                while key == "line_comment":
                    line = next(iterator)
                    self.counter += 1
                    key, match = self.__parse_line(line)
                self.end_line = self.counter - 1
                self.__append_data()
                continue

            if key == "block_line_comment":
                self.start_line = self.counter
                self.section_name = COMMENT
                self.end_line = self.counter
                self.__append_data()
            
            if key == "block_comment":
                self.start_line = self.counter
                self.section_name = COMMENT
                while key != "end_block_comment":
                    line = next(iterator)
                    self.counter += 1
                    key, match = self.__parse_line(line)
                self.end_line = self.counter
                self.__append_data()
            
            if key in [PROCEDURE, ASSEMBLY]:
                self.start_line = self.counter
                self.section_name = key
                brackets = 0
                match = re.findall("[\{\}]", line)
                if len(match):
                    brackets += self.__count_brackets(match, "{")
                else:
                    while len(match) == 0:
                        line = next(iterator)
                        self.counter += 1
                        match = re.findall("[\{\}]", line)
                    brackets += self.__count_brackets(match, "{")

                while brackets > 0:
                    line = next(iterator)
                    self.counter += 1
                    match = re.findall("[\{\}]", line)
                    brackets += self.__count_brackets(match, "{")

                self.end_line = self.counter
                self.__append_data()
            
            if key == "asm_round":
                self.start_line = self.counter
                self.section_name = ASSEMBLY
                brackets = 0
                match = re.findall("[\(\)]", line)
                if len(match):
                    brackets += self.__count_brackets(match, "(")
                else:
                    while len(match) == 0:
                        line = next(iterator)
                        self.counter += 1
                        match = re.findall("[\(\)]", line)
                    brackets += self.__count_brackets(match, "(")

                while brackets > 0:
                    line = next(iterator)
                    self.counter += 1
                    match = re.findall("[\(\)]", line)
                    brackets += self.__count_brackets(match, "(")

                self.end_line = self.counter
                self.__append_data()
            
            if key == "asm_floor_start":
                self.start_line = self.counter
                self.section_name = ASSEMBLY
                while key != "asm_floor_end":
                    line = next(iterator)
                    self.counter += 1
                    key, match = self.__parse_line(line)
                self.end_line = self.counter
                self.__append_data()

            try:
                line = next(iterator)
                self.counter += 1
            except:
                self.line_exists = False
        
        for section in self.data:
            print(section)
        return self.data