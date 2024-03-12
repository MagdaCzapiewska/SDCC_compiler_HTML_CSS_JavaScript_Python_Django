from django.test import TestCase
from compiler.api.folder_tree import FolderTree

class FolderTreeTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json"]

    def test_get_folder_structure(self):
        folder_tree = FolderTree()
        structure = folder_tree.get_folder_structure()

        expected = [
            {'id': 1, 'name': 'Clothing', 'is_file': False, 'children': [
                {'id': 2, 'name': 'Mens', 'is_file': False, 'children': [
                    {'id': 4, 'name': 'Suits', 'is_file': False, 'children': [
                        {'id': 5, 'name': 'Slacks', 'is_file': False, 'children': [], 'has_children': False}, 
                        {'id': 6, 'name': 'Jackets', 'is_file': False, 'children': [], 'has_children': False}], 'has_children': True}], 'has_children': True}, 
                {'id': 3, 'name': 'Womens', 'is_file': False, 'children': [
                    {'id': 7, 'name': 'Dresses', 'is_file': False, 'children': [
                        {'id': 10, 'name': 'Evening', 'is_file': False, 'children': [], 'has_children': False}, 
                        {'id': 11, 'name': 'SunDresses', 'is_file': False, 'children': [], 'has_children': False}, 
                        {'id': 1, 'name': 'just_lines.c', 'is_file': True}], 'has_children': True}, 
                    {'id': 8, 'name': 'Skirts', 'is_file': False, 'children': [], 'has_children': False}, 
                    {'id': 9, 'name': 'Blouses', 'is_file': False, 'children': [], 'has_children': False}], 'has_children': True}], 'has_children': True}]

        self.assertEqual(structure, expected)
    