import unittest
from io import BytesIO
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from src.components.attendance_export import (
    build_attendance_summary,
    build_student_attendance_matrix,
    create_student_attendance_workbook,
)


class AttendanceExportTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {
                "subject_id": 7,
                "timestamp": "2026-10-10T09:00:00",
                "is_present": True,
                "subjects": {
                    "subject_id": 7,
                    "name": "Biology",
                    "subject_code": "BIO101",
                },
            },
            {
                "subject_id": 7,
                "timestamp": "2026-10-10T09:00:00",
                "is_present": False,
                "subjects": {
                    "subject_id": 7,
                    "name": "Biology",
                    "subject_code": "BIO101",
                },
            },
            {
                "subject_id": 9,
                "timestamp": "2026-10-10T09:00:00",
                "is_present": True,
                "subjects": {
                    "subject_id": 9,
                    "name": "Chemistry",
                    "subject_code": "CHEM101",
                },
            },
        ]

    def test_summary_groups_by_subject_and_matches_ui_status(self):
        summary = build_attendance_summary(self.records)

        self.assertEqual(len(summary), 2)
        biology = next(row for row in summary if row["subject_id"] == 7)
        self.assertEqual(biology["date"], "2026-10-10 09:00 AM")
        self.assertEqual(
            biology["attendance_status"],
            "✅Present: 1 |❌Absent: 1 | Total: 2",
        )
        self.assertEqual(
            next(row for row in summary if row["subject_id"] == 9)["attendance_status"],
            "✅Present: 1 |❌Absent: 0 | Total: 1",
        )

    def test_matrix_includes_only_enrolled_students_and_their_session_status(self):
        enrollments = [
            {"student_id": 20, "students": {"student_id": 20, "name": "Zoe"}},
            {"student_id": 10, "students": {"student_id": 10, "name": "Amy"}},
        ]
        records = [
            {
                "student_id": 10,
                "timestamp": "2026-10-10T09:00:00.123456+05:30",
                "is_present": True,
            },
            {
                "student_id": 20,
                "timestamp": "2026-10-10T09:00:00.123456+05:30",
                "is_present": False,
            },
            {
                "student_id": 999,
                "timestamp": "2026-10-10T09:00:00",
                "is_present": True,
            },
            {
                "student_id": 10,
                "timestamp": "2026-10-11T10:30:08",
                "is_present": False,
            },
        ]

        dates, students = build_student_attendance_matrix(enrollments, records)

        self.assertEqual(
            dates,
            ["2026-10-10\n09:00:00 AM", "2026-10-11\n10:30:08 AM"],
        )
        self.assertEqual([student["student_id"] for student in students], [10, 20])
        self.assertEqual(students[0]["attendance"], ["Present", "Absent"])
        self.assertEqual(students[1]["attendance"], ["Absent", ""])

    def test_workbook_contains_class_heading_roster_and_date_status_cells(self):
        dates, students = build_student_attendance_matrix(
            [
                {"student_id": 10, "students": {"student_id": 10, "name": "Amy"}},
                {"student_id": 20, "students": {"student_id": 20, "name": "Zoe"}},
            ],
            [
                {
                    "student_id": 10,
                    "timestamp": "2026-10-10T09:00:00.123456+05:30",
                    "is_present": True,
                },
                {
                    "student_id": 20,
                    "timestamp": "2026-10-10T09:00:00.123456+05:30",
                    "is_present": False,
                },
            ],
        )
        workbook = create_student_attendance_workbook(
            "Biology (BIO101)",
            dates,
            students,
        )

        with ZipFile(BytesIO(workbook)) as workbook_zip:
            shared_strings_root = ET.fromstring(workbook_zip.read("xl/sharedStrings.xml"))
            namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            strings = [
                "".join(item.itertext())
                for item in shared_strings_root.findall("main:si", namespace)
            ]
            sheet_root = ET.fromstring(workbook_zip.read("xl/worksheets/sheet1.xml"))

        cells = {}
        for cell in sheet_root.findall(".//main:sheetData/main:row/main:c", namespace):
            value = cell.find("main:v", namespace)
            if value is not None:
                cells[cell.attrib["r"]] = (
                    strings[int(value.text)]
                    if cell.attrib.get("t") == "s"
                    else value.text
                )
        self.assertEqual(cells["A1"], "Biology (BIO101)")
        self.assertEqual(cells["A2"], "Student_id")
        self.assertEqual(cells["B2"], "name")
        self.assertEqual(cells["C2"], "2026-10-10\n09:00:00 AM")
        self.assertEqual(cells["A3"], "10")
        self.assertEqual(cells["B3"], "Amy")
        self.assertEqual(cells["C3"], "Present")
        self.assertEqual(cells["A4"], "20")
        self.assertEqual(cells["B4"], "Zoe")
        self.assertEqual(cells["C4"], "Absent")


if __name__ == "__main__":
    unittest.main()
