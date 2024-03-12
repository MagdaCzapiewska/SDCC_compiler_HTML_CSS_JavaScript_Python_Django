import re
from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from compiler.api.folder_tree import FolderTree
from compiler.api.file import FileApi
from compiler.api.folder import FolderApi
from compiler.api.compiler import Compiler
from compiler.api.parser import Parser
from compiler.api.section import SectionApi
from .forms import FolderForm, FileForm

# Create your views here.

def get_source_file(id):
    file_api = FileApi()
    return file_api.get(id)

def get_source_code_splitted(id):
    file_api = FileApi()
    return file_api.get_source_code_splitted(id)

def get_source_code_enriched(id):
    source_code = get_source_code_splitted(id)
    section_api = SectionApi(id)
    return section_api.get_source_code_enriched(source_code)

def get_folder_structure():
    folder_tree = FolderTree()
    return folder_tree.get_folder_structure()

command_line_options = {
    "standard": ["", "c89", "sdcc89", "c95", "c99", "sdcc99", "c11", "sdcc11", "c2x", "sdcc2x"],
    "optimization": ["noloopreverse", "nolabelopt", "no-xinit-opt", "nooverlay", "no-peep", "peep-return", "no-peep-return", "opt-code-speed", "opt-code-size", "fomit-frame-pointer", "nolospre", "nostdlibcall"],
    "processor": ["", "mcs51", "ds390", "ds400", "z80", "z180", "r2k", "r3ka", "sm83", "tlcs90", "ez80_z80", "stm8"]
}

dependent_options = {
    "mcs51": ["model-small", "model-medium", "model-large", "model-huge"],
    "ds390": ["model-flat24", "protect-sp-update", "stack-10bit", "stack-probe", "use-accelerator"],
    "z80": ["no-std-crt0", "callee-saves-bc", "reserve-regs-iy", "fno-omit-frame-pointer"],
    "sm83": ["no-std-crt0", "callee-saves-bc"],
    "stm8": ["model-medium", "model-large"]
}

def get_dependent_options(processor):
    if processor == "mcs51":
        return dependent_options[processor]
    elif processor in ["ds390", "ds400"]:
        return dependent_options["ds390"]
    elif processor in ["z80", "z180", "r2k", "r3ka", "tlcs90", "ez80_z80"]:
        return dependent_options["z80"]
    elif processor == "sm83":
        return dependent_options[processor]
    elif processor == "stm8":
        return dependent_options[processor]

@login_required
def index(request):
    print("User: ", request.user)
    folder_structure = get_folder_structure()
    return render(request, 'compiler/index.html', {
        'folder_structure': folder_structure,
        'command_line_options': command_line_options
    })

@login_required
def view_file(request, id):
    folder_structure = get_folder_structure()
    
    try:
        source_code = get_source_code_enriched(id)
        return render(request, 'compiler/main_code.html', {
            'folder_structure': folder_structure,
            'command_line_options': command_line_options,
            'source_code': source_code,
            'file_id': id
        })
    except:
        # return HttpResponseRedirect(reverse('error-page'))
        return render(request, 'compiler/error.html', status=400)

@login_required
def parse_file(request, id):
    try:
        source_code = get_source_code_splitted(id)
        parser = Parser(source_code, 0)
        parsed_data = parser.parse_source_code()

        for section in parsed_data:
            if section["section_name"] == "procedure":
                start_line = section["start_line"]
                end_line = section["end_line"]
                if start_line != end_line:
                    lines = source_code[start_line : end_line]
                    parser = Parser(lines, start_line)
                    subsection_data = parser.parse_source_code()
                    if len(subsection_data):
                        parsed_data.extend(subsection_data)

        section_api = SectionApi(id)
        section_api.delete()
        for section in parsed_data:
            section_api.create(section)

        # folder_structure = get_folder_structure()
        source_code = get_source_code_enriched(id)

        # return render(request, 'compiler/parser_result.html', {
        #     'folder_structure': folder_structure,
        #     'command_line_options': command_line_options,
        #     'source_code': source_code,
        #     'file_id': id,
        #     'parsed_data': parsed_data
        # })

        return render(request, 'compiler/main_code.html', {
            'source_code': source_code,
            'file_id': id
        })
    except:
        # return HttpResponseRedirect(reverse('error-page'))
        return render(request, 'compiler/error.html', status=400)

@login_required
def create_section(request, id, start_line, end_line, section_name):

    data = {
        "start_line": start_line,
        "end_line": end_line,
        "section_name": section_name
    }
    try:
        section_api = SectionApi(id)
        section_api.create(data)
    
        # folder_structure = get_folder_structure()
        source_code = get_source_code_enriched(id)
        return render(request, 'compiler/main_code.html', {
            # 'folder_structure': folder_structure,
            # 'command_line_options': command_line_options,
            'source_code': source_code,
            'file_id': id
        })
    except:
        # return HttpResponseRedirect(reverse('error-page'))
        return render(request, 'compiler/error.html', status=400)

@login_required
def error(request):
    return render(request, 'compiler/error.html')

def logout_view(request):
    logout(request)
    return render(request, 'compiler/logout.html')
    
class AddFolder(View):
    def get(self, request, id):
        form = FolderForm()
        return render(request, 'compiler/folder_add.html', {
            'form': form,
            'id': id
        })
    
    def post(self, request, id):
        form = FolderForm(request.POST)
        if (form.is_valid()):
            data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'parent_id': id,
                'user': request.user
            }

            try:
                folder_api = FolderApi()
                folder_id, name, parent_id = folder_api.create(data)
                data = {
                    "folder_id": folder_id,
                    "name": name,
                    "parent_id": parent_id
                }
                return JsonResponse(data)
            except:
                # return HttpResponseRedirect(reverse('error-page'))
                return render(request, 'compiler/error.html', status=400)

        else:
            return render(request, 'compiler/folder_add.html', {
                'form': form,
                'id': id
            })

