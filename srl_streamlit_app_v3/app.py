
import math
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud

st.set_page_config(page_title="Learning Progress Dashboard", layout="wide")

# ============================ Simulated Data (student-friendly) ============================
GOALS = [
    {
        "goal_id": "Goal 1",
        "title": "Identify and Describe Cell Structures",
        "unit": "Cells – Plant and Animal",
        "start_date": "2025-10-15",
        "target_date": "2025-11-15",
        "priority": 1,
        "stars": 4,
        "status": "in progress",
    },
    {
        "goal_id": "Goal 2",
        "title": "Compare Plant and Animal Cells",
        "unit": "Cells – Plant and Animal",
        "start_date": "2025-10-10",
        "target_date": "2025-11-01",
        "priority": 2,
        "stars": 3,
        "status": "completed",
    },
    {
        "goal_id": "Goal 3",
        "title": "Explain Cell Specialisation",
        "unit": "Cells – Specialised Cells and Adaptations",
        "start_date": "2025-10-20",
        "target_date": "2025-11-20",
        "priority": 1,
        "stars": 5,
        "status": "in progress",
    },
]

# Two clear tasks for each goal, written in simple words
TASKS = [
    # Goal 1
    {
        "task_id": "T1",
        "goal_id": "Goal 1",
        "title": "Label cell parts on plant and animal diagrams (cell wall, cell membrane, cytoplasm, nucleus, vacuole, chloroplast, mitochondria, ribosomes).",
        "est_mins": 30,
        "act_mins": 32,
        "completed": True,
        "effort": 4,
    },
    {
        "task_id": "T2",
        "goal_id": "Goal 1",
        "title": "Write in your own words what each cell part does.",
        "est_mins": 25,
        "act_mins": 0,
        "completed": False,
        "effort": 3,
    },

    # Goal 2
    {
        "task_id": "T3",
        "goal_id": "Goal 2",
        "title": "Make a table to show how plant and animal cells are similar and different.",
        "est_mins": 25,
        "act_mins": 28,
        "completed": True,
        "effort": 4,
    },
    {
        "task_id": "T4",
        "goal_id": "Goal 2",
        "title": "Write a short paragraph to explain why the differences make sense for plants and animals.",
        "est_mins": 20,
        "act_mins": 24,
        "completed": True,
        "effort": 3,
    },

    # Goal 3
    {
        "task_id": "T5",
        "goal_id": "Goal 3",
        "title": "Match examples of special cells (root hair cell, red blood cell, muscle cell) to their special features.",
        "est_mins": 20,
        "act_mins": 22,
        "completed": True,
        "effort": 3,
    },
    {
        "task_id": "T6",
        "goal_id": "Goal 3",
        "title": "Write how each special feature helps the cell do its job well.",
        "est_mins": 30,
        "act_mins": 0,
        "completed": False,
        "effort": 5,
    },
]

