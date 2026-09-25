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
    Works seamlessly whether or not a Job Description has been uploaded.
    """
    st.markdown('<div id="section-comparison"></div>', unsafe_allow_html=True)
    st.markdown("## ⚖ Candidate Comparison Tool")

    # Build candidates list: prefer ranked_candidates, fallback to rag.candidate_profiles, then candidate_metadata
    candidate_items = []
    if ranked_candidates:
        candidate_items = list(ranked_candidates)
    elif getattr(rag, "candidate_profiles", None) and len(rag.candidate_profiles) > 0:
        for fname, prof in rag.candidate_profiles.items():
            name = prof.get("name")
            if not name or name in ["Not Available", "null", "None", "", "Candidate"]:
                name = fname.replace(".pdf", "").replace("_", " ").title()
            candidate_items.append({
                "name": name,
                "filename": fname,
                "score": None,
                "breakdown": None,
                "matched_required": [],
                "missing_required": [],
                "cand_experience_years": 0.0,
            })
    elif getattr(rag, "candidate_metadata", None) and len(rag.candidate_metadata) > 0:
        for fname, meta in rag.candidate_metadata.items():
            name = meta.get("full_name") or fname.replace(".pdf", "").replace("_", " ").title()
            candidate_items.append({
                "name": name,
                "filename": fname,
                "score": None,
                "breakdown": None,
                "matched_required": [],
                "missing_required": [],
                "cand_experience_years": 0.0,
            })

    if len(candidate_items) < 2:
        with st.container(border=True):
            st.subheader("⚖️ Candidate Comparison")
            st.info("Upload at least two candidate resumes to enable side-by-side recruiter comparisons.")
        return

    names_list = [c["name"] for c in candidate_items]
    
    # Determine default indices for A and B
    idx_a = 0
    saved_a = st.session_state.get("comp_sel_a")
    if saved_a in names_list:
        idx_a = names_list.index(saved_a)

    idx_b = 1 if len(names_list) > 1 else 0
    saved_b = st.session_state.get("comp_sel_b")
    if saved_b in names_list and saved_b != saved_a:
        idx_b = names_list.index(saved_b)
    elif idx_a == idx_b and len(names_list) > 1:
        idx_b = (idx_a + 1) % len(names_list)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        cand_a_name = st.selectbox(
            "Select Candidate A", names_list, index=idx_a, key="comp_sel_a"
        )
    with col_sel2:
        cand_b_name = st.selectbox(
            "Select Candidate B", names_list, index=idx_b, key="comp_sel_b"
        )

    if cand_a_name == cand_b_name:
        st.warning("⚠️ Please select two different candidates to view side-by-side comparative analysis.")
        return

    cand_a = next((c for c in candidate_items if c["name"] == cand_a_name), candidate_items[0])
    cand_b = next((c for c in candidate_items if c["name"] == cand_b_name), candidate_items[1])

    profile_a = rag.candidate_profiles.get(cand_a["filename"], {})
    profile_b = rag.candidate_profiles.get(cand_b["filename"], {})

    has_jd_scoring = cand_a.get("score") is not None and cand_b.get("score") is not None
    score_a = cand_a.get("score", 0)
    score_b = cand_b.get("score", 0)

    cgpa_val_a = _safe_float_parse(profile_a.get("cgpa"))
    cgpa_val_b = _safe_float_parse(profile_b.get("cgpa"))

    # Calculate experience years if not present
    exp_val_a = cand_a.get("cand_experience_years")
    if exp_val_a is None or exp_val_a == 0:
        exp_val_a = float(len(profile_a.get("experience", [])))
    exp_val_b = cand_b.get("cand_experience_years")
    if exp_val_b is None or exp_val_b == 0:
        exp_val_b = float(len(profile_b.get("experience", [])))

    proj_count_a = len(profile_a.get("projects", []) or [])
    proj_count_b = len(profile_b.get("projects", []) or [])

    skills_a = [format_skill_name(s) for s in profile_a.get("skills", []) if s]
    skills_b = [format_skill_name(s) for s in profile_b.get("skills", []) if s]

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

        # JD Match Scoring (if JD is uploaded)
        if has_jd_scoring:
            ca, cb = _winner_color(score_a, score_b)
            _render_comparison_row("🏆 Overall Match", f"{score_a}%", f"{score_b}%", ca, cb)

            breakdown_a = cand_a.get("breakdown", {})
            breakdown_b = cand_b.get("breakdown", {})
            skills_score_a = breakdown_a.get("skills", 0)
            skills_score_b = breakdown_b.get("skills", 0)
            ca, cb = _winner_color(skills_score_a, skills_score_b)
            _render_comparison_row("🛠 Skills Score", f"{skills_score_a}%", f"{skills_score_b}%", ca, cb)

        # CGPA
        ca, cb = _winner_color(cgpa_val_a, cgpa_val_b)
        _render_comparison_row(
            "⭐ CGPA",
            profile_a.get("cgpa") or "N/A",
            profile_b.get("cgpa") or "N/A",
            ca, cb,
        )

        # Experience
        ca, cb = _winner_color(exp_val_a, exp_val_b)
        _render_comparison_row("💼 Experience", f"{exp_val_a} yrs", f"{exp_val_b} yrs", ca, cb)

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
            f"{proj_count_a} project(s)",
            f"{proj_count_b} project(s)",
            ca, cb,
        )

        st.divider()

        # Skills list
        sk_label, sk_a, sk_b = st.columns([2, 4, 4])
        with sk_label:
            st.markdown("**🛠 Skills**")
        with sk_a:
            st.caption(", ".join(skills_a) if skills_a else "None listed")
        with sk_b:
            st.caption(", ".join(skills_b) if skills_b else "None listed")

        # Matched and Missing Skills if JD scoring is available
        if has_jd_scoring:
            matched_a_str = ", ".join(format_skill_name(s) for s in cand_a.get("matched_required", [])) or "None"
            matched_b_str = ", ".join(format_skill_name(s) for s in cand_b.get("matched_required", [])) or "None"
            missing_a_str = ", ".join(format_skill_name(s) for s in cand_a.get("missing_required", [])) or "None"
            missing_b_str = ", ".join(format_skill_name(s) for s in cand_b.get("missing_required", [])) or "None"

            st.divider()
            mk_label, mk_a, mk_b = st.columns([2, 4, 4])
            with mk_label:
                st.markdown("**✅ Matched Skills**")
            with mk_a:
                st.caption(matched_a_str)
            with mk_b:
                st.caption(matched_b_str)

            ms_label, ms_a, ms_b = st.columns([2, 4, 4])
            with ms_label:
                st.markdown("**❌ Missing Skills**")
            with ms_a:
                st.caption(missing_a_str)
            with ms_b:
                st.caption(missing_b_str)
