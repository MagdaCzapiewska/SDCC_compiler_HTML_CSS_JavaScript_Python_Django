from django.contrib import admin

# Register your models here.
from .models import SectionType, SectionStatus, Section

admin.site.register(SectionType)
admin.site.register(SectionStatus)
admin.site.register(Section)