class DeleteFolder(View):
    def get(self, request, id):
        try:
            folder_api = FolderApi()
            folder = folder_api.get(id)
            return render(request, 'compiler/delete.html', {
                'object': folder,
                'action': "/folder/" + str(id) + "/delete",
                'onclick': "submitDeleteFolder();"
            })
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)

    def post(self, request, id):
        try:
            folder_api = FolderApi()
            folder_api.delete(id)
            data = {
                "folder_id": id
            }
            return JsonResponse(data)
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)
        
class AddFile(View):
    def get(self, request, id):
        form = FileForm()
        return render(request, 'compiler/file_add.html', {
            'form': form,
            'id': id
        })
    
    def post(self, request, id):
        form = FileForm(request.POST, request.FILES)
        if (form.is_valid()):
            uploaded_file = request.FILES["source_code_file"]
            source_code = uploaded_file.read().decode("utf-8")
            source_code = re.sub("\n$", "", source_code, 1)
            print(uploaded_file)
            data = {
                'name': uploaded_file.name,
                'description': form.cleaned_data['description'],
                'folder_id': id,
                'source_code': source_code,
                'user': request.user
            }

            try:
                file_api = FileApi()
                file_id = file_api.create(data)
                data = {
                    "file_id": file_id,
                    "name": uploaded_file.name,
                    "folder_id": id
                }
                return JsonResponse(data)
            except:
                # return HttpResponseRedirect(reverse('error-page'))
                return render(request, 'compiler/error.html', status=400)

        else:
            return render(request, 'compiler/file_add.html', {
                'form': form,
                'id': id
            })

class DeleteFile(View):
    def get(self, request, id):
        try:
            file_api = FileApi()
            file = file_api.get(id)
            return render(request, 'compiler/delete.html', {
                'object': file,
                'action': "/file/" + str(id) + "/delete",
                'onclick': "submitDeleteFile();"
            })
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)

    def post(self, request, id):
        try:
            file_api = FileApi()
            file_api.delete(id)
            data = {
                "file_id": id
            }
            return JsonResponse(data)
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)

class DeleteSection(View):
    def get(self, request, id, start_line, end_line):
        try:
            file_api = FileApi()
            file = file_api.get(id)

            object = {
                "name": file.name,
                "lines": str(start_line) + "-" + str(end_line)
            }
            return render(request, 'compiler/delete.html', {
                'object': object,
                'action': "/file/" + str(id) + "/delete-section/" +
                    str(start_line) + "/" + str(end_line),
                'onclick': "submitDeleteSection();"
            })
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)

    def post(self, request, id, start_line, end_line):
        try:
            section_api = SectionApi(id)
            section_api.delete_section(start_line, end_line)

            file_api = FileApi()
            file_api.delete_section(id, start_line, end_line)
            print(start_line)
            print(end_line)
            return HttpResponseRedirect(reverse('parse-file', args=(id,)))
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)

class Compile(View):
    def post(self, request):
        print(request.POST)
        file_id = request.POST.get("file_id", None)
        standard = request.POST.get("command_line_standard", None)
        optimizations = request.POST.getlist("command_line_optimization")
        processor = request.POST.get("command_line_processor", None)
        dependent = request.POST.getlist("command_line_dependent")

        if file_id == None or standard == None or processor == None:
            return render(request, 'compiler/error.html', status=400)

        request.session["standard"] = standard
        request.session["optimizations"] = optimizations
        request.session["processor"] = processor
        request.session["dependent"] = dependent
        request.session["dependent_options"] = get_dependent_options(processor)

        try:
            compiler = Compiler(file_id, standard, processor, optimizations, dependent)
            uid = compiler.compile()
            status, error_lines = compiler.get_compilation_statuses()
            print(status)
            print(error_lines)
            section_api = SectionApi(file_id)
            section_api.clear_status_data()

            for line in error_lines:
                section_api.update_status_data(status, line)
            if status == "Compiled with warnings":
                status = "Compiled without warnings"
            section_api.update_status(status)

            return HttpResponseRedirect(reverse('compile') + "?id=" + file_id + "&uid=" + uid)
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)
    
    def get(self, request):
        file_id = request.GET.get("id", None)
        uid = request.GET.get("uid", None)

        if file_id == None or uid == None:
            return render(request, 'compiler/error.html', status=400)

        compiler = Compiler(uid)

        try:
            result, asm_code = compiler.get_and_delete_asm()
            print(asm_code)

            # folder_structure = get_folder_structure()
            source_file = get_source_file(file_id)
            source_code = get_source_code_enriched(file_id)
            asm_name = (source_file.name)[:-2] + ".asm"

            if result:
                return render(request, 'compiler/compiled.html', {
                    # 'folder_structure': folder_structure,
                    # 'command_line_options': command_line_options,
                    'source_code': source_code,
                    'file_id': file_id,
                    'asm_code': asm_code,
                    'asm_name': asm_name
                })
            else:
                return render(request, 'compiler/compilation_error.html', {
                    # 'folder_structure': folder_structure,
                    # 'command_line_options': command_line_options,
                    'source_code': source_code,
                    'file_id': file_id,
                    'error_code': asm_code
                })
        
        except:
            # return HttpResponseRedirect(reverse('error-page'))
            return render(request, 'compiler/error.html', status=400)