# Attempts and reflections use easy words and match the goals
ATTEMPTS = [
    # Goal 1
    {
        "attempt_id": "A1",
        "goal_id": "Goal 1",
        "activity_title": "Cell parts labelling quiz 1",
        "timestamp": "2025-10-22T10:00:00",
        "score": 56,
        "error_tags": ["confused about cell membrane", "labelling error"],
        "time_spent_mins": 12,
    },
    {
        "attempt_id": "A2",
        "goal_id": "Goal 1",
        "activity_title": "Cell parts labelling quiz 2",
        "timestamp": "2025-10-25T14:30:00",
        "score": 61,
        "error_tags": ["confused about cell membrane", "incomplete answer"],
        "time_spent_mins": 15,
    },
    {
        "attempt_id": "A3",
        "goal_id": "Goal 1",
        "activity_title": "Plant and animal cells test",
        "timestamp": "2025-10-28T09:15:00",
        "score": 74,
        "error_tags": ["labelling error"],
        "time_spent_mins": 18,
    },

    # Goal 2
    {
        "attempt_id": "A4",
        "goal_id": "Goal 2",
        "activity_title": "Compare plant and animal cells quiz",
        "timestamp": "2025-10-30T11:00:00",
        "score": 79,
        "error_tags": ["incomplete answer"],
        "time_spent_mins": 14,
    },
    {
        "attempt_id": "A10",
        "goal_id": "Goal 2",
        "activity_title": "Comparison retest",
        "timestamp": "2025-11-04T14:00:00",
        "score": 92,
        "error_tags": [],
        "time_spent_mins": 15,
    },

    # Goal 3
    {
        "attempt_id": "A6",
        "goal_id": "Goal 3",
        "activity_title": "Special cells matching practice",
        "timestamp": "2025-10-24T16:00:00",
        "score": 68,
        "error_tags": ["labelling error", "size/shape not right"],
        "time_spent_mins": 22,
    },
    {
        "attempt_id": "A7",
        "goal_id": "Goal 3",
        "activity_title": "Special cells drawing practice",
        "timestamp": "2025-10-27T10:30:00",
        "score": 75,
        "error_tags": ["size/shape not right"],
        "time_spent_mins": 19,
    },
    {
        "attempt_id": "A8",
        "goal_id": "Goal 3",
        "activity_title": "Special cells label test",
        "timestamp": "2025-11-01T15:45:00",
        "score": 81,
        "error_tags": ["small detail missing"],
        "time_spent_mins": 16,
    },
    {
        "attempt_id": "A5",
        "goal_id": "Goal 1",
        "activity_title": "Final cell parts quiz",
        "timestamp": "2025-11-02T13:20:00",
        "score": 82,
        "error_tags": [],
        "time_spent_mins": 20,
    },
    {
        "attempt_id": "A9",
        "goal_id": "Goal 1",
        "activity_title": "Review quiz on cell parts",
        "timestamp": "2025-11-03T09:00:00",
        "score": 88,
        "error_tags": [],
        "time_spent_mins": 18,
    },
]

REFLECTIONS = [
    # Goal 1
    {
        "reflection_id": "R1",
        "goal_id": "Goal 1",
        "activity_title": "Cell parts labelling quiz 1",
        "timestamp": "2025-10-22T10:30:00",
        "free_text": "I mixed up the job of the cell membrane. Drawing should help me see the differences better.",
        "self_eval_confidence": 2,
        "self_eval_difficulty": 4,
        "self_eval_satisfaction": 2,
        "strategy_tags": ["re reading notes", "drawing pictures"],
        "feeling": -0.1,
    },
    {
        "reflection_id": "R2",
        "goal_id": "Goal 1",
        "activity_title": "Cell parts labelling quiz 2",
        "timestamp": "2025-10-25T15:00:00",
        "free_text": "Drawing helped me picture the parts. Self testing showed I still need to learn chloroplast uses.",
        "self_eval_confidence": 3,
        "self_eval_difficulty": 3,
        "self_eval_satisfaction": 4,
        "strategy_tags": ["drawing pictures", "self testing"],
        "feeling": 0.4,
    },
    {
        "reflection_id": "R3",
        "goal_id": "Goal 1",
        "activity_title": "Plant and animal cells test",
        "timestamp": "2025-10-28T10:00:00",
        "free_text": "Saying the ideas out loud made them clearer. I felt more sure of myself.",
        "self_eval_confidence": 4,
        "self_eval_difficulty": 2,
        "self_eval_satisfaction": 5,
        "strategy_tags": ["talking it out", "drawing pictures", "self testing"],
        "feeling": 0.6,
    },

    # Goal 2
    {
        "reflection_id": "R4",
        "goal_id": "Goal 2",
        "activity_title": "Compare plant and animal cells quiz",
        "timestamp": "2025-10-30T11:30:00",
        "free_text": "Putting the steps in my own words helped. I should not just scroll quickly through notes.",
        "self_eval_confidence": 4,
        "self_eval_difficulty": 3,
        "self_eval_satisfaction": 4,
        "strategy_tags": ["write in my own words", "quick scrolling"],
        "feeling": 0.3,
    },

    # Goal 3
    {
        "reflection_id": "R5",
        "goal_id": "Goal 3",
        "activity_title": "Special cells drawing practice",
        "timestamp": "2025-10-27T11:00:00",
        "free_text": "Drawing again and again is tiring but it works. Guessing labels does not help me learn.",
        "self_eval_confidence": 3,
        "self_eval_difficulty": 3,
        "self_eval_satisfaction": 3,
        "strategy_tags": ["drawing pictures", "guessing answers"],
        "feeling": 0.2,
    },
    {
        "reflection_id": "R6",
        "goal_id": "Goal 3",
        "activity_title": "Special cells label test",
        "timestamp": "2025-11-01T16:15:00",
        "free_text": "Testing myself with blank pictures was great. I feel ready.",
        "self_eval_confidence": 5,
        "self_eval_difficulty": 2,
        "self_eval_satisfaction": 5,
        "strategy_tags": ["self testing", "drawing pictures", "talking it out"],
        "feeling": 0.5,
    },
]

