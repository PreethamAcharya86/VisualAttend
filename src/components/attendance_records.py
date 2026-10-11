import re

import streamlit as st
from src.database.db import (
    get_attendance_for_teacher,
    get_enrolled_students_for_subject,
    get_teacher_subjects,
)
from src.components.attendance_export import (
    build_attendance_summary,
    build_student_attendance_matrix,
    create_student_attendance_workbook,
)


def attendance_record() :
    st.subheader("Attendance records")
    teacher_id = st.session_state.teacher_data["id"]
    records = get_attendance_for_teacher(teacher_id) or []

    if not records :
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTWGqo_db2tW-auSmOvGxqRUUuachAf1h_GIbbSKjnj5Cn-AL-n7b_kD94&s=10", width=300)
        st.info("No records found!")
    else:
        summary = build_attendance_summary(records)
        html = "<div class='modern-table-wrapper'><table class='modern-table'>"
        html += "<thead><tr><th>Time</th><th>Subject</th><th>Code</th><th>Status</th></tr></thead>"
        html += "<tbody>"
        for row in summary:
            html += (
                f"<tr><td>{row['date']}</td><td>{row['subject_name']}</td>"
                f"<td>{row['subject_code']}</td><td>{row['attendance_status']}</td></tr>"
            )
        html += "</tbody></table></div>"
        st.markdown(html, unsafe_allow_html=True)

    subjects = get_teacher_subjects(teacher_id) or []
    if not subjects:
        st.info("Create a subject before downloading an attendance sheet.")
        return

    subject_by_id = {subject["subject_id"]: subject for subject in subjects}
    subject_id = st.selectbox(
        "Select subject to download attendance",
        options=list(subject_by_id),
        format_func=lambda selected_id: (
            f"{subject_by_id[selected_id]['name']} "
            f"({subject_by_id[selected_id]['subject_code']})"
        ),
        key="attendance_export_subject",
    )
    selected_subject = subject_by_id[subject_id]
    enrolled_students = get_enrolled_students_for_subject(subject_id)
    subject_records = [
        record for record in records
        if str(record.get("subject_id", (record.get("subjects") or {}).get("subject_id")))
        == str(subject_id)
    ]
    date_columns, student_rows = build_student_attendance_matrix(
        enrolled_students,
        subject_records,
    )

    safe_filename = re.sub(
        r'[<>:"/\\|?*]+',
        "_",
        f"{selected_subject['subject_code']}_{selected_subject['name']}",
    ).strip(" ._")

    class_heading = (
        f"{selected_subject['name']} ({selected_subject['subject_code']})"
    )
    workbook = create_student_attendance_workbook(
        class_heading,
        date_columns,
        student_rows,
    )

    st.download_button(
        "Download Excel",
        data=workbook,
        file_name=f"{safe_filename}_attendance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )
