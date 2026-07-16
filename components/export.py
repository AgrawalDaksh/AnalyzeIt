import streamlit as st


def show_export(ranked_candidates, job_profile, rag, generate_export_file, render_notification):
    """
    Renders the Recruitment Export Center using native Streamlit components.
    """
    st.markdown("### 📥 Recruitment Export Center")

    exp_col1, exp_col2, exp_col3 = st.columns([2, 1, 1])

    with exp_col1:
        report_type = st.selectbox(
            "Export Document Type",
            ["Ranked Candidate List", "Candidate Comparison", "Job Match Report"],
            key="export_doc_type",
        )
    with exp_col2:
        file_format = st.selectbox(
            "Format",
            ["CSV", "Excel", "PDF"],
            key="export_file_format",
        )
    with exp_col3:
        # Simple native spacer
        st.write("")
        if not ranked_candidates:
            st.button("Download Report", disabled=True, key="btn_export_disabled_placeholder")
        else:
            file_bytes, ext, mime_type = generate_export_file(report_type, file_format)
            if file_bytes:
                st.download_button(
                    label="Download Report",
                    data=file_bytes,
                    file_name=f"{report_type.lower().replace(' ', '_')}.{ext}",
                    mime=mime_type,
                    key="btn_export_download",
                )
            else:
                render_notification(
                    "Error generating export document. Check that templates are valid.",
                    type="error",
                )
