import streamlit as st
from components.candidate_card import show_candidate_card


def show_candidate_rankings(ranked_candidates, rag, format_skill_name, render_notification):
    """
    Renders the ranked candidate list section.
    """
    st.markdown('<div id="section-rankings"></div>', unsafe_allow_html=True)
    st.markdown("## 🏆 Candidate Rankings")

    if not ranked_candidates:
        with st.container(border=True):
            st.subheader("👥 No Candidate Rankings Loaded")
            st.info("Upload resumes in the panel and add a Job Description to view automated rank scores and matches.")
        return

    for index, candidate in enumerate(ranked_candidates):
        show_candidate_card(
            candidate=candidate,
            index=index,
            rag=rag,
            format_skill_name=format_skill_name,
            render_notification=render_notification,
        )
