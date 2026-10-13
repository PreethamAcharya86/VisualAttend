import base64
from pathlib import Path

import streamlit as st
from src.components.header import navbar
from src.ui.base_layout import style_base_layout
from src.components.footer import footer


def _render_image_card(image_filename: str, alt_text: str, width: int = 420):
    image_path = Path(__file__).resolve().parents[1] / "Images" / image_filename
    with image_path.open("rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("ascii")

    st.markdown(
        f"""
        <div class="hero-visual-card">
            <img src="data:image/png;base64,{encoded_image}" alt="{alt_text}" style="max-width:{width}px;" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def home_screen():
    style_base_layout()
    navbar()

    assets_path = Path(__file__).resolve().parents[2] / "assets"
    learning_svg = base64.b64encode((assets_path / "home_learning.svg").read_bytes()).decode("ascii")
    attendance_svg = base64.b64encode((assets_path / "home_attendance.svg").read_bytes()).decode("ascii")

    st.markdown(
        f"""
        <div class="home-page-marker" aria-hidden="true"></div>
        <section class="home-hero">
            <div class="home-hero-orbit">
                <div class="home-hero-orbit-item home-hero-orbit-item--1" role="img" aria-label="Library" style="background-image:url('data:image/svg+xml;base64,{learning_svg}'); background-position:0% 50%;"></div>
                <div class="home-hero-orbit-item home-hero-orbit-item--2" role="img" aria-label="Textbook" style="background-image:url('data:image/svg+xml;base64,{learning_svg}'); background-position:50% 50%;"></div>
                <div class="home-hero-orbit-item home-hero-orbit-item--3" role="img" aria-label="Subjects" style="background-image:url('data:image/svg+xml;base64,{learning_svg}'); background-position:100% 50%;"></div>
                <div class="home-hero-orbit-item home-hero-orbit-item--4" role="img" aria-label="Attendance roster" style="background-image:url('data:image/svg+xml;base64,{attendance_svg}'); background-position:0% 50%;"></div>
                <div class="home-hero-orbit-item home-hero-orbit-item--5" role="img" aria-label="Daily attendance record" style="background-image:url('data:image/svg+xml;base64,{attendance_svg}'); background-position:50% 50%;"></div>
                <div class="home-hero-orbit-item home-hero-orbit-item--6" role="img" aria-label="Verified present student" style="background-image:url('data:image/svg+xml;base64,{attendance_svg}'); background-position:100% 50%;"></div>
                <div class="home-hero-content">
                    <div class="hero-badge">AI-powered classroom attendance</div>
                    <h1>VisualAttend</h1>
                    <p>Smarter attendance. More time for learning.</p>
                    <span class="home-hero-detail">Face recognition · Live insights · Simple class enrollment</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    hero_image_path = Path(__file__).resolve().parents[1] / "Images" / "Project_icon.png"
    with hero_image_path.open("rb") as hero_image_file:
        hero_image_b64 = base64.b64encode(hero_image_file.read()).decode("ascii")

    st.markdown(
        f"""
        <div class="hero-row">
            <div class="hero-left-panel">
                <div class="hero-card">
                    <div class="hero-badge">AI-powered attendance</div>
                    <h2>Automate Attendance with AI Face Recognition</h2>
                    <p>
                        Welcome to <strong>VisualAttend</strong> — a polished, fast classroom attendance experience designed for modern schools.
                        Teachers can scan classroom photos in seconds, and students gain instant visibility into their attendance performance.
                    </p>
                </div>
                <div class="hero-note-card hero-note-card--compact">
                    <h4>Built for fast, modern classrooms</h4>
                    <p>From instant face-based sign-in to cleaner attendance insights, every detail is designed to feel effortless.</p>
                </div>
            </div>
            <div class="hero-right-panel">
                <div class="hero-visual-card hero-visual-card--large">
                    <img src="data:image/png;base64,{hero_image_b64}" alt="VisualAttend hero illustration" />
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        if st.button("Start Managing Attendance Now", type="primary", use_container_width=True):
            st.session_state['login_type'] = 'choose'
            st.rerun()

    st.markdown(
        """
        <div class="feature-row">
            <div class="feature-card">
                <div class="fc-icon-box">
                    <span class="material-symbols-outlined">face</span>
                </div>
                <h4>AI Face Recognition</h4>
                <p>Detect and mark student attendance automatically using computer vision technology.</p>
            </div>
            <div class="feature-card">
                <div class="fc-icon-box">
                    <span class="material-symbols-outlined">analytics</span>
                </div>
                <h4>Instant Insights</h4>
                <p>Track real-time subject stats, attendance percentages, and detailed logs.</p>
            </div>
            <div class="feature-card">
                <div class="fc-icon-box">
                    <span class="material-symbols-outlined">qr_code_scanner</span>
                </div>
                <h4>Easy Class Enrollment</h4>
                <p>Students join classes instantly via unique subject codes or QR code scanning.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    footer()