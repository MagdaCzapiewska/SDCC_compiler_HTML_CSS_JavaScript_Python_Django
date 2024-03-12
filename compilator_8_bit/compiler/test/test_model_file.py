import json
from pathlib import Path
from django.test import TestCase
from django.contrib.auth.models import User
from compiler.api.file import FileApi
from compiler.models import Folder
from compilator_8_bit.settings import BASE_DIR

class FileTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json"]
    file_id = 1

    def test_get(self):
        file_api = FileApi()
        file = file_api.get(self.file_id)
        self.assertEqual(file.id, self.file_id)
        self.assertEqual(file.name, "just_lines.c")
    
    def test_get_source_code(self):
        expected = self.__get_tested_source_code()
        file_api = FileApi()
        source_code = file_api.get_source_code(self.file_id)
        self.assertEqual(source_code, expected)
    
    def test_get_source_code_splitted(self):
        expected = self.__get_tested_source_code().split("\n")
        file_api = FileApi()
        source_code = file_api.get_source_code_splitted(self.file_id)
        self.assertEqual(source_code, expected)
    
    def test_delete(self):
        file_api = FileApi()
        file_api.delete(self.file_id)
        file = file_api.get(self.file_id)
        self.assertEqual(file.enabled, False)
        self.assertIsNotNone(file.enable_update_date)
    
    def test_delete_section(self):
        file_api = FileApi()
        file_api.delete_section(self.file_id, 3, 5)
        source_code = file_api.get_source_code_splitted(self.file_id)
        tested_source_code = self.__get_tested_source_code().split("\n")
        expected = tested_source_code[0:2] + tested_source_code[5:]
        self.assertEqual(source_code, expected)
    
    def test_delete_section_exceeded(self):
        file_api = FileApi()
        file_api.delete_section(self.file_id, 45, 70)
        source_code = file_api.get_source_code_splitted(self.file_id)
        expected = self.__get_tested_source_code().split("\n")[0:44]
        self.assertEqual(source_code, expected)
    
    def test_delete_section_exceeded_fully(self):
        file_api = FileApi()
        file_api.delete_section(self.file_id, 100, 120)
        source_code = file_api.get_source_code_splitted(self.file_id)
        expected = self.__get_tested_source_code().split("\n")
        self.assertEqual(source_code, expected)
    
    # should create a file entry in db
    def test_create(self):
        user = self.__get_test_user()
        data = {
            "folder_id": 1,
            "name": "Test_file.c",
            "user": user,
            "source_code": "line 1"
        }
        file_api = FileApi()
        file_id = file_api.create(data)
        self.assertIsNotNone(file_id)
        file = file_api.get(file_id)
        self.assertEqual(file.folder_id, 1)
        self.assertEqual(file.name, "Test_file.c")
        self.assertEqual(file.source_code, "line 1")
    
    # should raise exception as creating files under disabled folder is not allowed
    def test_create_folder_disabled(self):
        user = self.__get_test_user()
        data = {
            "folder_id": 13,
            "name": "Test_file.c",
            "user": user,
            "source_code": "line 1"
        }
        file_api = FileApi()
        self.assertRaisesMessage(ValueError, "Parent folder is disabled.", file_api.create, data)
    
    # should raise exception as creating files under not existing folder is not allowed
    def test_create_folder_does_not_exist(self):
        user = self.__get_test_user()
        data = {
            "folder_id": 100,
            "name": "Test_file.c",
            "user": user,
            "source_code": "line 1"
        }
        file_api = FileApi()
        self.assertRaises(Folder.DoesNotExist, file_api.create, data)
    
    def test_str(self):
        file_api = FileApi()
        file = file_api.get(self.file_id)
        expected = f"{file.id} {file.name} (folder {file.folder})"
        self.assertEqual(file.__str__(), expected)

    def __get_tested_source_code(self):
        file_path = str(Path(BASE_DIR, "compiler", "fixtures", "file.json"))
        f = open(file_path)
        data = json.load(f)
        return data[0]["fields"]["source_code"]

    def __get_test_user(self):
        return User.objects.get(pk=1)
