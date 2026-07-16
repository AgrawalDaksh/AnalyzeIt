import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter


def format_skill_name(skill):
    if not skill:
        return ""
    if len(skill) <= 3:
        return skill.upper()
    return skill.title()


def show_analytics(ranked_candidates, rag):
    """
    Renders the Recruiter Analytics Dashboard using native Streamlit components.
    Uses st.metric() for KPIs and Plotly for charts.
    """
    st.markdown('<div id="section-dashboard"></div>', unsafe_allow_html=True)
    st.markdown("## 📊 Recruiter Analytics Dashboard")

    if not ranked_candidates:
        with st.container(border=True):
            st.subheader("📊 Recruiter Analytics")
            st.info(
                "Upload candidate resumes and a job description to view automated recruiting KPIs and skills charts."
            )
        return

    # ── Calculations ────────────────────────────────────────────────
    total_candidates = len(ranked_candidates)
    avg_score = round(sum(c["score"] for c in ranked_candidates) / total_candidates, 1)
    highest_score = round(max(c["score"] for c in ranked_candidates), 1)
    high_match_count = len([c for c in ranked_candidates if c["score"] >= 80])
    low_match_count = len([c for c in ranked_candidates if c["score"] < 60])

    cgpa_list = [
        c.get("cand_cgpa")
        for c in ranked_candidates
        if c.get("cand_cgpa") is not None
    ]
    avg_cgpa = round(sum(cgpa_list) / len(cgpa_list), 2) if cgpa_list else 0.0
    cgpa_str = f"{avg_cgpa} / 10" if avg_cgpa > 0 else "N/A"

    all_degrees = []
    all_skills = []
    for c in ranked_candidates:
        profile = rag.candidate_profiles.get(c["filename"], {})
        deg = profile.get("degree")
        if deg:
            all_degrees.append(deg.strip().upper())
        for s in profile.get("skills", []):
            if s:
                all_skills.append(format_skill_name(s))

    most_common_degree = Counter(all_degrees).most_common(1)[0][0] if all_degrees else "N/A"
    skill_counts = Counter(all_skills)

    # ── KPI Grid (columns wrapped in border containers) ───────────────
    # Row 1: Candidates, Avg Match, Top Match
    m1, m2, m3 = st.columns(3)
    with m1:
        with st.container(border=True):
            st.metric("👥 Candidates", total_candidates)
    with m2:
        with st.container(border=True):
            st.metric("🎯 Avg Match", f"{avg_score}%")
    with m3:
        with st.container(border=True):
            st.metric("🏆 Top Match", f"{highest_score}%")

    # Row 2: Average CGPA & Top Candidate Degree (extra width to prevent truncation)
    m4, m5 = st.columns([2, 3])
    with m4:
        with st.container(border=True):
            st.metric("⭐ Avg CGPA", cgpa_str)
    with m5:
        with st.container(border=True):
            st.metric("🎓 Top Degree", most_common_degree)

    # Row 3: Fit Status Breakdown
    m6, m7 = st.columns(2)
    with m6:
        with st.container(border=True):
            st.metric("🔥 Top Fits (≥80%)", high_match_count)
    with m7:
        with st.container(border=True):
            st.metric("⚠️ Low Fits (<60%)", low_match_count)

    st.divider()

    # ── Skills Distribution Chart ─────────────────────────────────────
    if skill_counts:
        st.markdown("### 📈 Top Skills Distribution")
        top_skills = skill_counts.most_common(8)
        labels = [s[0] for s in top_skills]
        values = [s[1] for s in top_skills]

        fig = go.Figure(go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(
                color=values,
                colorscale=[[0, "#2563EB"], [0.5, "#4F8CFF"], [1, "#7C5CFC"]],
                showscale=False,
            ),
            text=[f" {v} " for v in values],
            textposition="inside",
            textfont=dict(color="#FFFFFF", size=11),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#94A3B8"),
            margin=dict(l=100, r=20, t=10, b=10),
            height=280,
            xaxis=dict(
                showgrid=False,
                visible=False,
            ),
            yaxis=dict(
                color="#CBD5E1",
                tickfont=dict(size=12, family="Inter", weight="bold"),
                autorange="reversed",
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
