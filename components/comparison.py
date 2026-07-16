import streamlit as st
import re


def _safe_float_parse(val):
    if val is None:
        return -1.0
    try:
        match = re.search(r'(\d+(?:\.\d+)?)', str(val))
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return -1.0


def _winner_color(a, b):
    """Return (color_a, color_b) — green for winner, muted for loser."""
    if a > b:
        return "#10b981", "#64748B"
    elif b > a:
        return "#64748B", "#10b981"
    return "#94A3B8", "#94A3B8"


def _render_comparison_row(label, val_a, val_b, color_a, color_b):
    """Render one comparison metric row using native columns."""
    r_label, r_a, r_b = st.columns([2, 4, 4])
    with r_label:
        st.markdown(f"**{label}**")
    with r_a:
        st.markdown(
            f'<span style="color:{color_a}; font-weight:700;">{val_a}</span>',
            unsafe_allow_html=True,
        )
    with r_b:
        st.markdown(
            f'<span style="color:{color_b}; font-weight:700;">{val_b}</span>',
            unsafe_allow_html=True,
        )


def show_comparison(ranked_candidates, rag, format_skill_name, render_notification):
    """
    Renders the Candidate Comparison Tool using native Streamlit components.
    """
    st.markdown('<div id="section-comparison"></div>', unsafe_allow_html=True)
    st.markdown("## ⚖ Candidate Comparison Tool")

    if len(ranked_candidates) < 2:
        with st.container(border=True):
            st.subheader("⚖️ Candidate Comparison")
            st.info("Upload at least two candidates to enable side-by-side Recruiter comparisons.")
        return

    names_list = [c["name"] for c in ranked_candidates]

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        cand_a_name = st.selectbox(
            "Select Candidate A", names_list, index=0, key="comp_sel_a"
        )
    with col_sel2:
        cand_b_name = st.selectbox(
            "Select Candidate B",
            names_list,
            index=min(1, len(names_list) - 1),
            key="comp_sel_b",
        )

    if cand_a_name == cand_b_name:
        render_notification(
            "Please select two different candidates to compare.", type="warning"
        )
        return

    cand_a = next(c for c in ranked_candidates if c["name"] == cand_a_name)
    cand_b = next(c for c in ranked_candidates if c["name"] == cand_b_name)
    profile_a = rag.candidate_profiles.get(cand_a["filename"], {})
    profile_b = rag.candidate_profiles.get(cand_b["filename"], {})

    score_a, score_b = cand_a["score"], cand_b["score"]
    cgpa_val_a = _safe_float_parse(profile_a.get("cgpa"))
    cgpa_val_b = _safe_float_parse(profile_b.get("cgpa"))
    exp_val_a = cand_a.get("cand_experience_years", 0.0)
    exp_val_b = cand_b.get("cand_experience_years", 0.0)

    proj_count_a = len(profile_a.get("projects", []) or [])
    proj_count_b = len(profile_b.get("projects", []) or [])
    skills_score_a = cand_a["breakdown"]["skills"]
    skills_score_b = cand_b["breakdown"]["skills"]

    matched_a_str = ", ".join(format_skill_name(s) for s in cand_a["matched_required"]) or "None"
    matched_b_str = ", ".join(format_skill_name(s) for s in cand_b["matched_required"]) or "None"
    missing_a_str = ", ".join(format_skill_name(s) for s in cand_a["missing_required"]) or "None"
    missing_b_str = ", ".join(format_skill_name(s) for s in cand_b["missing_required"]) or "None"

    with st.container(border=True):
        # Header row
        h_label, h_a, h_b = st.columns([2, 4, 4])
        with h_label:
            st.markdown("**Metric**")
        with h_a:
            st.markdown(f"**👤 {cand_a_name}**")
        with h_b:
            st.markdown(f"**👤 {cand_b_name}**")

        st.divider()

        # Overall Match
        ca, cb = _winner_color(score_a, score_b)
        _render_comparison_row("🏆 Overall Match", f"{score_a}%", f"{score_b}%", ca, cb)

        # Skills Score
        ca, cb = _winner_color(skills_score_a, skills_score_b)
        _render_comparison_row("🛠 Skills Score", f"{skills_score_a}%", f"{skills_score_b}%", ca, cb)

        # Experience
        ca, cb = _winner_color(exp_val_a, exp_val_b)
        _render_comparison_row("💼 Experience", f"{exp_val_a} yrs", f"{exp_val_b} yrs", ca, cb)

        # CGPA
        ca, cb = _winner_color(cgpa_val_a, cgpa_val_b)
        _render_comparison_row(
            "⭐ CGPA",
            profile_a.get("cgpa") or "N/A",
            profile_b.get("cgpa") or "N/A",
            ca, cb,
        )

        # Degree
        _render_comparison_row(
            "🎓 Degree",
            profile_a.get("degree") or "N/A",
            profile_b.get("degree") or "N/A",
            "#94A3B8", "#94A3B8",
        )

        # College
        _render_comparison_row(
            "🏫 College",
            profile_a.get("college") or "N/A",
            profile_b.get("college") or "N/A",
            "#94A3B8", "#94A3B8",
        )

        # Projects
        ca, cb = _winner_color(proj_count_a, proj_count_b)
        _render_comparison_row(
            "🚀 Projects",
            f"{proj_count_a} projects",
            f"{proj_count_b} projects",
            ca, cb,
        )

        st.divider()

        # Matched Skills
        mk_label, mk_a, mk_b = st.columns([2, 4, 4])
        with mk_label:
            st.markdown("**✅ Matched Skills**")
        with mk_a:
            st.caption(matched_a_str)
        with mk_b:
            st.caption(matched_b_str)

        # Missing Skills
        ms_label, ms_a, ms_b = st.columns([2, 4, 4])
        with ms_label:
            st.markdown("**❌ Missing Skills**")
        with ms_a:
            st.caption(missing_a_str)
        with ms_b:
            st.caption(missing_b_str)
