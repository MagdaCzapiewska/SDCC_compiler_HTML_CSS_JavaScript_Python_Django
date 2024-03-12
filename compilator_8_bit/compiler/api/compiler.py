import uuid
import subprocess
import re
from pathlib import Path
from django.core.files.storage import FileSystemStorage
from compilator_8_bit.settings import BASE_DIR
from .file import FileApi

COMPILER_DIR = "asm"


class Compiler:

    file_name = "source"
    file_ext = ".c"
    asm_ext = ".asm"

    def __init__(self, *args):
        if len(args) == 5:
            self.file_id = args[0]
            self.standard = args[1]
            self.processor = args[2]
            self.optimizations = args[3]
            self.dependent = args[4]
            self.uid = str(uuid.uuid1())
            self.can_compile = True
        else:
            self.uid = args[0]
            self.can_compile = False

    def compile(self):
        if self.can_compile == False:
            raise TypeError("Initialize compiler properly!")
        
        print("Kompiluję")
        print(self.file_id)
        print(self.standard)
        print(self.processor)
        print(self.optimizations)
        print(self.dependent)
        print("Koniec zmiennych")
        self.__create_directory()
        self.__create_source_code_file()
        self.__compile()
        return self.uid
    
    def get_compilation_statuses(self):
        file_name = self.file_name + ".stderr"
        error_body = self.__get_asm(file_name)
        error_lines = error_body.split(self.file_name + self.file_ext + ":")[1:]

        data = []
        for error in error_lines:
            match = re.search("^\d+", error)
            if match:
                data.append({
                    "line_id": match.group(0),
                    "line_content": error
                })
        status = "Compiled without warnings"
        if self.__check_asm_exists():
            if len(data):
                status = "Compiled with warnings"
        else:
            status = "Does not compile"
        return status, data
    
    def get_and_delete_asm(self):
        try:
            file_name = self.file_name + self.asm_ext
            asm_body = self.__get_asm(file_name)
            self.__delete_directory()
            enriched = self.__enrich_asm(asm_body.split("\n"))
            return True, enriched
        except:
            file_name = self.file_name + ".stderr"
            error_body = self.__get_asm(file_name)
            self.__delete_directory()
            enriched = self.__enrich_error(error_body.split("\n"))
            return False, enriched

    def __create_directory(self):
        directory = str(Path(BASE_DIR, COMPILER_DIR))
        command = "cd " + directory + " && mkdir " + self.uid
        subprocess.call(command, shell=True)

    def __create_source_code_file(self):
        file_api = FileApi()
        source_code = file_api.get_source_code(self.file_id)
        file_name = self.file_name + self.file_ext
        file = str(Path(BASE_DIR, COMPILER_DIR, self.uid, file_name))
        with open(file, "w+") as destination:
            destination.write(source_code)

    def __compile(self):
        directory = str(Path(BASE_DIR, COMPILER_DIR, self.uid))
        file_name = self.file_name
        options = self.__get_options()
        command = "cd " + directory + " && sdcc -S " + options + " " + file_name + \
            self.file_ext + " 1>" + file_name + ".stdout 2>" + file_name + ".stderr"
        print(command)
        subprocess.call(command, shell=True)

    def __get_options(self):
        optimizations = ""
        dependent = ""

        for optimization in self.optimizations:
            optimizations += " --" + optimization

        for dep in self.dependent:
            dependent += " --" + dep

        return "--std-" + self.standard + " -m" + self.processor + optimizations + dependent
    
    def __get_asm(self, file_name):
        file = str(Path(BASE_DIR, COMPILER_DIR, self.uid, file_name))
        fs = FileSystemStorage()

        file_body = fs.open(file).read().decode("utf-8")
        return file_body
    
    def __check_asm_exists(self):
        file_name = self.file_name + self.asm_ext
        file = str(Path(BASE_DIR, COMPILER_DIR, self.uid, file_name))
        fs = FileSystemStorage()
        return fs.exists(file)
    
    def __enrich_asm(self, lines):
        class_header = "asm-header"
        class_body = "asm-body"
        file_name = self.file_name + self.file_ext
        regex =  "^;\t*\s*" + file_name + ":\s*\d+"
        regex_repl = ";\t*\s*" + file_name + ":\s*"

        is_body = True
        data = []
        for line in lines:
            source_code_line = 0
            if is_body == True and line.startswith(";-----------------"):
                data.append({"code": line, "start": True, "start_class": class_header, "position": "before", "source_code_line": source_code_line})
                is_body = False
            elif is_body == False and line.startswith(";-----------------"):
                data.append({"code": line, "start": True, "start_class": class_body, "position": "after", "source_code_line": source_code_line})
                is_body = True
            elif is_body == False and line.startswith(";"):
                data.append({"code": line, "start": False, "source_code_line": source_code_line})
            elif is_body == True and line.startswith(";"):
                match = re.search(regex, line)
                if match:
                    source_code_line = int(re.sub(regex_repl, "", match.group(0)))
                data.append({"code": line, "start": False, "source_code_line": source_code_line})
            else:
                data.append({"code": line, "start": False, "source_code_line": source_code_line})
        return data
    
    def __enrich_error(self, lines):
        file_name = self.file_name + self.file_ext
        regex =  "^" + file_name + ":\d+"
        regex_repl = file_name + ":"

        data = []
        for line in lines:
            source_code_line = 0
            match = re.search(regex, line)
            if match:
                source_code_line = int(re.sub(regex_repl, "", match.group(0)))
            data.append({
                "line_content": line,
                "source_code_line": source_code_line
            })
        return data

    def __delete_directory(self):
        directory = str(Path(BASE_DIR, COMPILER_DIR))
        command = "cd " + directory + " && rm -rf " + self.uid
        subprocess.call(command, shell=True)

