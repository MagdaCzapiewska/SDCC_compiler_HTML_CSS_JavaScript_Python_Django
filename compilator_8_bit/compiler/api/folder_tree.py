from compiler.models import Folder, File


class FolderTree:
    def __init__(self):
        self.folders = Folder.objects.all()
        self.files = File.objects.all()

    def get_folder_structure(self):
        roots = self.__find_roots()
        tree = self.__traverse_siblings(roots)
        return tree

    def __find_roots(self):
        roots = []
        root_folders = self.folders.filter(
            parent_id__isnull=True, enabled=True)
        for elem in root_folders:
            root = {
                'id': elem.id,
                'name': elem.name,
                'is_file': False
            }
            roots.append(root)
        return roots

    def __traverse_siblings(self, siblings):
        for elem in siblings:
            children = []
            child_folders = self.folders.filter(
                parent_id=elem['id'], enabled=True)
            for child_folder in child_folders:
                child = {
                    'id': child_folder.id,
                    'name': child_folder.name,
                    'is_file': False
                }
                children.append(child)
            elem['children'] = children
            if (len(children)):
                self.__traverse_siblings(elem['children'])

            child_files = self.files.filter(folder_id=elem['id'], enabled=True)
            for child_file in child_files:
                child = {
                    'id': child_file.id,
                    'name': child_file.name,
                    'is_file': True
                }
                elem['children'].append(child)

            elem['has_children'] = (len(elem['children']) > 0)
        return siblings
