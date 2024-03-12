from django.utils import timezone
from compiler.models import Folder

class FolderApi:
    def get(self, id):
        folder = Folder.objects.get(pk=id)
        return folder
    
    def create(self, data):
        parent_id = data['parent_id']
        if (parent_id == 0):
            parent_id = None
        else:
            parent = self.get(parent_id)
            if (parent.enabled == False):
                raise ValueError("Parent folder is disabled.")
        
        folder = Folder(
            name = data['name'],
            description = data.get('description', ''),
            parent_id = parent_id,
            user = data["user"]
        )
        folder.save()
        return folder.id, folder.name, folder.parent_id
    
    def delete(self, id):
        folder = self.get(id)
        folder.enabled = False
        folder.enable_update_date = timezone.now()
        folder.save()
