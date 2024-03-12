import subprocess
from pathlib import Path
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from compilator_8_bit.settings import BASE_DIR
from compiler.views import get_source_file, get_dependent_options, dependent_options

STATUS_CODE_OK = 200
STATUS_CODE_REDIRECT = 302
STATUS_CODE_ERROR = 400

f_id = 1

def get_test_user():
    return User.objects.get(pk=1)

class ErrorViewTest(TestCase):
    fixtures = ["user.json"]

    def test_error_not_logged(self):
        url = reverse("error-page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, "/login?next=/error")
    
    def test_error_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("error-page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        self.assertContains(response, "Error happened")

# does not require to be logged in
class LogoutViewTest(TestCase):
    def test_logout(self):
        url = reverse("logout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        self.assertContains(response, "You have been succesfully logged out!")

class ViewFileViewTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json"]

    def test_view_file_not_logged(self):
        url = reverse("file", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/file/{f_id}")
    
    def test_view_file_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("file", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        self.assertContains(response, f'<input type="hidden" id="selected_file" value="{f_id}">')
    
    def test_view_file_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("file", args=(100,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    def test_get_source_file(self):
        file = get_source_file(f_id)
        self.assertEqual(file.id, f_id)
    
class IndexViewTest(TestCase):
    fixtures = ["user.json"]

    def test_index_not_logged(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/")
    
    def test_index_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

class ParseFileViewTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json", "file_timer.json",
                "section_type.json", "section_status.json", "section.json"]

    def test_parse_file_not_logged(self):
        url = reverse("parse-file", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/file/{f_id}/parse")
    
    def test_parse_file_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("parse-file", args=(2,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        self.assertContains(response, f'<input type="hidden" id="selected_file" value="2">')
    
    def test_parse_file_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("parse-file", args=(100,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)

class CreateSectionViewTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json", "file_timer.json",
                "section_type.json", "section_status.json", "section.json"]

    def test_create_section_not_logged(self):
        url = reverse("create-section", args=(f_id, 12, 22, "procedure"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/file/{f_id}/create-section/12/22/procedure")
    
    def test_create_section_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("create-section", args=(f_id, 12, 22, "procedure"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_create_section_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("create-section", args=(100, 12, 22, "procedure"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    def test_create_section_conflict(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("create-section", args=(f_id, 2, 8, "procedure"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)

class AddFolderViewTest(TestCase):
    fixtures = ["user.json", "folder.json"]
    
    def test_add_folder_get_not_logged(self):
        url = reverse("add-folder", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/folder/{f_id}/add-folder")
    
    def test_add_folder_get_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-folder", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_add_folder_post_not_logged(self):
        url = reverse("add-folder", args=(f_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/folder/{f_id}/add-folder")
    
    def test_add_folder_post_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-folder", args=(f_id,))
        response = self.client.post(url, {
            'name': 'name',
            'description': 'description'
        })
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_add_folder_post_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-folder", args=(100,))
        response = self.client.post(url, {
            'name': 'name',
            'description': 'description'
        })
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    # validates form data - name must be present
    def test_add_folder_post_not_valid(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-folder", args=(f_id,))
        response = self.client.post(url, {
            'description': 'description'
        })
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        self.assertContains(response, f'<form method="POST" class="form" action="/folder/{f_id}/add-folder" id="add_folder_form">')
    
class DeleteFolderViewTest(TestCase):
    fixtures = ["user.json", "folder.json"]
    
    def test_delete_folder_get_not_logged(self):
        url = reverse("delete-folder", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/folder/{f_id}/delete")
    
    def test_delete_folder_get_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-folder", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_delete_folder_get_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-folder", args=(100,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    def test_delete_folder_post_not_logged(self):
        url = reverse("delete-folder", args=(f_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/folder/{f_id}/delete")
    
    def test_delete_folder_post_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-folder", args=(f_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    def test_delete_folder_post_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-folder", args=(100,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)

class AddFileViewTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json"]
    
    def test_add_file_get_not_logged(self):
        url = reverse("add-file", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/folder/{f_id}/add-file")
    
    def test_add_file_get_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-file", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_add_file_post_not_logged(self):
        url = reverse("add-file", args=(f_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/folder/{f_id}/add-file")
    
    def test_add_file_post_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-file", args=(f_id,))
        source_code_file = SimpleUploadedFile("source.c", b"file content")
        response = self.client.post(url, {
            'description': 'description',
            'source_code_file': source_code_file
        })
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_add_file_post_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-file", args=(100,))
        source_code_file = SimpleUploadedFile("source.c", b"file content")
        response = self.client.post(url, {
            'description': 'description',
            'source_code_file': source_code_file
        })
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    # validates form data - source code file must be present
    def test_add_file_post_not_valid(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("add-file", args=(f_id,))
        response = self.client.post(url, {
            'description': 'description'
        })
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        self.assertContains(response, f'<form method="POST" enctype="multipart/form-data" class="form" action="/folder/{f_id}/add-file" id="add_file_form">')

class DeleteFileViewTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json"]
    
    def test_delete_file_get_not_logged(self):
        url = reverse("delete-file", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/file/{f_id}/delete")
    
    def test_delete_file_get_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-file", args=(f_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_delete_file_get_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-file", args=(100,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    def test_delete_file_post_not_logged(self):
        url = reverse("delete-file", args=(f_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/file/{f_id}/delete")
    
    def test_delete_file_post_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-file", args=(f_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    def test_delete_file_post_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-file", args=(100,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)

class DeleteSectionViewTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json", "file_timer.json",
                "section_type.json", "section_status.json", "section.json"]
    
    def test_delete_section_get_not_logged(self):
        url = reverse("delete-section", args=(f_id, 5, 8))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/file/{f_id}/delete-section/5/8")
    
    def test_delete_section_get_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-section", args=(f_id, 5, 8))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
    
    def test_delete_section_get_file_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-section", args=(100, 5, 8))
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    def test_delete_section_post_not_logged(self):
        url = reverse("delete-section", args=(f_id, 5, 8))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/file/{f_id}/delete-section/5/8")
    
    def test_delete_section_post_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-section", args=(f_id, 5, 8))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/file/{f_id}/parse")

    def test_delete_section_post_file_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("delete-section", args=(100, 5, 8))
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)

class CompileViewTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json", "file_timer.json",
                "section_type.json", "section_status.json", "section.json"]
    
    def test_compile_post_not_logged(self):
        url = reverse("compile")
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/compile")
    
    # should fail if file, processor or standard are not present
    def test_compile_post_logged_missing_data(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("compile")
        response = self.client.post(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    def test_compile_post_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("compile")
        response = self.client.post(url, {
            "file_id": f_id,
            "command_line_standard": "c11",
            "command_line_processor": "stm8"
        })
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertRegex(response.url, f"^/compile\?id={f_id}&uid=")
        uid = response.url.replace(f"/compile?id={f_id}&uid=", "")
        print(uid)
        # deleting folder
        self.__delete_asm_content()
    
    def test_compile_post_logged_timer(self):
        timer_file_id = 2
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("compile")
        response = self.client.post(url, {
            "file_id": timer_file_id,
            "command_line_standard": "c11",
            "command_line_processor": "stm8"
        })
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertRegex(response.url, f"^/compile\?id={timer_file_id}&uid=")
        uid = response.url.replace(f"/compile?id={timer_file_id}&uid=", "")
        print(uid)
        # deleting folder
        self.__delete_asm_content()
    
    def test_compile_post_logged_not_exist(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("compile")
        response = self.client.post(url, {
            "file_id": 100,
            "command_line_standard": "c11",
            "command_line_processor": "stm8"
        })
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
        self.__delete_asm_content()
    
    def test_compile_get_not_logged(self):
        url = reverse("compile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertEqual(response.url, f"/login?next=/compile")
    
    def test_compile_get_logged_missing_data(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("compile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)
    
    def test_compile_get_logged(self):
        user = get_test_user()
        self.client.force_login(user)
        url = reverse("compile")
        response = self.client.get(f"{url}?id={f_id}&uid=123")
        self.assertEqual(response.status_code, STATUS_CODE_ERROR)

    def __delete_asm_content(self):
        COMPILER_DIR = "asm"
        directory = str(Path(BASE_DIR, COMPILER_DIR))
        command = f"cd {directory} && rm -rf *"
        subprocess.call(command, shell=True)
    
    def test_get_dependent_options(self):
        self.assertEqual(get_dependent_options("mcs51"), dependent_options["mcs51"])
        self.assertEqual(get_dependent_options("ds390"), dependent_options["ds390"])
        self.assertEqual(get_dependent_options("z80"), dependent_options["z80"])
        self.assertEqual(get_dependent_options("sm83"), dependent_options["sm83"])
        self.assertEqual(get_dependent_options("stm8"), dependent_options["stm8"])
