from datetime import datetime
from io import BytesIO

import xlsxwriter


def build_attendance_summary(records):
    sessions = {}

    for record in records:
        timestamp = record.get("timestamp")
        if not timestamp:
            continue

        subject = record["subjects"]
        subject_id = subject.get("subject_id", record.get("subject_id"))
        session_key = (
            timestamp.split(".", 1)[0],
            subject_id,
            subject["name"],
            subject["subject_code"],
        )
        session = sessions.setdefault(
            session_key,
            {
                "session_timestamp": session_key[0],
                "subject_id": subject_id,
                "date": datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %I:%M %p"),
                "subject_name": subject["name"],
                "subject_code": subject["subject_code"],
                "present_count": 0,
                "total_count": 0,
            },
        )
        session["present_count"] += bool(record.get("is_present", False))
        session["total_count"] += 1

    summary = []
    for session in sessions.values():
        absent_count = session["total_count"] - session["present_count"]
        summary.append({
            **session,
            "attendance_status": (
                f"✅Present: {session['present_count']} "
                f"|❌Absent: {absent_count} "
                f"| Total: {session['total_count']}"
            ),
        })

    return sorted(summary, key=lambda row: row["session_timestamp"], reverse=True)


def build_student_attendance_matrix(enrolled_students, attendance_records):
    enrolled = {}
    for enrollment in enrolled_students:
        student = enrollment.get("students") or {}
        student_id = enrollment["student_id"]
        enrolled[student_id] = {
            "student_id": student_id,
            "name": student.get("name", ""),
        }

    sessions = {}
    attendance_by_student = {}
    for record in attendance_records:
        timestamp = record.get("timestamp")
        if not timestamp:
            continue

        session_key = timestamp.split(".", 1)[0]
        sessions[session_key] = datetime.fromisoformat(timestamp).strftime(
            "%Y-%m-%d\n%I:%M:%S %p"
        )
        student_id = record["student_id"]
        if student_id in enrolled:
            attendance_by_student[(student_id, session_key)] = (
                "Present" if record.get("is_present", False) else "Absent"
            )

    ordered_sessions = sorted(sessions, key=datetime.fromisoformat)
    date_columns = [sessions[session_key] for session_key in ordered_sessions]
    students = []
    for student_id, student in enrolled.items():
        students.append({
            **student,
            "attendance": [
                attendance_by_student.get((student_id, session_key), "")
                for session_key in ordered_sessions
            ],
        })
    students.sort(key=lambda student: (str(student["name"]).casefold(), str(student["student_id"])))
    return date_columns, students


def create_student_attendance_workbook(class_heading, date_columns, students):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Attendance")

    title_format = workbook.add_format({"bold": True, "font_size": 16, "align": "center"})
    header_format = workbook.add_format({
        "bold": True,
        "bg_color": "#DCE6F1",
        "border": 1,
        "text_wrap": True,
        "align": "center",
        "valign": "vcenter",
    })
    status_format = workbook.add_format({"align": "center"})

    last_column = len(date_columns) + 1
    worksheet.merge_range(0, 0, 0, last_column, class_heading, title_format)
    worksheet.write(1, 0, "Student_id", header_format)
    worksheet.write(1, 1, "name", header_format)
    for column, date_label in enumerate(date_columns, start=2):
        worksheet.write(1, column, date_label, header_format)
        worksheet.set_column(column, column, 18)

    worksheet.set_column("A:A", 14)
    worksheet.set_column("B:B", 28)
    worksheet.set_row(1, 38)
    worksheet.freeze_panes(2, 2)

    for row_index, student in enumerate(students, start=2):
        worksheet.write(row_index, 0, student["student_id"])
        worksheet.write_string(row_index, 1, str(student["name"]))
        for column, status in enumerate(student["attendance"], start=2):
            worksheet.write_string(row_index, column, status, status_format)

    workbook.close()
    return output.getvalue()
