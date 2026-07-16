import streamlit as st
import re


def _get_initials(name_str):
    if not name_str:
        return "CN"
    parts = name_str.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name_str[:2].upper()


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


def _render_skill_badges(skills, badge_class):
    """Render skill badges — only CSS class used, no layout HTML."""
    if not skills:
        return "<span style='color:#94a3b8; font-style:italic; font-size:12px;'>None</span>"
    return " ".join(
        f'<span class="skill-badge {badge_class}">{s}</span>'
        for s in skills
    )


def show_candidate_card(candidate, index, rag, format_skill_name, render_notification):
    """
    Renders a single candidate card using native Streamlit components.
    All layout via st.container / st.columns — no HTML for layout.
    """
    rank = index + 1
    name = candidate["name"]
    filename = candidate["filename"]
    overall_score = candidate["score"]
    breakdown = candidate["breakdown"]
    matched_req = [format_skill_name(s) for s in candidate["matched_required"]]
    missing_req = [format_skill_name(s) for s in candidate["missing_required"]]
    profile = rag.candidate_profiles.get(filename, {})

    initials = _get_initials(name)
    degree = profile.get("degree") or "N/A"
    college = profile.get("college") or "N/A"
    cgpa = profile.get("cgpa") or "N/A"
    experience = str(candidate.get("cand_experience_years", 0))
    exp_list = profile.get("experience", [])
    experience_summary = exp_list[0] if exp_list else "No experience listed"

    # Style block for avatar Circle
    st.markdown("""
    <style>
    .avatar-circle {
        background: linear-gradient(135deg, rgba(79,140,255,0.25), rgba(124,92,252,0.25));
        color: #93c5fd;
        font-weight: 800;
        font-size: 15px;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        border: 1px solid rgba(79,140,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Card container ───────────────────────────────────────────────
    with st.container(border=True):

        # ── Header row: Avatar | Name/Role  ·  Score ────────────────
        header_col, score_col = st.columns([8, 2])

        with header_col:
            av_col, info_col = st.columns([1, 8])
            with av_col:
                st.markdown(
                    f'<div class="avatar-circle">{initials}</div>',
                    unsafe_allow_html=True,
                )
            with info_col:
                st.markdown(f"**{name}**")
                st.markdown(
                    f'<span class="rank-tag">Rank #{rank}</span>'
                    f'<span style="font-size:12px; color:#64748B;"> &bull; {degree}</span>',
                    unsafe_allow_html=True,
                )

        with score_col:
            st.metric("Match", f"{overall_score}%")

        st.divider()

        # ── Education / Experience / CGPA row ────────────────────────
        edu_col, exp_col, cgpa_col = st.columns(3)
        with edu_col:
            st.markdown("**🎓 Education**")
            st.caption(f"{degree}")
            st.caption(f"{college}")
        with exp_col:
            st.markdown("**💼 Experience**")
            st.caption(f"{experience} yrs exp")
            st.caption(experience_summary)
        with cgpa_col:
            st.markdown("**⭐ CGPA**")
            st.caption(str(cgpa))

        st.divider()

        # ── Matched / Missing Skills ──────────────────────────────────
        sk1, sk2 = st.columns(2)
        with sk1:
            st.markdown(
                '<p style="font-size:10px; color:#64748B; font-weight:700; '
                'text-transform:uppercase; letter-spacing:0.6px; margin-bottom:6px;">'
                'Matched Skills</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="display:flex; flex-wrap:wrap; gap:6px;">'
                f'{_render_skill_badges(matched_req, "skill-badge-matched")}'
                f'</div>',
                unsafe_allow_html=True,
            )
        with sk2:
            st.markdown(
                '<p style="font-size:10px; color:#64748B; font-weight:700; '
                'text-transform:uppercase; letter-spacing:0.6px; margin-bottom:6px;">'
                'Missing Skills</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="display:flex; flex-wrap:wrap; gap:6px;">'
                f'{_render_skill_badges(missing_req, "skill-badge-missing")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Action buttons ────────────────────────────────────────────
        action1, action2 = st.columns(2)
        with action1:
            btn_details = st.button("👁 View Details", key=f"btn_details_{filename}")
        with action2:
            btn_compare = st.button("⚖ Compare", key=f"btn_compare_{filename}")

        action3, action4 = st.columns(2)
        with action3:
            btn_interview = st.button("💬 Interview Questions", key=f"btn_interview_{filename}")
        with action4:
            btn_report = st.button("🤖 Hiring Report", key=f"btn_report_{filename}")

        key_view = f"active_view_{filename}"
        
        # Toggle view details panel
        if btn_details:
            st.session_state[key_view] = "details" if st.session_state.get(key_view) != "details" else None
            st.rerun()
            
        # Select for comparison
        if btn_compare:
            # Alternate placing the selected candidate in comp_sel_a
            st.session_state.comp_sel_a = name
            render_notification(f"Selected {name} as Candidate A. Scroll down to candidate comparison tool.", type="success")
            st.rerun()
            
        # Toggle interview guide panel
        if btn_interview:
            st.session_state[key_view] = "interview" if st.session_state.get(key_view) != "interview" else None
            st.rerun()
            
        # Toggle hiring report panel
        if btn_report:
            st.session_state[key_view] = "hiring" if st.session_state.get(key_view) != "hiring" else None
            st.rerun()

        # ── Toggle Container Renders ─────────────────────────────────
        active_view = st.session_state.get(key_view)
        
        if active_view == "details":
            with st.container(border=True):
                st.markdown("#### 👤 Profile Details")
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.markdown(f"**Name:** {profile.get('name') or 'N/A'}")
                    st.markdown(f"**Email:** {profile.get('email') or 'N/A'}")
                    st.markdown(f"**Phone:** {profile.get('phone') or 'N/A'}")
                with p_col2:
                    st.markdown(f"**College:** {profile.get('college') or 'N/A'}")
                    st.markdown(f"**Degree:** {profile.get('degree') or 'N/A'}")
                    st.markdown(f"**CGPA:** {profile.get('cgpa') or 'N/A'}")

                st.divider()
                st.markdown("#### 🛠 Extracted Skills")
                skills_list = profile.get("skills", [])
                if skills_list:
                    st.markdown(", ".join(f"`{format_skill_name(s)}`" for s in skills_list))
                else:
                    st.markdown("*No skills listed*")

                st.divider()
                st.markdown("#### 🚀 Projects")
                projects_list = profile.get("projects", [])
                if projects_list:
                    for project in projects_list:
                        st.markdown(f"- {project}")
                else:
                    st.markdown("*No projects listed*")

                st.divider()
                st.markdown("#### 💼 Experience Entries")
                exp_entries = profile.get("experience", [])
                if exp_entries:
                    for exp in exp_entries:
                        st.markdown(f"- {exp}")
                else:
                    st.markdown("*No experience listed*")

                st.divider()
                st.markdown("#### 📊 Match Breakdown")
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    st.markdown(f"**Overall Match:** `{overall_score}%`")
                    st.markdown(f"- **Skills match:** `{breakdown['skills']}%`")
                    st.markdown(f"- **Experience match:** `{breakdown['experience']}%`")
                    st.markdown(f"- **Education match:** `{breakdown['education']}%`")
                    st.markdown(f"- **CGPA match:** `{breakdown['cgpa']}%`")
                    st.markdown(f"- **Projects match:** `{breakdown['projects']}%`")
                with m_col2:
                    raw_matched = candidate["matched_required"]
                    raw_missing = candidate["missing_required"]
                    if raw_matched:
                        st.markdown(f"**Matched Required Skills ({len(raw_matched)}):**")
                        st.markdown(", ".join(f"`{format_skill_name(s)}`" for s in raw_matched))
                    else:
                        st.markdown("**Matched Required Skills:** None")
                    if raw_missing:
                        st.markdown(f"**Missing Required Skills ({len(raw_missing)}):**")
                        st.markdown(", ".join(f"`{format_skill_name(s)}`" for s in raw_missing))
                    else:
                        st.markdown("**Missing Required Skills:** None")

        elif active_view == "interview":
            with st.container(border=True):
                st.markdown("#### 💬 AI Interview Questions Guide")
                
                difficulty = st.selectbox(
                    "Interview Difficulty",
                    ["Easy", "Medium", "Hard"],
                    index=1,
                    key=f"diff_{filename}",
                )

                q_key = f"questions_{filename}"
                if q_key in st.session_state:
                    questions = st.session_state[q_key]

                    def _render_question_set(section_label, q_list):
                        with st.expander(section_label):
                            for idx, q in enumerate(q_list):
                                st.markdown(f"**Q{idx+1}: {q.get('question')}**")
                                st.info(f"💡 **Ideal Answer:**\n{q.get('ideal_answer')}")
                                st.success(f"🎯 **Evaluation Criteria:**\n{q.get('criteria')}")
                                st.divider()

                    _render_question_set("💻 Technical Questions", questions.get("technical", []))
                    _render_question_set("🤝 Behavioral Questions", questions.get("behavioral", []))
                    _render_question_set("🚀 Project-based Questions", questions.get("project", []))
                    _render_question_set("⚠️ Missing Skill Questions", questions.get("missing_skill", []))

                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        pdf_bytes = rag.export_interview_pdf(
                            filename=filename,
                            difficulty=difficulty,
                            questions_data=questions,
                        )
                        st.download_button(
                            label="📄 Export Questions as PDF",
                            data=pdf_bytes,
                            file_name=f"interview_questions_{name}.pdf",
                            mime="application/pdf",
                            key=f"dl_{filename}",
                        )
                    with act_col2:
                        if st.button("🗑 Clear Questions", key=f"clear_q_{filename}"):
                            del st.session_state[q_key]
                            st.rerun()
                else:
                    if not st.session_state.job_profile:
                        render_notification(
                            "Please upload a Job Description to generate custom Interview Questions.",
                            type="warning"
                        )
                    else:
                        if st.button("🤖 Generate Interview Questions", key=f"gen_q_{filename}", type="primary"):
                            with st.spinner("Interview Generator: Formulating custom evaluation questions..."):
                                q_data = rag.generate_interview_questions(
                                    filename=filename,
                                    difficulty=difficulty,
                                )
                            st.session_state[q_key] = q_data
                            st.rerun()

        elif active_view == "hiring":
            with st.container(border=True):
                st.markdown("#### 🤖 AI Hiring Decision Report")
                report_key = f"report_{filename}"

                if report_key in st.session_state:
                    report = st.session_state[report_key]
                    rec = report.get("recommendation", "Borderline")

                    if "strong" in rec.lower():
                        rec_fn = st.success
                    elif "no" in rec.lower():
                        rec_fn = st.error
                    elif "borderline" in rec.lower():
                        rec_fn = st.warning
                    else:
                        rec_fn = st.info

                    rec_fn(f"**{rec}** — Confidence: {report.get('confidence', 50)}%")

                    st.markdown(f"*\"{report.get('summary', '')}\"*")

                    r_col1, r_col2 = st.columns(2)
                    with r_col1:
                        st.markdown("**✔ Key Strengths:**")
                        for s in report.get("strengths", []):
                            st.markdown(f"- {s}")
                    with r_col2:
                        st.markdown("**✖ Areas of Improvement:**")
                        for w in report.get("weaknesses", []):
                            st.markdown(f"- {w}")

                    r_col3, r_col4 = st.columns(2)
                    with r_col3:
                        st.markdown("**⚠️ Risk Factors:**")
                        risks = report.get("risk_factors", [])
                        if risks:
                            for r_item in risks:
                                st.markdown(f"- {r_item}")
                        else:
                            st.markdown("- None identified")
                    with r_col4:
                        st.markdown("**💡 Training Recommendations:**")
                        trainings = report.get("training_recommendations", [])
                        if trainings:
                            for t in trainings:
                                st.markdown(f"- {t}")
                        else:
                            st.markdown("- None required")

                    st.caption(
                        f"**Estimated Ramp-up:** {report.get('estimated_ramp_up_time', 'N/A')} &nbsp;|&nbsp; "
                        f"**Missing Skills:** {', '.join(report.get('missing_skills', [])) or 'None'}"
                    )

                    if st.button("🗑 Clear AI Report", key=f"clear_{filename}"):
                        del st.session_state[report_key]
                        st.rerun()
                else:
                    if not st.session_state.job_profile:
                        render_notification(
                            "Please upload a Job Description to generate a Hiring Decision Report.",
                            type="warning"
                        )
                    else:
                        if st.button("🤖 Generate AI Hiring Decision", key=f"btn_decision_{filename}", type="primary"):
                            with st.spinner("Hiring Decision Engine: Compiling structured assessment report..."):
                                report_data = rag.generate_hiring_decision(filename)
                            st.session_state[report_key] = report_data
                            st.rerun()
