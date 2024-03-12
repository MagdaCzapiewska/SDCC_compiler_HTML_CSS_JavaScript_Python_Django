from django.test import TestCase
from django.contrib.auth.models import User
from compiler.api.folder import FolderApi
from compiler.models import Folder

class FolderTest(TestCase):
    fixtures = ["user.json", "folder.json"]
    folder_id = 1

    def test_get(self):
        folder_api = FolderApi()
        folder = folder_api.get(self.folder_id)
        self.assertEqual(folder.name, "Clothing")
    
    def test_delete(self):
        folder_api = FolderApi()
        folder_api.delete(self.folder_id)
        folder = folder_api.get(self.folder_id)
        self.assertEqual(folder.enabled, False)
        self.assertIsNotNone(folder.enable_update_date)
    
    # should create root level folder (parent_id is Null)
    def test_create_no_parent(self):
        user = self.__get_test_user()
        data = {
            "parent_id": 0,
            "name": "Root_folder",
            "user": user
        }
        folder_api = FolderApi()
        folder_id, folder_name, parent_id = folder_api.create(data)
        self.assertIsNone(parent_id)
        self.assertEqual(folder_name, "Root_folder")
    
    # should create folder referencing passed parent_id
    def test_create_with_parent(self):
        user = self.__get_test_user()
        data = {
            "parent_id": self.folder_id,
            "name": "Underroot_folder",
            "user": user
        }
        folder_api = FolderApi()
        folder_id, folder_name, parent_id = folder_api.create(data)
        self.assertEqual(parent_id, self.folder_id)
        self.assertEqual(folder_name, "Underroot_folder")
        folder = folder_api.get(folder_id)
        self.assertEqual(folder.description, "")
    
    # should create folder referencing passed parent_id
    def test_create_with_parent_and_description(self):
        user = self.__get_test_user()
        data = {
            "parent_id": self.folder_id,
            "name": "Under_root_folder",
            "user": user,
            "description": "Example description"
        }
        folder_api = FolderApi()
        folder_id, folder_name, parent_id = folder_api.create(data)
        self.assertEqual(parent_id, self.folder_id)
        self.assertEqual(folder_name, "Under_root_folder")
        folder = folder_api.get(folder_id)
        self.assertEqual(folder.description, "Example description")
    
    # should raise exception as creating folders under disabled parent is not allowed
    def test_create_with_disabled_parent(self):
        user = self.__get_test_user()
        data = {
            "parent_id": 13,
            "name": "Under_disabled_folder",
            "user": user
        }
        folder_api = FolderApi()
        self.assertRaisesMessage(ValueError, "Parent folder is disabled.", folder_api.create, data)

    # should raise exception as creating folder under not existing parent is not allowed
    def test_create_with_non_existing_parent(self):
        user = self.__get_test_user()
        data = {
            "parent_id": 100,
            "name": "Under_not_existing_folder",
            "user": user
        }
        folder_api = FolderApi()
        self.assertRaises(Folder.DoesNotExist, folder_api.create, data)
    
    def test_str(self):
        folder_api = FolderApi()
        folder = folder_api.get(self.folder_id)
        expected = f"{folder.id} {folder.name} (parent_id {folder.parent_id})"
        self.assertEqual(folder.__str__(), expected)
    
    def __get_test_user(self):
        return User.objects.get(pk=1)