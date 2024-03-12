from django.db.models import Q
from compiler.models import Section, SectionType, SectionStatus
from .file import FileApi

class SectionApi:
    def __init__(self, file_id):
        file_api = FileApi()
        self.file = file_api.get(file_id)
        self.source_code = self.file.source_code.split("\n")
        self.total_lines = len(self.source_code)
    
    def get(self):
        return Section.objects.filter(file_id = self.file.id)

    def delete(self):
        sections = self.get()
        sections.delete()
    
    def create(self, data):
        start_line = data.get("start_line", 0)
        end_line = data.get("end_line", 0)

        self.__validate_range(start_line, end_line)

        section_type = SectionType.objects.get(name=data["section_name"])
        section = Section(
            file = self.file,
            start_line = start_line,
            end_line = end_line,
            section_type = section_type,
            name = data.get("name", ""),
            description = data.get("description", ""),
            source_code = (self.source_code)[start_line - 1 : end_line]
        )
        section.save()
    
    def clear_status_data(self):
        sections = self.get()
        for section in sections:
            section.section_status_id = None
            section.status_data = ""
            section.save()
    
    def update_status_data(self, status, data):
        section_status = self.__get_section_status_instance(status)
        line_id = data["line_id"]
        line_content = data["line_content"]
        sections = self.get().filter(start_line__lte=line_id,
                                          end_line__gte=line_id)
        for section in sections:
            section.section_status = section_status
            section.status_data += line_content + ","
            section.save()

    def update_status(self, status):
        section_status = self.__get_section_status_instance(status)
        sections = self.get().filter(section_status_id__isnull = True)
        for section in sections:
            section.section_status = section_status
            section.save()
    
    def get_source_code_enriched(self, source_code):
        sections = self.get()

        data = []
        for counter, line in enumerate(source_code, start=1):
            start_line = 0
            end_line = 0
            end_div = False
            section_type = ""
            section_status = ""
            class_name = ""
            section = next(filter(lambda el: el.start_line == counter, sections), None)
            if section:
                start_line = section.start_line
                end_line = section.end_line
                section_type = section.section_type.name
                if section.section_status:
                    section_status = section.section_status.name
                section = next(filter(lambda el: el.start_line < section.start_line and el.end_line > section.end_line, sections), None)
                if section:
                    class_name = "code-section-inner"
                else:
                    class_name = "code-section-outer"
            section = next(filter(lambda el: el.end_line == counter, sections), None)
            if section:
                end_div = True
            
            data.append({
                "line": line,
                "start_line": start_line,
                "end_line": end_line,
                "end_div": end_div,
                "section_type": section_type,
                "section_status": section_status,
                "class_name": class_name
            })
        return data
    
    def delete_section(self, start, end):
        section = self.get().filter(start_line = start, end_line = end)
        section.delete()

    def __get_section_status_instance(self, status):
        return SectionStatus.objects.get(name=status)
    
    def __validate_range(self, start, end):
        if start <= 0 or end <=0 or start > end or start > self.total_lines or end > self.total_lines:
            raise ValueError("Start and end line values are wrong!")
        
        if self.get().filter(Q(start_line__gt=start, end_line__gt=end, start_line__lte=end) | Q(start_line__lt=start, end_line__lt=end, end_line__gte=start) | Q(start_line=start) | Q(end_line=end)).exists():
            raise ValueError('Section conflict detected')
