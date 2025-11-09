
import math
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
from collections import Counter

st.set_page_config(page_title="Learning Progress Dashboard", layout="wide")

# ============== Global CSS: Arial body 22, headers 26 bold ==============
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: Arial, sans-serif !important;
        font-size: 22px !important;
        line-height: 1.35;
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-size: 26px !important;
        font-weight: 700 !important;
        font-family: Arial, sans-serif !important;
    }
    [data-testid="stMarkdownContainer"] * {
        font-size: 22px !important;
    }
    .stButton button, .stSelectbox, .stDateInput, .stTextInput input {
        font-size: 22px !important;
        font-family: Arial, sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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


def error_frequency(attempts, start, end, goal_filter=None):
    counts = {}
    for a in attempts:
        if (goal_filter in (None, "ALL") or a["goal_id"] == goal_filter) and within_range(a["timestamp"], start, end):
            for tag in a["error_tags"]:
                counts.setdefault(tag, 0)
                counts[tag] += 1
    data = [{"error": k, "count": v} for k, v in counts.items()]
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


# ====== Chat state (per-phase 15-turn limit + overall coach) ======
if "chat" not in st.session_state:
    st.session_state.chat = {"forethought": [], "performance": [], "reflection": [], "overall": []}
if "seed_done" not in st.session_state:
    st.session_state.seed_done = False

def scripted_pairs(pairs):
    """Helper to ensure exactly the given scripted conversation list is set."""
    return list(pairs)

# Seed 15 student lines in every chat that surface research themes:
def seed_once():
    if not st.session_state.seed_done:
        # -------------------- OVERALL (15 user lines) --------------------
        overall = scripted_pairs([
            ("agent", "Overview: I look at your goals, scores, time, and notes to help you plan and trust the numbers."),
            ("user", "I see the radar but I am not sure what each point means."),
            ("agent", "Hover to see how each point is worked out. For example, Forethought = completed tasks ÷ total tasks × 100."),
            ("user", "So if I complete one more task does the Forethought score go up?"),
            ("agent", "Yes. It will rise because the completed part becomes bigger."),
            ("user", "I used to think a bigger area always means I am learning more. Is that true?"),
            ("agent", "Not always. Bigger can mean effort is spent, but we check errors and reflections too for real progress."),
            ("user", "Where do these numbers come from? Teacher marks or my own work?"),
            ("agent", "From your tasks and attempts in this class. The time and errors come from your quizzes and practice."),
            ("user", "Can the numbers be wrong if I forgot to start the quiz timer?"),
            ("agent", "Time could be off, yes. The chart shows what is recorded. You can add a note if something looks off."),
            ("user", "How do these chats link to the study questions?"),
            ("agent", "We test if clear talk explains graphs, if you trust the data more, and if the tips help your planning."),
            ("user", "If my teacher asks how I read this, I will say I use the hover help and the formulas."),
            ("agent", "Great. Next, pick a small goal that targets your most common errors."),
            ("user", "Okay, I will fix labelling errors first and set a 15‑minute goal."),
        ])
        st.session_state.chat["overall"] = overall

        # -------------------- FORETHOUGHT (15 user lines) --------------------
        forethought = scripted_pairs([
            ("agent", "Pick a goal for today and say why."),
            ("user", "Goal 1 because I mix up parts like membrane and wall."),
            ("agent", "Rate your confidence 1–5 and choose a small step."),
            ("user", "Confidence 3. Small step: label 5 parts and write what they do."),
            ("agent", "Good. Your plan chart splits days by effort points. Do you understand how Estimated Days is set?"),
            ("user", "It uses a fair share rule… more effort points, more days."),
            ("agent", "Right. And Actual Days updates using actual minutes ÷ planned minutes."),
            ("user", "If Actual is higher than Estimated, I under‑planned or took longer."),
            ("agent", "Yes. What error will you prevent?"),
            ("user", "Labelling errors. I will slow down and check chloroplast vs mitochondria."),
            ("agent", "How will you know this plan is working?"),
            ("user", "My next quick quiz score should rise and error bars should shrink."),
            ("agent", "Where do the plan numbers come from?"),
            ("user", "From my task list and the time window of the dates I chose."),
            ("agent", "Set a time box now."),
            ("user", "I will do 15 minutes after lunch and press Refresh."),
        ])
        st.session_state.chat["forethought"] = forethought

        # -------------------- PERFORMANCE (15 user lines) --------------------
        performance = scripted_pairs([
            ("agent", "Look at your errors. Which type appears the most?"),
            ("user", "Labelling error appears most."),
            ("agent", "Choose one error type to fix in the next 10 minutes."),
            ("user", "I will focus on cell membrane vs cell wall."),
            ("agent", "What prompt will you use to check yourself?"),
            ("user", "I will say the job of each part out loud before I label."),
            ("agent", "Good. The bar chart counts errors in your chosen dates. Does that feel accurate?"),
            ("user", "Yes, I remember missing those labels."),
            ("agent", "Time chart shows minutes per goal. Any surprises?"),
            ("user", "I spent more time on Goal 2 than I thought."),
            ("agent", "Try one short quiz now. Aim a little higher than your last score."),
            ("user", "Okay, I scored a bit higher this time."),
            ("agent", "What helped?"),
            ("user", "Saying the job of the part first. It reduced my errors."),
            ("agent", "Great. Plan one small next step and record it."),
        ])
        st.session_state.chat["performance"] = performance

        # -------------------- REFLECTION (15 user lines) --------------------
        reflection = scripted_pairs([
            ("agent", "What worked well today?"),
            ("user", "Drawing and saying it out loud."),
            ("agent", "What will you change next time?"),
            ("user", "Stop guessing, check each label with the function first."),
            ("agent", "Your word cloud shows 'drawing pictures' and 'self testing' often. Why do these help you?"),
            ("user", "Because I can see and test what I know."),
            ("agent", "Your feeling trend is rising. What does that tell you?"),
            ("user", "I am more confident now."),
            ("agent", "How do these notes support trust in the charts?"),
            ("user", "They explain the story behind the numbers."),
            ("agent", "Write one future goal linked to your top error."),
            ("user", "Explain three cell parts in my own words by Friday."),
            ("agent", "What will you do tomorrow for 10 minutes?"),
            ("user", "Quick quiz and check any errors right away."),
            ("agent", "Add one reason for each corrected answer."),
            ("user", "Okay, I will do that and press Refresh."),
        ])
        st.session_state.chat["reflection"] = reflection

        st.session_state.seed_done = True

# Metrics helpers for coaching
def metrics_for_goal(goal_id, start, end):
    attempts = [a for a in ATTEMPTS if (goal_id in ("ALL", None) or a["goal_id"] == goal_id) and within_range(a["timestamp"], start, end)]
    avg3 = None
    if attempts:
        scores = [a["score"] for a in attempts][-3:]
        avg3 = round(sum(scores) / len(scores), 1)
    err_df = error_frequency(ATTEMPTS, start, end, goal_filter=None if goal_id in ("ALL", None) else goal_id)
    common_err = None
    if not err_df.empty:
        err_row = err_df.sort_values("count", ascending=False).iloc[0]
        common_err = f"{err_row['error']} ({int(err_row['count'])}x)"
    time_sum = sum(a["time_spent_mins"] for a in ATTEMPTS if (goal_id in ("ALL", None) or a["goal_id"] == goal_id) and within_range(a["timestamp"], start, end))
    return {"avg3": avg3, "common_err": common_err, "time_sum": time_sum}

def coach_reply(phase, goal_id, start, end):
    m = metrics_for_goal(goal_id, start, end)
    if phase == "forethought":
        tips = [
            f"Your last 3 scores for {goal_id}: {m['avg3']} (if blank, no recent scores).",
            f"Most common errors: {m['common_err'] or 'none in this range'}.",
            f"Time spent so far: {m['time_sum']} minutes.",
            "Set a small goal for today (for example: label 5 parts and say what each does).",
            "Pick a time box (10–15 minutes) and press Refresh after you do it."
        ]
    elif phase == "performance":
        tips = [
            f"Looking at your data for {goal_id}: average of last 3 scores = {m['avg3']} (if any).",
            f"Top errors to fix next: {m['common_err'] or 'none'} — focus on this first.",
            f"You have spent {m['time_sum']} minutes on this goal in the chosen dates.",
            "Try one short quiz now. Aim a little higher than your last score.",
            "If you get an error, write the right answer and a one-line reason."
        ]
    elif phase == "overall":
        tips = [
            f"Across your goals, your last 3 scores average to {m['avg3']} (if any).",
            f"Common errors to target: {m['common_err'] or 'none'}.",
            f"Total learning time in the chosen dates: {m['time_sum']} minutes.",
            "Pick one small goal for tomorrow that links to your top error.",
            "Plan a 10–15 minute slot and press Refresh after you complete it."
        ]
    else:  # reflection
        tips = [
            f"From your notes and scores for {goal_id}, your recent average (last 3) is {m['avg3']} (if any).",
            f"Error trend: {m['common_err'] or 'no repeating errors spotted'}.",
            "Write one 'what worked' and one 'what to change'.",
            "Set a future goal (for example: 'Explain 3 cell parts in my own words by Friday').",
            "Next step: schedule 10 minutes tomorrow and press Refresh after you finish."
        ]
    return " ".join(tips)

def chat_tab(phase, sel_goal_id, start, end):
    msgs = st.session_state.chat[phase]
    st.subheader(f"{phase.capitalize()} Coach (max 15 messages you send)")
    for role, text in msgs:
        st.write(f"**{'Coach' if role=='agent' else 'You'}:** {text}")
    # Count user messages
    turns = sum(1 for r, _ in msgs if r == "user")
    disabled = turns >= 15
    if disabled:
        # Show the limit message as the next coach line if not already shown
        if not any("You have reached the 15-message limit" in t for r, t in msgs if r == "agent"):
            msgs.append(("agent", "You have reached the 15-message limit for this phase. Please ask your teacher if you need more help."))
            st.session_state.chat[phase] = msgs
        st.warning("You have hit the 15-message limit for this phase.")
    user = st.text_input(f"Your reply ({phase})", disabled=disabled, key=f"in_{phase}")
    if st.button(f"Send ({phase})", disabled=disabled or not user.strip()):
        msgs.append(("user", user.strip()))
        # After sending, check if this was the 15th message
        turns_after = sum(1 for r, _ in msgs if r == "user")
        if turns_after >= 15:
            msgs.append(("agent", "You have reached the 15-message limit for this phase. Please ask your teacher if you need more help."))
        else:
            # Data-aware coaching
            msgs.append(("agent", coach_reply(phase, sel_goal_id, start, end)))
        st.session_state.chat[phase] = msgs
        st.experimental_rerun()
    st.caption(f"Messages you sent in this phase: {turns}/15")

def overall_chat(start, end):
    phase = "overall"
    msgs = st.session_state.chat[phase]
    st.subheader("Overview Coach (max 15 messages you send)")
    for role, text in msgs:
        st.write(f"**{'Coach' if role=='agent' else 'You'}:** {text}")
    turns = sum(1 for r, _ in msgs if r == "user")
    disabled = turns >= 15
    if disabled:
        if not any("You have reached the 15-message limit" in t for r, t in msgs if r == "agent"):
            msgs.append(("agent", "You have reached the 15-message limit for this phase. Please ask your teacher if you need more help."))
            st.session_state.chat[phase] = msgs
        st.warning("You have hit the 15-message limit for this phase.")
    user = st.text_input("Your reply (overall)", disabled=disabled, key="in_overall")
    if st.button("Send (overall)", disabled=disabled or not user.strip()):
        msgs.append(("user", user.strip()))
        turns_after = sum(1 for r, _ in msgs if r == "user")
        if turns_after >= 15:
            msgs.append(("agent", "You have reached the 15-message limit for this phase. Please ask your teacher if you need more help."))
        else:
            msgs.append(("agent", coach_reply("overall", "ALL", start, end)))
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
        "- **Attempts**: your quizzes and practice work (with time spent and common errors).\n"
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
sel_goal_effective = sel_goal if sel_goal != "ALL" else "ALL"

# ============================ 4 Tabs ============================
tab_overview, tab_fore, tab_perf, tab_refl = st.tabs(
    ["Overview", "Phase 1 • Plan", "Phase 2 • Do", "Phase 3 • Reflect"]
)

with tab_overview:
    st.subheader("Overview • SRL Radar (Expected vs Actual)")

    expected = [
        {"phase": "Forethought", "score": 80},
        {"phase": "Performance", "score": 85},
        {"phase": "Reflection", "score": 75},
    ]
    actual = actual_radar(TASKS, ATTEMPTS, REFLECTIONS, start_str, end_str)

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
            hovertemplate="<b>%{theta}</b><br>Score: %{r}%<br><i>How this is worked out:</i> %{customdata}<extra></extra>"
        )

    fig = go.Figure()
    fig.add_trace(radar_trace(expected, "Expected", "rgba(100,116,139,0.6)"))
    fig.add_trace(radar_trace(actual, "Actual", "rgba(245,158,11,0.6)"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(title="Hover a phase in the chart to see how it is worked out."),
        font=dict(family="Arial", size=22)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Overview coach chat inside Overview tab
    seed_once()
    overall_chat(start_str, end_str)

with tab_fore:
    st.header("Plan (set simple steps)")
    prog_df = goal_progress(GOALS, TASKS)
    prog_df["Date range"] = prog_df["start_date"] + " → " + prog_df["target_date"]
    pretty = prog_df.rename(columns={
        "goal_id": "Goal",
        "title": "Goal title",
        "doneEffort": "Done effort",
        "totalEffort": "Total effort"
    })[["Goal", "Goal title", "Date range", "Done effort", "Total effort"]]
    st.dataframe(pretty)
    with st.expander("How are these numbers worked out?"):
        st.markdown(
            "- **Total effort** = add up the effort points for all tasks under the goal.\n"
            "- **Done effort** = add up the effort points for tasks marked complete."
        )

    st.subheader("Progress by Task (respects your goal filter)")
    if sel_goal_effective == "ALL":
        window_days = max(1, (pd.to_datetime(end_str) - pd.to_datetime(start_str)).days or 1)
        sel_tasks = TASKS[:]
    else:
        g = next((x for x in GOALS if x["goal_id"] == sel_goal_effective), GOALS[0])
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
            "goal": t["goal_id"],
            "Estimated Days": estimated_days,
            "Actual Days": actual_days,
            "ExplainEstimated": "We split the total time window across tasks using effort points. More effort = more days.",
            "ExplainActual": "We adjust the estimate by how much time you actually used compared to what you planned.",
            "FormulaEstimated": "Estimated Days = Total time window in days × (Task effort ÷ Sum of effort of shown tasks)",
            "FormulaActual": "Actual Days = Estimated Days × (Actual minutes ÷ Planned minutes)"
        })
    bars_df = pd.DataFrame(rows).melt(
        id_vars=["task", "goal", "ExplainEstimated", "ExplainActual", "FormulaEstimated", "FormulaActual"],
        value_vars=["Estimated Days", "Actual Days"],
        var_name="Type",
        value_name="Days",
    )
    bars_df["Explain"] = bars_df.apply(
        lambda r: r["ExplainEstimated"] if r["Type"] == "Estimated Days" else r["ExplainActual"],
        axis=1
    )
    bars_df["Formula"] = bars_df.apply(
        lambda r: r["FormulaEstimated"] if r["Type"] == "Estimated Days" else r["FormulaActual"],
        axis=1
    )
    fig_bars = px.bar(
        bars_df.sort_values(["goal", "task"]),
        x="Days", y="task", color="Type", orientation="h",
        hover_data={"Explain": True, "Formula": True, "goal": True, "Days": ":.2f", "task": False, "Type": False}
    )
    fig_bars.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.2f} days<br><i>Goal:</i> %{customdata[1]}<br><i>Meaning:</i> %{customdata[0]}<br><i>Formula:</i> %{customdata[2]}<extra></extra>")
    fig_bars.update_layout(font=dict(family="Arial", size=22))
    st.plotly_chart(fig_bars, use_container_width=True)

    seed_once()
    chat_tab("forethought", sel_goal_effective if sel_goal_effective != "ALL" else "ALL", start_str, end_str)