# ============================ Helpers ============================
def within_range(ts, start, end):
    return pd.to_datetime(ts) >= pd.to_datetime(start) and pd.to_datetime(
        ts
    ) <= pd.to_datetime(end)


def goal_progress(goals, tasks):
    rows = []
    for g in goals:
        g_tasks = [t for t in tasks if t["goal_id"] == g["goal_id"]]
        total_effort = sum(t["effort"] for t in g_tasks) or 1
        done_effort = sum(t["effort"] for t in g_tasks if t["completed"])
        pct = (done_effort / total_effort) * 100.0
        rows.append(
            {**g, "totalEffort": total_effort, "doneEffort": done_effort, "pct": pct}
        )
    return pd.DataFrame(rows)


def error_frequency(attempts, start, end):
    counts = {}
    for a in attempts:
        if within_range(a["timestamp"], start, end):
            for tag in a["error_tags"]:
                counts.setdefault(tag, []).append(
                    {
                        "activity": a["activity_title"],
                        "date": pd.to_datetime(a["timestamp"]).strftime("%b %d"),
                        "goal_id": a["goal_id"],
                    }
                )
    data = [{"error": k, "count": len(v), "details": v} for k, v in counts.items()]
    return pd.DataFrame(data)


def time_by_goal(attempts, goals):
    rows = []
    for g in goals:
        g_attempts = [a for a in attempts if a["goal_id"] == g["goal_id"]]
        time_sum = sum(a["time_spent_mins"] for a in g_attempts)
        rows.append(
            {
                "goal_id": g["goal_id"],
                "title": g["title"],
                "time": time_sum,
                "attempts": len(g_attempts),
            }
        )
    return pd.DataFrame(rows)


def self_eval_for_goal(reflections, goal_id):
    rs = [r for r in reflections if r["goal_id"] == goal_id]
    if not rs:
        return {"confidence": 0, "difficulty": 0, "satisfaction": 0}
    avg_conf = np.mean([r["self_eval_confidence"] for r in rs]) / 5.0 * 100
    avg_diff = np.mean([r["self_eval_difficulty"] for r in rs]) / 5.0 * 100
    avg_sat = np.mean([r["self_eval_satisfaction"] for r in rs]) / 5.0 * 100
    return {"confidence": avg_conf, "difficulty": avg_diff, "satisfaction": avg_sat}


def actual_radar(tasks, attempts, reflections, start, end):
    # Forethought: percent of tasks marked complete
    total = len(tasks)
    complete = len([t for t in tasks if t["completed"]])
    fore = (complete / total) * 100 if total else 0
    # Performance: percent of last 10 attempts without errors in the selected time
    filt_attempts = [a for a in attempts if within_range(a["timestamp"], start, end)]
    last10 = filt_attempts[-10:]
    errorfree = len([a for a in last10 if len(a["error_tags"]) == 0])
    perf = (errorfree / len(last10) * 100) if last10 else 0
    # Reflection: percent of reflections with positive feeling
    filt_refl = [r for r in reflections if within_range(r["timestamp"], start, end)]
    pos = len([r for r in filt_refl if r["feeling"] > 0])
    refl = (pos / len(filt_refl) * 100) if filt_refl else 0
    return [
        {"phase": "Forethought", "score": round(fore)},
        {"phase": "Performance", "score": round(perf)},
        {"phase": "Reflection", "score": round(refl)},
    ]


def wordcloud_image(reflections, goal_filter=None):
    freq = {}
    for r in reflections:
        if goal_filter in (None, "ALL") or r["goal_id"] == goal_filter:
            for t in r["strategy_tags"]:
                freq[t] = freq.get(t, 0) + 1
    if not freq:
        freq = {"no data": 1}
    wc = WordCloud(width=640, height=340, background_color="white")
    wc.generate_from_frequencies(freq)
    return wc.to_image()


# ====== Chat: per-phase 15-turn limit, with seeded 15 lines + 16th "limit hit" note ======
if "chat" not in st.session_state:
    st.session_state.chat = {"forethought": [], "performance": [], "reflection": []}

