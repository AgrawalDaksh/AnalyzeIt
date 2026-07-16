import streamlit as st
import pandas as pd
import io
from collections import Counter

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="AnalyzeIt",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================
# SESSION STATE
# ============================================

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "rag" not in st.session_state:
    from backend import ResumeRAG
    st.session_state.rag = ResumeRAG()

if "embeddings_generated" not in st.session_state:
    st.session_state.embeddings_generated = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_matches" not in st.session_state:
    st.session_state.last_matches = []

if "loaded_files" not in st.session_state:
    st.session_state.loaded_files = []

if "job_profile" not in st.session_state:
    st.session_state.job_profile = None

if "loaded_jd" not in st.session_state:
    st.session_state.loaded_jd = None

if "ranked_candidates" not in st.session_state:
    st.session_state.ranked_candidates = []

# ============================================
# LOAD CSS
# ============================================

with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ============================================
# HELPERS
# ============================================

def format_skill_name(skill):
    if not skill:
        return ""
    if len(skill) <= 3:
        return skill.upper()
    return skill.title()


def generate_export_file(report_type, file_format):
    try:
        ranked = st.session_state.ranked_candidates
        job = st.session_state.job_profile
        rag = st.session_state.rag

        if not ranked or not job:
            return None, None, None

        if report_type == "Ranked Candidate List":
            data = []
            for idx, c in enumerate(ranked):
                data.append({
                    "Rank": idx + 1,
                    "Name": c["name"],
                    "Overall Match %": c["score"],
                    "Skills Match %": c["breakdown"]["skills"],
                    "Experience Match %": c["breakdown"]["experience"],
                    "Education Match %": c["breakdown"]["education"],
                    "CGPA Match %": c["breakdown"]["cgpa"],
                    "Projects Match %": c["breakdown"]["projects"],
                })
            df = pd.DataFrame(data)
            if file_format == "CSV":
                return df.to_csv(index=False).encode("utf-8"), "csv", "text/csv"
            elif file_format == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Rankings")
                return output.getvalue(), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file_format == "PDF":
                return rag.export_recruitment_report(), "pdf", "application/pdf"

        elif report_type == "Candidate Comparison":
            comparison_data = {
                "Metric": [
                    "Overall Match", "Skills Score", "Experience Score",
                    "Education Score", "CGPA Score", "Projects Score",
                    "Matched Required Skills", "Missing Required Skills",
                ]
            }
            for c in ranked:
                name = c["name"]
                comparison_data[name] = [
                    f"{c['score']}%",
                    f"{c['breakdown']['skills']}%",
                    f"{c['breakdown']['experience']}%",
                    f"{c['breakdown']['education']}%",
                    f"{c['breakdown']['cgpa']}%",
                    f"{c['breakdown']['projects']}%",
                    ", ".join(c["matched_required"]) or "None",
                    ", ".join(c["missing_required"]) or "None",
                ]
            df = pd.DataFrame(comparison_data)
            if file_format == "CSV":
                return df.to_csv(index=False).encode("utf-8"), "csv", "text/csv"
            elif file_format == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Comparison")
                return output.getvalue(), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file_format == "PDF":
                return rag.export_recruitment_report(), "pdf", "application/pdf"

        elif report_type == "Job Match Report":
            data = []
            for idx, c in enumerate(ranked):
                data.append({
                    "Rank": idx + 1,
                    "Name": c["name"],
                    "Match Score %": c["score"],
                    "Matched Required": ", ".join(c["matched_required"]),
                    "Missing Required": ", ".join(c["missing_required"]),
                })
            df = pd.DataFrame(data)
            if file_format == "CSV":
                return df.to_csv(index=False).encode("utf-8"), "csv", "text/csv"
            elif file_format == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="JobMatch")
                return output.getvalue(), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file_format == "PDF":
                return rag.export_recruitment_report(), "pdf", "application/pdf"

    except Exception as e:
        import logging
        logging.error(f"Failed to generate export file: {e}")
        return None, None, None

    return None, None, None

# ============================================
# IMPORT COMPONENTS
# ============================================