with tab_perf:
    st.header("Do (watch errors and time)")
    ef_df = error_frequency(ATTEMPTS, start_str, end_str, goal_filter=None if sel_goal == "ALL" else sel_goal)
    if not ef_df.empty:
        fig_err = px.bar(
            ef_df.sort_values("count", ascending=True),
            x="count",
            y="error",
            orientation="h",
            labels={"count": "Number of times", "error": "Common errors"},
            hover_data={"count": True, "error": True}
        )
        fig_err.update_traces(hovertemplate="<b>%{y}</b><br>Times seen: %{x}<br><i>Tip:</i> Fix one error type at a time.<extra></extra>")
        fig_err.update_layout(font=dict(family="Arial", size=22))
        st.plotly_chart(fig_err, use_container_width=True)
    else:
        st.info("No errors found in the chosen dates.")

    tbg_df = time_by_goal(ATTEMPTS, GOALS)
    fig_time = px.bar(
        tbg_df,
        x="goal_id",
        y="time",
        hover_data=["title", "attempts"],
        labels={"goal_id": "Goal", "time": "Minutes", "attempts": "Activities counted"}
    )
    fig_time.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Minutes: %{y}<br>Activities: %{customdata[1]}<br><i>How this is worked out:</i> We add all minutes from attempts for this goal.<extra></extra>")
    fig_time.update_layout(font=dict(family="Arial", size=22))
    st.plotly_chart(fig_time, use_container_width=True)

    seed_once()
    chat_tab("performance", sel_goal_effective if sel_goal_effective != "ALL" else "ALL", start_str, end_str)

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
        ].rename(columns={"feeling": "Feeling (−1 to +1)"})
        st.dataframe(df_show)

    st.subheader("Feelings over time")
    sent_series = [
        {"idx": i + 1, "feeling": r["feeling"]} for i, r in enumerate(REFLECTIONS)
    ]
    fig_sent = px.line(pd.DataFrame(sent_series), x="idx", y="feeling", markers=True,
                       labels={"idx": "Reflection number", "feeling": "Feeling (−1 to +1)"})
    fig_sent.update_yaxes(range=[-1, 1])
    fig_sent.update_traces(hovertemplate="Reflection #%{x}<br>Feeling: %{y}<br><i>Note:</i> closer to +1 means more positive.<extra></extra>")
    fig_sent.update_layout(font=dict(family="Arial", size=22))
    st.plotly_chart(fig_sent, use_container_width=True)

    seed_once()
    chat_tab("reflection", sel_goal_effective if sel_goal_effective != "ALL" else "ALL", start_str, end_str)

st.caption(
    "ⓘ Data source: goals, tasks, attempts, and reflections on this page. "
    "Charts use simple math; hover or open the help boxes to see how we work them out."
)