def seeded_lines(phase_name):
    # 15 alternating lines (agent/user), simple language + 16th agent cap message
    convo = [
        ("agent", f"Welcome to {phase_name.capitalize()}! Pick one goal to focus on today and say why."),
        ("user", "I choose Goal 1 because I still mix up some parts."),
        ("agent", "Great choice. How sure do you feel, from 1 (not sure) to 5 (very sure)?"),
        ("user", "Maybe 2."),
        ("agent", "What is your first small step? Keep it simple."),
        ("user", "I will label a plant cell picture."),
        ("agent", "Nice. When will you do it? Give a short time box."),
        ("user", "I will spend 10 minutes now."),
        ("agent", "Good plan. What could stop you, and what will you do about it?"),
        ("user", "I get stuck on terms. I will use the glossary my teacher gave."),
        ("agent", "Say one success sign you will look for after 10 minutes."),
        ("user", "I can label at least five parts correctly."),
        ("agent", "Last check: which strategy will you use first (drawing, self testing, or talking it out)?"),
        ("user", "Drawing first."),
        ("agent", "You are set. Click Refresh after you finish so the charts update."),
        ("agent", "You have reached the 15-message limit for this phase. Please ask your teacher if you need more help.")
    ]
    return convo

if "seed_done" not in st.session_state:
    st.session_state.seed_done = False

def seed_once():
    if not st.session_state.seed_done:
        st.session_state.chat["forethought"] = seeded_lines("plan")
        st.session_state.chat["performance"] = [
            ("agent", "Check your recent work. Which mistake shows up the most?"),
            ("user", "Labelling mistakes show up a lot."),
            ("agent", "Pick one mistake type to fix next. What is your plan?"),
            ("user", "I will check labels using a checklist after each question."),
            ("agent", "Strong plan. Do you want a short 10-minute review now?"),
            ("user", "Yes, 10 minutes."),
            ("agent", "Good. What will you review first?"),
            ("user", "Cell membrane and cell wall differences."),
            ("agent", "After review, try one quick quiz. What score will you aim for?"),
            ("user", "I will aim for 70 or more."),
            ("agent", "If you make a mistake, what will you do next?"),
            ("user", "I will write the right label and one reason."),
            ("agent", "Nice move. Keep going and watch your time."),
            ("user", "Okay, starting now."),
            ("agent", "Refresh to update your charts when you finish."),
            ("agent", "You have reached the 15-message limit for this phase. Please ask your teacher if you need more help.")
        ]
        st.session_state.chat["reflection"] = [
            ("agent", "Think back. Which study habit helped you the most?"),
            ("user", "Testing myself with blank pictures."),
            ("agent", "Why did it help? Say it in one line."),
            ("user", "It showed me what I really did not know."),
            ("agent", "What will you stop doing next time?"),
            ("user", "Stop guessing labels."),
            ("agent", "What is one small change you will try next?"),
            ("user", "I will speak my answers out loud."),
            ("agent", "How did you feel about your learning today? (one word is fine)"),
            ("user", "More confident."),
            ("agent", "Write one takeaway I can pin to the overview."),
            ("user", "Drawing and self testing together work best for me."),
            ("agent", "Nice. What is your next step for tomorrow?"),
            ("user", "Finish the paragraph for Goal 2."),
            ("agent", "Great. See you next time."),
            ("agent", "You have reached the 15-message limit for this phase. Please ask your teacher if you need more help.")
        ]
        st.session_state.seed_done = True

seed_once()

def chat_tab(phase):
    msgs = st.session_state.chat[phase]
    st.subheader(f"{phase.capitalize()} Coach (max 15 messages)")
    for role, text in msgs:
        st.write(f"**{'Coach' if role=='agent' else 'You'}:** {text}")
    # Count user messages (interactions from student)
    turns = sum(1 for r, _ in msgs if r == "user")
    if turns >= 15:
        st.warning("You have hit the 15-message limit for this phase. Please check with your teacher for more help.")
        disabled = True
    else:
        disabled = False
    user = st.text_input(f"Your reply ({phase})", disabled=disabled, key=f"in_{phase}")
    if st.button(f"Send ({phase})", disabled=disabled or not user.strip()):
        msgs.append(("user", user.strip()))
        # Keep conversation simple: coach replies with a short nudge
        msgs.append(("agent", "Thanks. Keep going. Refresh the page after you act so the charts update."))
        st.session_state.chat[phase] = msgs
        st.experimental_rerun()
    st.caption(f"Messages you sent in this phase: {turns}/15")