from components.header import show_header
from components.sidebar import show_sidebar
from components.upload import show_upload, show_jd_upload
from components.notifications import render_notification
from components.analytics import show_analytics
from components.candidate_rankings import show_candidate_rankings
from components.comparison import show_comparison
from components.chat import show_chat
from components.export import show_export

# ============================================
# SIDEBAR
# ============================================

show_sidebar()

# ============================================
# HEADER
# ============================================

show_header()

# ============================================
# MAIN LAYOUT (Full Width Dashboard)
# ============================================

# ── Analytics Dashboard ───────────────────────────────────────────
show_analytics(st.session_state.ranked_candidates, st.session_state.rag)

# ── Export Center ─────────────────────────────────────────────────
if st.session_state.ranked_candidates:
    show_export(
        ranked_candidates=st.session_state.ranked_candidates,
        job_profile=st.session_state.job_profile,
        rag=st.session_state.rag,
        generate_export_file=generate_export_file,
        render_notification=render_notification,
    )

st.divider()

# ── Upload Columns ────────────────────────────────────────────────
resume_col, jd_col = st.columns(2)

with resume_col:

    # Resume Upload
    uploaded_files = show_upload()

    current_files = (
        [file.name for file in uploaded_files] if uploaded_files else []
    )

    if current_files != st.session_state.loaded_files:
        st.session_state.loaded_files = current_files
        st.session_state.uploaded_files = uploaded_files

        if uploaded_files:
            with st.spinner("Parsing Resumes & Indexing Vector Store..."):
                rag = st.session_state.rag
                success_count, errors = rag.load_resumes(uploaded_files)
                if success_count > 0:
                    rag.generate_embeddings()
                    st.session_state.embeddings_generated = True
                else:
                    st.session_state.embeddings_generated = False

            if success_count > 0:
                render_notification(
                    f"Indexed {success_count} candidate resume(s) successfully!",
                    type="success",
                )

            for err_msg in errors:
                if err_msg.startswith("⚠️"):
                    render_notification(err_msg.replace("⚠️ ", ""), type="warning")
                else:
                    render_notification(err_msg.replace("❌ ", ""), type="error")

            if st.session_state.job_profile and st.session_state.embeddings_generated:
                with st.spinner("Running Match Scoring & Candidate Rankings Engine..."):
                    st.session_state.ranked_candidates = rag.rank_candidates()
            else:
                st.session_state.ranked_candidates = []
        else:
            st.session_state.embeddings_generated = False
            st.session_state.ranked_candidates = []

with jd_col:
    # JD Upload
    jd_file = show_jd_upload()
    jd_filename = jd_file.name if jd_file else None

    if jd_filename != st.session_state.loaded_jd:
        st.session_state.loaded_jd = jd_filename

        if jd_file:
            with st.spinner("Parsing Job Description & Analyzing Role Parameters..."):
                success, err_msg = st.session_state.rag.load_job_description(jd_file)

            if success:
                st.session_state.job_profile = st.session_state.rag.job_profile
                render_notification("Job Description parsed successfully!", type="success")

                if st.session_state.uploaded_files and st.session_state.embeddings_generated:
                    with st.spinner("Running Match Scoring & Candidate Rankings Engine..."):
                        st.session_state.ranked_candidates = st.session_state.rag.rank_candidates()
                else:
                    st.session_state.ranked_candidates = []
            else:
                st.session_state.job_profile = {}
                st.session_state.ranked_candidates = []
                render_notification(err_msg, type="error")
        else:
            st.session_state.job_profile = None
            st.session_state.rag.job_description = ""
            st.session_state.rag.job_profile = {}
            st.session_state.ranked_candidates = []

# ── Candidate Rankings ────────────────────────────────────────
show_candidate_rankings(
    ranked_candidates=st.session_state.ranked_candidates,
    rag=st.session_state.rag,
    format_skill_name=format_skill_name,
    render_notification=render_notification,
)

# ── Candidate Comparison ──────────────────────────────────────
show_comparison(
    ranked_candidates=st.session_state.ranked_candidates,
    rag=st.session_state.rag,
    format_skill_name=format_skill_name,
    render_notification=render_notification,
)

st.divider()

# ── Chat ──────────────────────────────────────────────────────────
show_chat(st.session_state.rag)