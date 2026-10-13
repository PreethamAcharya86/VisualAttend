import base64
from pathlib import Path

import streamlit as st
from src.components.header import back, navbar
from src.components.create_subject_dialog import create_subject_dialog
from src.components.share_subject_dialog import share_subject_dialog
from src.components.subject_card import subject_card
from src.components.attendance_records import attendance_record
from src.components.take_attendance import take_attendance
from src.database.db import register_teacher, login_teacher, get_teacher_subjects
import time


def teacher_screen():
    navbar(hide_actions=True)

    if 'teacher_data' in st.session_state and st.session_state.user_role == 'teacher':
        teacher_dashboard()
    elif 'teacher' not in st.session_state or st.session_state.teacher == "login":
        teacher_screen_login()
    elif st.session_state.teacher == "register":
        teacher_screen_register()


def teacher_screen_login():
    image_path = Path(__file__).resolve().parents[2] / "assets" / "login_image.png"
    with image_path.open("rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("ascii")

    image_col, login_col = st.columns(2, gap="large", vertical_alignment="center")
    with image_col:
        st.markdown(
            f"""
            <div class="teacher-login-artwork">
                <img src="data:image/png;base64,{encoded_image}" alt="Teacher login illustration" />
            </div>
            """,
            unsafe_allow_html=True,
        )

    with login_col:
        st.markdown(
            """
            <div style="text-align:center; margin-bottom:1.2rem;">
                <div style="width:48px; height:48px; background:var(--blue-50); border-radius:50%; display:inline-flex; align-items:center; justify-content:center; margin-bottom:0.5rem;">
                    <span class="material-symbols-outlined" style="color:var(--blue-600); font-size:26px;">lock</span>
                </div>
                <h2 style="margin:0; color:var(--blue-900); font-size:1.6rem; font-weight:800;">Teacher Login</h2>
                <p style="color:var(--gray-600); font-size:0.93rem; margin-top:0.3rem;">Sign in to access your teacher portal.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            teacher_username = st.text_input("Username", placeholder='Enter your username')
            teacher_password = st.text_input("Password", type="password", placeholder='Enter your password')

            st.divider()

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Login", shortcut='enter', type="primary", use_container_width=True):
                    success, message = login_teacher(teacher_username.strip(), teacher_password)
                    if success:
                        st.toast(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Incorrect username or password. Please try again.")
            with btn2:
                if st.button("Register", use_container_width=True):
                    st.session_state.teacher = 'register'
                    st.rerun()


def teacher_screen_register():
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.2rem;">
            <div style="width:48px; height:48px; background:var(--blue-50); border-radius:50%; display:inline-flex; align-items:center; justify-content:center; margin-bottom:0.5rem;">
                <span class="material-symbols-outlined" style="color:var(--blue-600); font-size:26px;">person_add</span>
            </div>
            <h2 style="margin:0; color:var(--blue-900); font-size:1.6rem; font-weight:800;">Teacher Registration</h2>
            <p style="color:var(--gray-600); font-size:0.93rem; margin-top:0.3rem;">Create your teacher account.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, mid_col, _ = st.columns([1, 1.8, 1])
    with mid_col:
        with st.container(border=True):
            teacher_name = st.text_input("Full Name", placeholder='Enter your full name')
            teacher_username = st.text_input("Username", placeholder='Choose a username')
            teacher_password = st.text_input("Password", type="password", placeholder='Create a password')

            st.divider()

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Register", shortcut="enter", type="primary", use_container_width=True):
                    success, message = register_teacher(
                        teacher_name.strip(), teacher_username.strip(), teacher_password
                    )
                    if success:
                        st.toast(message)
                        time.sleep(2)
                        st.session_state.teacher = 'login'
                        st.rerun()
                    else:
                        st.error("Registration failed. Username may already be taken.")
                        time.sleep(2)

            with btn2:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.teacher = "login"
                    st.rerun()


def _render_teacher_hero(image_filename: str, title: str, subtitle: str):
    image_path = Path(__file__).resolve().parents[1] / "Images" / image_filename
    with image_path.open("rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("ascii")

    st.markdown(
        f"""
        <div class="teacher-dashboard-hero">
            <div class="teacher-dashboard-copy">
                <h2>{title}</h2>
                <p class="hero-desktop-copy">{subtitle}</p>
            </div>
            <img src="data:image/png;base64,{encoded_image}" alt="{title}" />
        </div>
        <div class="hero-mobile-copy">
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def teacher_dashboard():
    data = st.session_state.teacher_data

    col_left, col_right = st.columns([1, 0.24], gap="small")
    with col_left:
        back()
    with col_right:
        st.markdown('<div class="action-right-wrapper">', unsafe_allow_html=True)
        if st.button("Logout", key='logout_teacher', type='secondary', icon=":material/logout:"):
            del st.session_state.teacher_data
            st.session_state.user_role = None
            st.session_state.is_logged_in = False
            st.session_state['login_type'] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    _render_teacher_hero(
        "teacherIcon.png",
        f"Hello, {data['name']}",
        "Manage subjects, inspect attendance, and keep your classroom workflow running smoothly.",
    )

    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        tab_type = 'primary' if st.session_state.current_teacher_tab == 'take_attendance' else 'secondary'
        if st.button("Take Attendance", type=tab_type, width='stretch', icon=':material/camera_alt:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()
    with tab2:
        tab_type = 'primary' if st.session_state.current_teacher_tab == 'manage_subjects' else 'secondary'
        if st.button("Manage Subjects", type=tab_type, width='stretch', icon=':material/menu_book:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
    with tab3:
        tab_type = 'primary' if st.session_state.current_teacher_tab == 'attendance_record' else 'secondary'
        if st.button("Attendance Records", type=tab_type, width='stretch', icon=':material/assessment:'):
            st.session_state.current_teacher_tab = 'attendance_record'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == 'take_attendance':
        take_attendance()
    if st.session_state.current_teacher_tab == 'manage_subjects':
        manage_subjects(data)
    if st.session_state.current_teacher_tab == 'attendance_record':
        attendance_record()


def manage_subjects(data):
    teacher_id = data['id']

    col1, col2 = st.columns([2, 1], vertical_alignment="center")
    with col1:
        st.subheader("My Subjects")
    with col2:
        if st.button("Create New Subject", type="primary", width='stretch', icon=":material/add:"):
            create_subject_dialog(teacher_id)

    st.divider()

    subjects = get_teacher_subjects(teacher_id)

    if subjects:
        for subject in subjects:
            stats = [
                ("", "Students", subject["total_students"]),
                ("", "Classes", subject["total_classes"])
            ]

            def share_btn():
                if st.button(
                    f"Share Class Code",
                    key=f"Share_{subject['subject_code']}",
                    icon=":material/share:"
                ):
                    share_subject_dialog(subject['name'], subject['subject_code'])

            subject_card(
                name=subject['name'],
                code=subject['subject_code'],
                section=subject["section"],
                stats=stats,
                footer_callback=share_btn
            )

    else:
        st.markdown(
            """
            <div style="text-align:center; padding:2rem 1rem; color:var(--gray-600);">
                <p style="margin:0; font-size:1rem; font-weight:500;">No subjects found.</p>
                <p style="margin:0.3rem 0 0; font-size:0.88rem;">Click <strong>Create New Subject</strong> to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
