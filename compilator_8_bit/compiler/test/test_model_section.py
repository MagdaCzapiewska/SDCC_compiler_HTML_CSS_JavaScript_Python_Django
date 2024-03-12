from django.test import TestCase
from compiler.api.section import SectionApi
from compiler.api.file import FileApi

class SectionTest(TestCase):
    fixtures = ["user.json", "folder.json", "file.json", "file_timer.json",
                "section.json", "section_type.json", "section_status.json"]
    file_id = 1

    def test_get(self):
        section_api = SectionApi(self.file_id)
        sections = section_api.get()
        self.assertEqual(len(sections), 7)

    def test_delete(self):
        section_api = SectionApi(self.file_id)
        section_api.delete()
        sections = section_api.get()
        self.assertEqual(len(sections), 0)
        section_api = SectionApi(2)
        sections = section_api.get()
        self.assertEqual(len(sections), 1)
    
    def test_create(self):
        data = {
            "start_line": 12,
            "end_line": 22,
            "section_name": "procedure" 
        }
        section_api = SectionApi(self.file_id)
        section_api.create(data)
        sections = section_api.get()
        self.assertEqual(len(sections), 8)
    
    def test_create_inner(self):
        data = {
            "start_line": 36,
            "end_line": 37,
            "section_name": "directive"
        }
        section_api = SectionApi(self.file_id)
        section_api.create(data)
        sections = section_api.get()
        self.assertEqual(len(sections), 8)
    
    def test_create_outer(self):
        data = {
            "start_line": 39,
            "end_line": 45,
            "section_name": "comment" 
        }
        section_api = SectionApi(self.file_id)
        section_api.create(data)
        sections = section_api.get()
        self.assertEqual(len(sections), 8)
    
    # should raise exception if start<0 or end<0
    def test_create_fail_1(self):
        data = {
            "start_line": -22,
            "end_line": -12,
            "section_name": "comment" 
        }
        section_api = SectionApi(self.file_id)
        self.assertRaisesMessage(ValueError, "Start and end line values are wrong!", section_api.create, data)
    
    # should raise exception if start>end
    def test_create_fail_2(self):
        data = {
            "start_line": 22,
            "end_line": 12,
            "section_name": "comment" 
        }
        section_api = SectionApi(self.file_id)
        self.assertRaisesMessage(ValueError, "Start and end line values are wrong!", section_api.create, data)
    
    # should raise exception if start>total or end>total
    def test_create_fail_3(self):
        data = {
            "start_line": 12,
            "end_line": 100,
            "section_name": "comment" 
        }
        section_api = SectionApi(self.file_id)
        self.assertRaisesMessage(ValueError, "Start and end line values are wrong!", section_api.create, data)
    
    # should raise exception if start>total or end>total
    def test_create_fail_4(self):
        data = {
            "start_line": 90,
            "end_line": 100,
            "section_name": "comment" 
        }
        section_api = SectionApi(self.file_id)
        self.assertRaisesMessage(ValueError, "Start and end line values are wrong!", section_api.create, data)

    # should raise exception if line conflict is detected
    def test_create_fail_with_conflict(self):
        data = {
            "start_line": 2,
            "end_line": 8,
            "section_name": "comment" 
        }
        section_api = SectionApi(self.file_id)
        self.assertRaisesMessage(ValueError, "Section conflict detected", section_api.create, data)
    
    # should delete section
    def test_delete_section(self):
        section_api = SectionApi(self.file_id)
        section_api.delete_section(1, 3)
        sections = section_api.get()
        self.assertEqual(len(sections), 6)
    
    # should not delete anything
    def test_delete_section_fake(self):
        section_api = SectionApi(self.file_id)
        section_api.delete_section(12, 22)
        sections = section_api.get()
        self.assertEqual(len(sections), 7)
    
    # should update section_status for all lines having it null
    def test_update_status(self):
        section_api = SectionApi(self.file_id)
        section_api.update_status("Does not compile")
        sections = section_api.get()
        filtered_null = sections.filter(section_status_id__isnull = True)
        filtered_not_null = sections.filter(section_status_id__isnull = False)
        self.assertEqual(len(filtered_null), 0)
        self.assertEqual(len(filtered_not_null), 7)
        self.assertEqual(filtered_not_null[0].section_status_id, 3)
    
    # should update status once
    def test_update_status_data(self):
        data = {
            "line_id": 2,
            "line_content": "Text 1"
        }
        section_api = SectionApi(self.file_id)
        section_api.update_status_data("Does not compile", data)
        sections = section_api.get()
        filtered = sections.filter(section_status_id__isnull = False)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].status_data, "Text 1,")
    
    # should update status_data twice
    def test_update_status_data_twice(self):
        data = {
            "line_id": 2,
            "line_content": "Text 1"
        }
        section_api = SectionApi(self.file_id)
        section_api.update_status_data("Does not compile", data)
        section_api.update_status_data("Does not compile", data)
        sections = section_api.get()
        filtered = sections.filter(section_status_id__isnull = False)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].status_data, "Text 1,Text 1,")

    def test_update_status_data_nested(self):
        data = {
            "line_id": 33,
            "line_content": "Text 1"
        }
        section_api = SectionApi(self.file_id)
        section_api.update_status_data("Does not compile", data)
        sections = section_api.get()
        filtered = sections.filter(section_status_id__isnull = False)
        self.assertEqual(len(filtered), 2)
    
    # should clear all statuses
    def test_clear_status_data(self):
        data = {
            "line_id": 2,
            "line_content": "Text 1"
        }
        section_api = SectionApi(self.file_id)
        section_api.update_status_data("Does not compile", data)
        data = {
            "line_id": 33,
            "line_content": "Text 1"
        }
        section_api.update_status_data("Does not compile", data)

        section_api.clear_status_data()
        sections = section_api.get()
        filtered_null = sections.filter(section_status_id__isnull = True)
        filtered_not_null = sections.filter(section_status_id__isnull = False)
        self.assertEqual(len(filtered_null), 7)
        self.assertEqual(len(filtered_not_null), 0)
    
    def test_get_source_code_enriched(self):
        file_api = FileApi()
        source_code = file_api.get_source_code_splitted(self.file_id)

        section_api = SectionApi(self.file_id)
        section_api.update_status("Does not compile")
        source_code_enriched = section_api.get_source_code_enriched(source_code)

        expected = [
            {'line': 'line 1', 'start_line': 1, 'end_line': 3, 'end_div': False, 'section_type': 'comment', 'section_status': 'Does not compile', 'class_name': 'code-section-outer'}, 
            {'line': 'line 2', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 3', 'start_line': 0, 'end_line': 0, 'end_div': True, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 4', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 5', 'start_line': 5, 'end_line': 10, 'end_div': False, 'section_type': 'directive', 'section_status': 'Does not compile', 'class_name': 'code-section-outer'}, 
            {'line': 'line 6', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 7', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 8', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 9', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 10', 'start_line': 0, 'end_line': 0, 'end_div': True, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 11', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 12', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 13', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 14', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 15', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 16', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 17', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 18', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 19', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 20', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 21', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 22', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 23', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 24', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 25', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 26', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 27', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 28', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 29', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 30', 'start_line': 30, 'end_line': 50, 'end_div': False, 'section_type': 'procedure', 'section_status': 'Does not compile', 'class_name': 'code-section-outer'}, 
            {'line': 'line 31', 'start_line': 31, 'end_line': 35, 'end_div': False, 'section_type': 'variable', 'section_status': 'Does not compile', 'class_name': 'code-section-inner'}, 
            {'line': 'line 32', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 33', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 34', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 35', 'start_line': 0, 'end_line': 0, 'end_div': True, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 36', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 37', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 38', 'start_line': 38, 'end_line': 38, 'end_div': True, 'section_type': 'comment', 'section_status': 'Does not compile', 'class_name': 'code-section-inner'}, 
            {'line': 'line 39', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 40', 'start_line': 40, 'end_line': 44, 'end_div': False, 'section_type': 'assembly', 'section_status': 'Does not compile', 'class_name': 'code-section-inner'}, 
            {'line': 'line 41', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 42', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 43', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 44', 'start_line': 0, 'end_line': 0, 'end_div': True, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 45', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 46', 'start_line': 46, 'end_line': 48, 'end_div': False, 'section_type': 'comment', 'section_status': 'Does not compile', 'class_name': 'code-section-inner'}, 
            {'line': 'line 47', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 48', 'start_line': 0, 'end_line': 0, 'end_div': True, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 49', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'line 50', 'start_line': 0, 'end_line': 0, 'end_div': True, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': 'int main(void) {', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': '//comment', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': '//comment', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': '}', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}, 
            {'line': '', 'start_line': 0, 'end_line': 0, 'end_div': False, 'section_type': '', 'section_status': '', 'class_name': ''}
        ]
        self.assertEqual(source_code_enriched, expected)
    
    def test_str(self):
        section_api = SectionApi(self.file_id)
        sections = section_api.get()
        section = sections[0]
        expected = f"{section.id}, file: {section.file.name}, {section.file.id} (lines {section.start_line} - {section.end_line}), {section.section_type.name}"
        self.assertEqual(section.__str__(), expected)
