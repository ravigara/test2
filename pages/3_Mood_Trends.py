"""
Page 3 — Mood Trends Dashboard
Charts: 7-day mood line, emotion pie, stress heatmap, sentiment bars, stats panel.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

from database.db import (
    get_checkins, get_journals, get_streak, get_longest_streak,
    get_total_checkins, get_avg_mood_score,
)
from utils.constants import EMOTION_COLOR, STRESS_COLORS

st.set_page_config(
    page_title="Mood Trends | Mitra",
    page_icon="📊",
    layout="wide",
)

from components.sidebar import render_sidebar
render_sidebar()

try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown("""
<style>
.trends-header {
    background: linear-gradient(135deg, rgba(245,166,35,0.15), rgba(27,108,168,0.12));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.trends-header::before {
    content: '📊';
    position: absolute; right: 24px; top: 50%;
    transform: translateY(-50%);
    font-size: 7rem; opacity: 0.06;
}
.trends-header h2 { margin: 0 0 4px 0; color: #f0f4ff !important; }
.trends-header p  { margin: 0; color: #64748b !important; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="trends-header">
    <h2>📊 Your Mood Trends</h2>
    <p>All data is stored privately on your device. No external servers involved.</p>
</div>
""", unsafe_allow_html=True)

# ── Fetch Data ─────────────────────────────────────────────────────────────────
checkins_30 = get_checkins(days=30)
checkins_7  = get_checkins(days=7)
journals_30 = get_journals(days=30)
journals_7  = get_journals(days=7)

df_checkins = pd.DataFrame(checkins_30) if checkins_30 else pd.DataFrame()
df_journals = pd.DataFrame(journals_30) if journals_30 else pd.DataFrame()
df_7        = pd.DataFrame(checkins_7)  if checkins_7  else pd.DataFrame()

# ── Stats Panel ────────────────────────────────────────────────────────────────
st.markdown("### 🏆 Your Wellness Stats")
col1, col2, col3, col4 = st.columns(4)

with col1:
    streak = get_streak()
    st.metric("🔥 Current Streak", f"{streak} day{'s' if streak != 1 else ''}")
with col2:
    longest = get_longest_streak()
    st.metric("🏆 Longest Streak", f"{longest} day{'s' if longest != 1 else ''}")
with col3:
    total = get_total_checkins()
    st.metric("✅ Total Check-ins", total)
with col4:
    avg = get_avg_mood_score()
    st.metric("💛 Average Mood", f"{avg}/10" if avg else "—")

st.markdown("---")

# ── No Data State ──────────────────────────────────────────────────────────────
if df_checkins.empty:
    st.markdown(
        """
        <div style="text-align:center;padding:60px;color:#718096;">
            <div style="font-size:3rem;margin-bottom:16px;">📈</div>
            <h3>No data yet</h3>
            <p>Complete your first daily check-in to start seeing your trends here!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Daily_Checkin.py", label="➡️ Go to Daily Check-In")
    st.stop()

# ── Chart 1: 7-Day Mood Score Line Chart ──────────────────────────────────────
st.markdown("### 📈 7-Day Mood Score")

if not df_7.empty and "mood_score" in df_7.columns and "date" in df_7.columns:
    df_7 = df_7.sort_values("date")
    fig_line = go.Figure()

    # Color bands
    fig_line.add_hrect(y0=7, y1=10, fillcolor="#4CAF82", opacity=0.15, line_width=0, annotation_text="Great", annotation_position="right")
    fig_line.add_hrect(y0=4, y1=7,  fillcolor="#F5A623", opacity=0.15, line_width=0, annotation_text="Okay",  annotation_position="right")
    fig_line.add_hrect(y0=1, y1=4,  fillcolor="#E05C5C", opacity=0.15, line_width=0, annotation_text="Low",   annotation_position="right")

    fig_line.add_trace(go.Scatter(
        x=df_7["date"],
        y=df_7["mood_score"],
        mode="lines+markers+text",
        text=df_7["mood_score"],
        textposition="top center",
        line=dict(color="#1B6CA8", width=3),
        marker=dict(size=10, color="#1B6CA8", line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(27, 108, 168, 0.1)",
    ))

    fig_line.update_layout(
        height=320,
        yaxis=dict(range=[0, 10.5], title="Mood Score", dtick=1,
                   gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        xaxis=dict(title="Date", gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=60, t=10, b=10),
        showlegend=False,
        font=dict(color="#94a3b8"),
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Not enough data for the 7-day chart yet.")

# ── Charts 2 & 3 Side by Side ──────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🎭 Emotion Distribution (30 days)")
    if "detected_mood" in df_checkins.columns:
        emotion_counts = df_checkins["detected_mood"].value_counts().reset_index()
        emotion_counts.columns = ["emotion", "count"]
        colors = [EMOTION_COLOR.get(e, "#95A5A6") for e in emotion_counts["emotion"]]

        fig_pie = go.Figure(go.Pie(
            labels=emotion_counts["emotion"].str.capitalize(),
            values=emotion_counts["count"],
            marker=dict(colors=colors),
            hole=0.4,
            textinfo="label+percent",
        ))
        fig_pie.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            font=dict(color="#94a3b8"),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No emotion data yet.")

with col_right:
    st.markdown("### 🌡️ Stress Levels (30 days)")
    if "stress_level" in df_checkins.columns and "date" in df_checkins.columns:
        stress_map = {"low": 1, "medium": 2, "high": 3}
        df_stress = df_checkins[["date", "stress_level"]].copy()
        df_stress["stress_num"] = df_stress["stress_level"].map(stress_map)
        df_stress = df_stress.sort_values("date")

        stress_colors_list = [
            STRESS_COLORS.get(s, "#95A5A6") for s in df_stress["stress_level"]
        ]

        fig_stress = go.Figure(go.Bar(
            x=df_stress["date"],
            y=df_stress["stress_num"],
            marker_color=stress_colors_list,
            text=df_stress["stress_level"].str.capitalize(),
            textposition="auto",
        ))
        fig_stress.update_layout(
            height=300,
            yaxis=dict(tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"], title="Stress Level",
                       gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
            xaxis=dict(title="Date", gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            font=dict(color="#94a3b8"),
        )
        st.plotly_chart(fig_stress, use_container_width=True)
    else:
        st.info("No stress data yet.")

# ── Chart 4: Journal Sentiment Trend ──────────────────────────────────────────
st.markdown("### 📝 Journal Sentiment (30 days)")

if not df_journals.empty and "sentiment" in df_journals.columns:
    sentiment_counts = df_journals["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    sent_colors = {"positive": "#4CAF82", "neutral": "#F5A623", "negative": "#E05C5C"}

    fig_sent = go.Figure(go.Bar(
        x=sentiment_counts["sentiment"].str.capitalize(),
        y=sentiment_counts["count"],
        marker_color=[sent_colors.get(s, "#95A5A6") for s in sentiment_counts["sentiment"]],
        text=sentiment_counts["count"],
        textposition="auto",
    ))
    fig_sent.update_layout(
        height=260,
        xaxis=dict(title="Sentiment", color="#94a3b8"),
        yaxis=dict(title="Number of Entries", gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        font=dict(color="#94a3b8"),
    )
    st.plotly_chart(fig_sent, use_container_width=True)
else:
    st.info("📝 No journal entries yet. Start journaling to see sentiment trends.")

# ── Chart 5: Emotional Risk Trends (Crisis Detection) ─────────────────────────
st.markdown("### 🛡️ Emotional Risk Trends")
if not df_checkins.empty and "risk_score" in df_checkins.columns and df_checkins["risk_score"].sum() > 0:
    df_risk = df_checkins.sort_values("date")
    fig_risk = go.Figure()
    
    # Add severity bands
    fig_risk.add_hrect(y0=61, y1=100, fillcolor="#ef4444", opacity=0.1, line_width=0, annotation_text="High Risk")
    fig_risk.add_hrect(y0=31, y1=60, fillcolor="#f97316", opacity=0.1, line_width=0, annotation_text="Moderate")
    fig_risk.add_hrect(y0=0, y1=30, fillcolor="#4CAF82", opacity=0.1, line_width=0, annotation_text="Normal")

    fig_risk.add_trace(go.Scatter(
        x=df_risk["date"],
        y=df_risk["risk_score"],
        mode="lines+markers",
        line=dict(color="#ef4444", width=3, shape="spline"),
        marker=dict(size=8, color="#ef4444"),
    ))

    fig_risk.update_layout(
        height=300,
        yaxis=dict(range=[0, 100], title="Risk Score", gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        xaxis=dict(title="Date", gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=60, t=10, b=10),
        showlegend=False,
        font=dict(color="#94a3b8"),
    )
    st.plotly_chart(fig_risk, use_container_width=True)
else:
    st.info("🛡️ No risk data detected yet.")


# ── Recent Check-ins Table ─────────────────────────────────────────────────────
st.markdown("### 📋 Recent Check-ins")
with st.expander("View last 10 entries"):
    if not df_checkins.empty:
        display_cols = ["date", "detected_mood", "mood_score", "energy_level", "stress_level", "notes"]
        available = [c for c in display_cols if c in df_checkins.columns]
        st.dataframe(
            df_checkins[available].head(10).rename(columns={
                "date": "Date", "detected_mood": "Mood", "mood_score": "Score",
                "energy_level": "Energy", "stress_level": "Stress", "notes": "Notes",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No data yet.")