# ===== Controls =====
st.title("Self-Regulated Learning Dashboard")
st.caption("Plan → Do → Reflect. Simple charts and short tips to help you learn.")

# Data source banner
with st.expander("Where does the data come from?"):
    st.markdown(
        "- **Goals and tasks**: set by your teacher and you.\n"
        "- **Attempts**: your quizzes and practice work (with time spent and common mistakes).\n"
        "- **Reflections**: short notes you write after activities.\n"
        "These power the charts on this page."
    )

# Global filters + Refresh
colA, colB, colC, colD = st.columns([1, 1, 1, 0.7])
with colA:
    goal_options = ["ALL"] + [g["goal_id"] for g in GOALS]
    sel_goal = st.selectbox("Pick a goal", goal_options, index=1, help="Choose a goal to focus the visuals.")
with colB:
    start = st.date_input("Start date", value=pd.to_datetime("2025-10-22"))
with colC:
    end = st.date_input("End date", value=pd.to_datetime("2025-11-04"))
with colD:
    st.write("")
    if st.button("🔁 Refresh visuals"):
        st.rerun()

start_str = pd.to_datetime(start).strftime("%Y-%m-%d")
end_str = pd.to_datetime(end).strftime("%Y-%m-%d")

# ============================ Overview Radar with tooltips ============================
st.subheader("Overview • SRL Radar (Expected vs Actual)")

expected = [
    {"phase": "Forethought", "score": 80},
    {"phase": "Performance", "score": 85},
    {"phase": "Reflection", "score": 75},
]
actual = actual_radar(TASKS, ATTEMPTS, REFLECTIONS, start_str, end_str)

# Tooltip text for formulas
radar_tooltips = {
    "Forethought": "Completed tasks ÷ Total tasks × 100",
    "Performance": "Error-free attempts (last 10 in date range) ÷ Attempts checked × 100",
    "Reflection": "Positive feelings ÷ All reflections × 100",
}

def radar_trace(data, name, color):
    theta = [pt["phase"] for pt in data] + [data[0]["phase"]]
    r = [pt["score"] for pt in data] + [data[0]["score"]]
    tips = [radar_tooltips[pt["phase"]] for pt in data] + [radar_tooltips[data[0]["phase"]]]
    return go.Scatterpolar(
        r=r,
        theta=theta,
        fill="toself",
        name=name,
        line=dict(color=color),
        customdata=tips,
        hovertemplate="<b>%{theta}</b><br>Score: %{r}%<br><i>Formula:</i> %{customdata}<extra></extra>"
    )

fig = go.Figure()
fig.add_trace(radar_trace(expected, "Expected", "rgba(100,116,139,0.6)"))
fig.add_trace(radar_trace(actual, "Actual", "rgba(245,158,11,0.6)"))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=True,
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(title="Hover a phase label in the chart to see the formula:\n"
                      "• Forethought = completed tasks ÷ total tasks × 100\n"
                      "• Performance = error-free attempts ÷ attempts checked × 100\n"
                      "• Reflection = positive feelings ÷ all reflections × 100")
)
st.plotly_chart(fig, use_container_width=True)

# ============================ Three Phase Tabs ============================
tab_fore, tab_perf, tab_refl = st.tabs(
    ["Phase 1 • Plan", "Phase 2 • Do", "Phase 3 • Reflect"]
)

