import streamlit as st


def format_size(bytes_size):
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"


def show_upload():
    """
    Resume upload section using native Streamlit components.
    Returns the list of uploaded file objects.
    """
    with st.container(border=True):
        st.markdown("### ☁️ Upload Candidate Resumes")
        st.caption("Drag & Drop your resume PDFs here • Supports: PDF • Multiple files")

        uploaded = st.file_uploader(
            "Upload Resumes",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="resumes_uploader"
        )

    return uploaded


def show_jd_upload():
    """
    Job Description upload section using native Streamlit components.
    Returns the uploaded JD file object or None.
    """
    with st.container(border=True):
        st.markdown("### 📥 Upload Job Description")
        st.caption("Drag & Drop your JD PDF here • Supports: PDF • Single file")

        uploaded = st.file_uploader(
            "Upload Job Description",
            type=["pdf"],
            accept_multiple_files=False,
            label_visibility="collapsed",
            key="jd_uploader"
        )

    return uploaded