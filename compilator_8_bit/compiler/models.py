from django.db import models
from django.contrib.auth.models import User


class Folder(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    enabled = models.BooleanField(null=False, default=True)
    enable_update_date = models.DateTimeField(null=True)
    update_date = models.DateTimeField(auto_now=True)
    parent_id = models.IntegerField(null=True, db_index=True)

    def __str__(self):
        return f"{self.id} {self.name} (parent_id {self.parent_id})"


class File(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    enabled = models.BooleanField(null=False, default=True)
    enable_update_date = models.DateTimeField(null=True)
    update_date = models.DateTimeField(auto_now=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, db_index=True)
    source_code = models.TextField()

    def __str__(self):
        return f"{self.id} {self.name} (folder {self.folder})"

class SectionType(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True)

class SectionStatus(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True)

class Section(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, db_index=True)
    start_line = models.IntegerField(null=False)
    end_line = models.IntegerField(null=False)
    section_type = models.ForeignKey(SectionType, on_delete=models.CASCADE, db_index=True)
    section_status = models.ForeignKey(SectionStatus, on_delete=models.CASCADE, db_index=True, null=True)
    status_data = models.TextField()
    source_code = models.TextField()

    def __str__(self):
        return f"{self.id}, file: {self.file.name}, {self.file.id} (lines {self.start_line} - {self.end_line}), {self.section_type.name}"
