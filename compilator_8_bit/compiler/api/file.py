from django.utils import timezone
from compiler.models import File
from .folder import FolderApi

class FileApi:
    def get(self, id):
        file = File.objects.get(pk=id)
        return file
    
    def get_source_code(self, id):
        file = self.get(id)
        return file.source_code
    
    def get_source_code_splitted(self, id):
        source_code = self.get_source_code(id)
        return source_code.split("\n")
    
    def create(self, data):
        folder_api = FolderApi()
        folder = folder_api.get(data["folder_id"])
        if (folder.enabled==False):
            raise ValueError("Parent folder is disabled.")

        file = File(
            name = data["name"],
            description = data.get("description", ""),
            folder = folder,
            user = data["user"],
            source_code = data["source_code"]
        )
        file.save()
        return file.id
    
    def delete(self, id):
        file = self.get(id)
        file.enabled = False
        file.enable_update_date = timezone.now()
        file.save()

    def delete_section(self, id, start_line, end_line):
        file = self.get(id)
        splitted = file.source_code.split("\n")
        del splitted[start_line - 1 : end_line]
        file.source_code = '\n'.join(splitted)
        file.save()
