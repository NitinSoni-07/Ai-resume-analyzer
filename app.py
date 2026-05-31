"""
app.py - AI Resume Analyzer | Streamlit Frontend
Full-featured: Upload, Analysis, Job Match, Score, Suggestions + MongoDB storage
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from ai_analyzer import analyze_resume, extract_resume_text, score_label
from database import (
    save_resume_analysis,
    get_all_analyses,
    get_analysis_by_id,
    delete_analysis,
    get_stats,
    check_connection,
)

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800;
}

.main { background: #0a0a0f; }

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%);
    color: #e8e8f0;
}

.metric-card {
    background: linear-gradient(135deg, #13131f 0%, #1a1a2e 100%);
    border: 1px solid rgba(100, 100, 200, 0.2);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: rgba(100, 100, 255, 0.5);
}
.metric-card h2 {
    font-size: 2.2rem;
    margin: 0;
    background: linear-gradient(90deg, #6C63FF, #00C896);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-card p { color: #888; margin: 4px 0 0; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; }

.score-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}

.strength-item {
    background: rgba(0, 200, 150, 0.08);
    border-left: 3px solid #00C896;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.9rem;
}

.weakness-item {
    background: rgba(255, 107, 107, 0.08);
    border-left: 3px solid #FF6B6B;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.9rem;
}

.suggestion-high {
    background: rgba(255, 107, 107, 0.06);
    border: 1px solid rgba(255, 107, 107, 0.3);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0;
}

.suggestion-medium {
    background: rgba(255, 179, 71, 0.06);
    border: 1px solid rgba(255, 179, 71, 0.3);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0;
}

.suggestion-low {
    background: rgba(74, 158, 255, 0.06);
    border: 1px solid rgba(74, 158, 255, 0.3);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0;
}

.skill-tag {
    display: inline-block;
    background: rgba(108, 99, 255, 0.15);
    border: 1px solid rgba(108, 99, 255, 0.4);
    color: #a09cff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    margin: 3px;
    font-weight: 500;
}

.keyword-match {
    display: inline-block;
    background: rgba(0, 200, 150, 0.12);
    border: 1px solid rgba(0, 200, 150, 0.4);
    color: #00C896;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    margin: 2px;
}

.keyword-miss {
    display: inline-block;
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid rgba(255, 107, 107, 0.35);
    color: #FF6B6B;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    margin: 2px;
}

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #c0c0d8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding-bottom: 8px;
    margin-bottom: 14px;
    margin-top: 4px;
}

.stButton > button {
    background: linear-gradient(135deg, #6C63FF 0%, #4A9EFF 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.03em;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
}

.stFileUploader {
    border: 2px dashed rgba(108, 99, 255, 0.4) !important;
    border-radius: 14px !important;
    background: rgba(108, 99, 255, 0.04) !important;
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #0a0a14 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.status-connected {
    color: #00C896;
    font-weight: 600;
    font-size: 0.85rem;
}
.status-disconnected {
    color: #FF6B6B;
    font-weight: 600;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📄 AI Resume Analyzer")
    st.markdown("*Powered by Streamlit & MongoDB*")
    st.divider()

    # DB Status
    db_ok = check_connection()
    if db_ok:
        st.markdown('<span class="status-connected">● MongoDB Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-disconnected">● MongoDB Offline</span>', unsafe_allow_html=True)
        st.caption("Results won't be saved. Start MongoDB to persist data.")

    st.divider()

    page = st.radio(
        "Navigation",
        ["🔍 Analyze Resume", "📊 History", "📈 Dashboard"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Supports PDF, DOCX, TXT")
    st.caption("Max file size: 10 MB")


# ─── Page: Analyze Resume ────────────────────────────────────────────────────
if page == "🔍 Analyze Resume":
    st.markdown("# AI Resume Analyzer")
    st.markdown("Upload a resume and get an instant AI-powered analysis with scores, strengths, job match, and improvement suggestions.")
    st.divider()

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">Upload Resume</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop your resume here",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed"
        )

        st.markdown('<div class="section-header" style="margin-top:20px;">Job Description (Optional)</div>', unsafe_allow_html=True)
        job_desc = st.text_area(
            "Paste the job description for match scoring",
            height=180,
            placeholder="Paste job description here to get a match score and keyword gap analysis...",
            label_visibility="collapsed"
        )

        analyze_btn = st.button("🚀 Analyze Resume", use_container_width=True)

    with col2:
        if uploaded_file:
            st.success(f"✅ File uploaded: **{uploaded_file.name}**")
            st.info(f"Size: {uploaded_file.size / 1024:.1f} KB | Type: {uploaded_file.name.split('.')[-1].upper()}")
        else:
            st.markdown("""
            <div style="background: rgba(108,99,255,0.05); border: 1px solid rgba(108,99,255,0.2);
            border-radius: 14px; padding: 28px; text-align: center; color: #888; margin-top: 0px;">
            <div style="font-size: 2.5rem;">📄</div>
            <div style="font-family: 'Syne', sans-serif; font-weight: 600; margin: 8px 0; color: #aaa;">
            Ready to analyze</div>
            <div style="font-size: 0.85rem;">Upload a resume to get started</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Analyze on click ──
    if analyze_btn:
        if not uploaded_file:
            st.warning("⚠️ Please upload a resume first.")
        else:
            with st.spinner("🤖 Claude is analyzing your resume..."):
                try:
                    resume_text = extract_resume_text(uploaded_file)
                    if len(resume_text) < 100:
                        st.error("❌ Could not extract enough text from the file. Please try a different format.")
                        st.stop()

                    analysis = analyze_resume(resume_text, job_desc)
                    st.session_state["analysis"] = analysis
                    st.session_state["resume_text"] = resume_text
                    st.session_state["filename"] = uploaded_file.name
                    st.session_state["job_desc"] = job_desc

                    # Save to MongoDB
                    doc_id = save_resume_analysis(
                        filename=uploaded_file.name,
                        resume_text=resume_text,
                        analysis=analysis,
                        job_description=job_desc
                    )
                    if doc_id:
                        st.session_state["saved_id"] = doc_id

                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"❌ Error during analysis: {e}")

    # ── Display Results ──
    if "analysis" in st.session_state:
        a = st.session_state["analysis"]
        st.divider()

        # Candidate header
        name = a.get("candidate_name", "Candidate")
        role = a.get("current_role", "")
        level = a.get("career_level", "")
        exp = a.get("experience_years", 0)

        st.markdown(f"## {name}")
        if role:
            st.markdown(f"**{role}** · {level} · {exp} years experience")
        if a.get("summary"):
            st.markdown(f"*{a['summary']}*")

        st.divider()

        # ── Score Cards ──
        cols = st.columns(4)
        overall = a.get("overall_score", 0)
        ats = a.get("ats_score", 0)
        job_match = a.get("job_match_score")
        label_o, color_o = score_label(overall)
        label_a, color_a = score_label(ats)

        with cols[0]:
            st.markdown(f"""<div class="metric-card"><h2>{overall}</h2>
            <p>Overall Score</p></div>""", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""<div class="metric-card"><h2>{ats}</h2>
            <p>ATS Score</p></div>""", unsafe_allow_html=True)
        with cols[2]:
            if job_match is not None:
                st.markdown(f"""<div class="metric-card"><h2>{job_match}</h2>
                <p>Job Match</p></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="metric-card"><h2>—</h2>
                <p>Job Match</p></div>""", unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f"""<div class="metric-card"><h2>{exp}y</h2>
            <p>Experience</p></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Section Scores Radar Chart ──
        col_chart, col_skills = st.columns([1, 1], gap="large")

        with col_chart:
            st.markdown('<div class="section-header">Section Scores</div>', unsafe_allow_html=True)
            sec = a.get("section_scores", {})
            if sec:
                categories = list(sec.keys())
                values = list(sec.values())
                labels = [c.replace("_", " ").title() for c in categories]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=labels + [labels[0]],
                    fill='toself',
                    fillcolor='rgba(108, 99, 255, 0.15)',
                    line=dict(color='#6C63FF', width=2),
                    name='Score'
                ))
                fig.update_layout(
                    polar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        radialaxis=dict(visible=True, range=[0, 100],
                                       gridcolor='rgba(255,255,255,0.08)',
                                       tickcolor='rgba(255,255,255,0.3)',
                                       tickfont=dict(color='#888', size=10)),
                        angularaxis=dict(gridcolor='rgba(255,255,255,0.08)',
                                         tickfont=dict(color='#ccc', size=11))
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=280,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_skills:
            st.markdown('<div class="section-header">Top Skills</div>', unsafe_allow_html=True)
            skills = a.get("top_skills", [])
            if skills:
                skills_html = "".join([f'<span class="skill-tag">{s}</span>' for s in skills])
                st.markdown(skills_html, unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:20px;">Recommended Roles</div>', unsafe_allow_html=True)
            roles = a.get("recommended_roles", [])
            if roles:
                for r in roles:
                    st.markdown(f"→ {r}")

        st.divider()

        # ── Strengths & Weaknesses ──
        col_s, col_w = st.columns(2, gap="large")
        with col_s:
            st.markdown('<div class="section-header">✅ Strengths</div>', unsafe_allow_html=True)
            for s in a.get("strengths", []):
                st.markdown(f'<div class="strength-item">{s}</div>', unsafe_allow_html=True)

        with col_w:
            st.markdown('<div class="section-header">⚠️ Areas to Improve</div>', unsafe_allow_html=True)
            for w in a.get("weaknesses", []):
                st.markdown(f'<div class="weakness-item">{w}</div>', unsafe_allow_html=True)

        st.divider()

        # ── Suggestions ──
        st.markdown('<div class="section-header">💡 Improvement Suggestions</div>', unsafe_allow_html=True)
        suggestions = a.get("suggestions", [])
        for sug in suggestions:
            p = sug.get("priority", "Low")
            css_class = f"suggestion-{p.lower()}"
            badge_color = {"High": "#FF6B6B", "Medium": "#FFB347", "Low": "#4A9EFF"}.get(p, "#888")
            st.markdown(f"""
            <div class="{css_class}">
                <span style="color:{badge_color}; font-weight:700; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.05em;">{p} Priority</span>
                <span style="color:#888; font-size:0.78rem;"> · {sug.get('area','')}</span>
                <div style="margin-top:6px; font-size:0.92rem; color:#ddd;">{sug.get('suggestion','')}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── ATS Issues ──
        ats_issues = a.get("ats_issues", [])
        if ats_issues:
            st.divider()
            st.markdown('<div class="section-header">🤖 ATS Issues Detected</div>', unsafe_allow_html=True)
            for issue in ats_issues:
                st.warning(f"⚠️ {issue}")

        # ── Job Match ──
        if job_match is not None:
            st.divider()
            st.markdown('<div class="section-header">🎯 Job Match Analysis</div>', unsafe_allow_html=True)
            if a.get("job_match_summary"):
                st.info(a["job_match_summary"])

            col_m, col_miss = st.columns(2)
            with col_m:
                st.markdown("**✅ Matching Keywords**")
                kws = a.get("matching_keywords", [])
                if kws:
                    html = "".join([f'<span class="keyword-match">{k}</span>' for k in kws])
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    st.caption("No matches found")

            with col_miss:
                st.markdown("**❌ Missing Keywords**")
                mkws = a.get("missing_keywords", [])
                if mkws:
                    html = "".join([f'<span class="keyword-miss">{k}</span>' for k in mkws])
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    st.caption("No critical gaps")


# ─── Page: History ───────────────────────────────────────────────────────────
elif page == "📊 History":
    st.markdown("# Analysis History")
    st.markdown("All previously analyzed resumes stored in MongoDB.")
    st.divider()

    records = get_all_analyses(limit=50)

    if not records:
        st.info("No resume analyses found. Upload and analyze a resume first.")
    else:
        for doc in records:
            a = doc.get("analysis", {})
            name = a.get("candidate_name", "Unknown")
            score = a.get("overall_score", 0)
            role = a.get("current_role", "—")
            ts = doc.get("created_at", "")
            filename = doc.get("filename", "—")
            label, color = score_label(score)

            with st.expander(f"**{name}** — {filename} — Score: {score}/100"):
                cols = st.columns([1,1,1,1])
                cols[0].metric("Overall", f"{score}/100")
                cols[1].metric("ATS Score", f"{a.get('ats_score',0)}/100")
                cols[2].metric("Experience", f"{a.get('experience_years',0)} yrs")
                cols[3].metric("Role", role[:20] if role else "—")

                if a.get("top_skills"):
                    st.markdown("**Skills:** " + " · ".join(a["top_skills"]))

                if a.get("summary"):
                    st.caption(a["summary"])

                if st.button(f"🗑️ Delete", key=f"del_{doc['_id']}"):
                    if delete_analysis(doc["_id"]):
                        st.success("Deleted!")
                        st.rerun()


# ─── Page: Dashboard ─────────────────────────────────────────────────────────
elif page == "📈 Dashboard":
    st.markdown("# Analytics Dashboard")
    st.markdown("Aggregate insights from all analyzed resumes.")
    st.divider()

    stats = get_stats()
    records = get_all_analyses(limit=100)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><h2>{stats.get('total_resumes', 0)}</h2>
        <p>Total Resumes</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><h2>{stats.get('avg_score', 0)}</h2>
        <p>Avg Score</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><h2>{len(records)}</h2>
        <p>This Session</p></div>""", unsafe_allow_html=True)

    if records:
        st.divider()
        df_data = []
        for doc in records:
            a = doc.get("analysis", {})
            df_data.append({
                "Name": a.get("candidate_name", "Unknown"),
                "Score": a.get("overall_score", 0),
                "ATS": a.get("ats_score", 0),
                "Experience": a.get("experience_years", 0),
                "Level": a.get("career_level", "Unknown"),
                "Date": doc.get("created_at", ""),
            })

        df = pd.DataFrame(df_data)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-header">Score Distribution</div>', unsafe_allow_html=True)
            fig = px.histogram(df, x="Score", nbins=10,
                               color_discrete_sequence=["#6C63FF"])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#aaa', height=250,
                margin=dict(t=10,b=10,l=10,r=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">Career Level Breakdown</div>', unsafe_allow_html=True)
            level_counts = df["Level"].value_counts().reset_index()
            level_counts.columns = ["Level", "Count"]
            fig2 = px.pie(level_counts, values="Count", names="Level",
                          color_discrete_sequence=px.colors.sequential.Plasma)
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#aaa', height=250,
                margin=dict(t=10,b=10,l=10,r=10)
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-header">Score vs Experience</div>', unsafe_allow_html=True)
        fig3 = px.scatter(df, x="Experience", y="Score", color="Level",
                          size="Score", hover_name="Name",
                          color_discrete_sequence=px.colors.qualitative.Vivid)
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#aaa', height=300,
            margin=dict(t=10,b=10,l=10,r=10)
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data yet. Analyze some resumes to see dashboard insights.")