with tab_fore:
    st.header("Plan (set simple steps)")
    prog_df = goal_progress(GOALS, TASKS)

    # Build a date range column and drop percentage
    prog_df["Date range"] = prog_df["start_date"] + " → " + prog_df["target_date"]

    # Friendly column names (no percent column shown)
    pretty = prog_df.rename(columns={
        "goal_id": "Goal",
        "title": "Goal title",
        "doneEffort": "Done effort",
        "totalEffort": "Total effort"
    })[["Goal", "Goal title", "Date range", "Done effort", "Total effort"]]

    st.dataframe(pretty)
    with st.expander("How are these numbers worked out? (tap for formula)"):
        st.markdown(
            "- **Total effort** = add up the effort points for all tasks under the goal.\n"
            "- **Done effort** = add up the effort points for tasks marked complete."
        )

    st.subheader("Progress by Task (picked goal)")
    g = next(
        (x for x in GOALS if x["goal_id"] == (sel_goal if sel_goal != "ALL" else "Goal 1")),
        GOALS[0],
    )
    window_days = max(
        1,
        (
            pd.to_datetime(min(g["target_date"], end_str))
            - pd.to_datetime(max(g["start_date"], start_str))
        ).days
        or 1,
    )
    sel_tasks = [t for t in TASKS if t["goal_id"] == g["goal_id"]]
    total_effort = sum(t["effort"] for t in sel_tasks) or 1
    rows = []
    for t in sel_tasks:
        share = t["effort"] / total_effort
        estimated_days = window_days * share
        ratio = (t["act_mins"] / t["est_mins"]) if t["est_mins"] else 0
        actual_days = min(estimated_days, estimated_days * ratio)
        rows.append({
            "task": t["title"],
            "Estimated Days": estimated_days,
            "Actual Days": actual_days,
            "formula": "Estimated Days = Time window × (Task effort ÷ Total effort); Actual Days = Estimated Days × (Actual minutes ÷ Planned minutes)"
        })
    bars_df = pd.DataFrame(rows).melt(
        id_vars=["task", "formula"],
        value_vars=["Estimated Days", "Actual Days"],
        var_name="Type",
        value_name="Days",
    )
    fig_bars = px.bar(bars_df, x="Days", y="task", color="Type", orientation="h",
                      hover_data={"formula": True, "Days": ":.2f", "task": False, "Type": False})
    fig_bars.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.2f} days<br><i>Formula:</i> %{customdata[0]}<extra></extra>")
    st.plotly_chart(fig_bars, use_container_width=True)

    chat_tab("forethought")

with tab_perf:
    st.header("Do (watch mistakes and time)")
    ef_df = error_frequency(ATTEMPTS, start_str, end_str)
    if not ef_df.empty:
        fig_err = px.bar(
            ef_df.sort_values("count", ascending=True),
            x="count",
            y="error",
            orientation="h",
            labels={"count": "Number of times", "error": "Common mistake"},
            hover_data={"count": True, "error": True}
        )
        fig_err.update_traces(hovertemplate="<b>%{y}</b><br>Times seen: %{x}<br><i>Tip:</i> Fix one mistake type at a time.<extra></extra>")
        st.plotly_chart(fig_err, use_container_width=True)
    else:
        st.info("No mistakes found in the chosen dates.")

    tbg_df = time_by_goal(ATTEMPTS, GOALS)
    fig_time = px.bar(
        tbg_df,
        x="goal_id",
        y="time",
        hover_data=["title", "attempts"],
        labels={"goal_id": "Goal", "time": "Minutes", "attempts": "Activities counted"}
    )
    fig_time.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Minutes: %{y}<br>Activities: %{customdata[1]}<br><i>Formula:</i> add all minutes from attempts for this goal.<extra></extra>")
    st.plotly_chart(fig_time, use_container_width=True)

    chat_tab("performance")

with tab_refl:
    st.header("Reflect (what worked, what to change)")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Strategy word cloud")
        img = wordcloud_image(
            REFLECTIONS, goal_filter=None if sel_goal == "ALL" else sel_goal
        )
        st.image(
            img,
            caption="Bigger words = used more often."
        )
    with c2:
        st.subheader("Your reflection notes")
        df_show = pd.DataFrame(REFLECTIONS)[
            ["goal_id", "activity_title", "feeling", "strategy_tags", "free_text"]
        ].rename(columns={"feeling": "feeling (−1 to +1)"})
        st.dataframe(df_show)

    st.subheader("Feelings over time")
    sent_series = [
        {"idx": i + 1, "feeling": r["feeling"]} for i, r in enumerate(REFLECTIONS)
    ]
    fig_sent = px.line(pd.DataFrame(sent_series), x="idx", y="feeling", markers=True,
                       labels={"idx": "Reflection number", "feeling": "Feeling (−1 to +1)"})
    fig_sent.update_yaxes(range=[-1, 1])
    fig_sent.update_traces(hovertemplate="Reflection #%{x}<br>Feeling: %{y}<br><i>Note:</i> closer to +1 means more positive.<extra></extra>")
    st.plotly_chart(fig_sent, use_container_width=True)

    chat_tab("reflection")

st.caption(
    "ⓘ Data source: goals, tasks, attempts, and reflections on this page. "
    "Charts use simple math; hover or open the help boxes to see how we work them out."
)
