from django import forms
from compiler.models import Folder


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea({
                "rows": 5
            })
        }
        error_messages = {
            "name": {
                "required": "Folder name must not be empty.",
                "max_length": "Folder name is too long."
            },
            "description": {
                "max_length": "Description is too long."
            }
        }


class FileForm(forms.Form):
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea({"rows": 5})
    )
    source_code_file = forms.FileField(required=True)
