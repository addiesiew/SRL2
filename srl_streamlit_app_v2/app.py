import math
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud

st.set_page_config(page_title="SRL Dashboard (Streamlit)", layout="wide")

# ============================ Simulated Data (coherent) ============================
GOALS = [
    {"goal_id":"G1","title":"Compare plant vs animal cells","unit":"Cells – Plant vs Animal","start_date":"2025-10-15","target_date":"2025-11-15","priority":1,"stars":4,"status":"in progress"},
    {"goal_id":"G2","title":"Explain mitochondria role","unit":"Cell Organelles","start_date":"2025-10-10","target_date":"2025-11-01","priority":2,"stars":3,"status":"completed"},
    {"goal_id":"G3","title":"Draw labeled cell diagram","unit":"Cell Structure","start_date":"2025-10-20","target_date":"2025-11-20","priority":1,"stars":5,"status":"in progress"},
]

TASKS = [
  {"task_id":"T1","goal_id":"G1","title":"Read textbook chapter 3","est_mins":30,"act_mins":35,"completed":True,"effort":3},
  {"task_id":"T2","goal_id":"G1","title":"Watch video on plant cells","est_mins":15,"act_mins":18,"completed":True,"effort":2},
  {"task_id":"T3","goal_id":"G1","title":"Create comparison table","est_mins":20,"act_mins":28,"completed":True,"effort":4},
  {"task_id":"T4","goal_id":"G1","title":"Practice quiz - cells","est_mins":25,"act_mins":22,"completed":True,"effort":3},
  {"task_id":"T5","goal_id":"G1","title":"Review with flashcards","est_mins":15,"act_mins":0,"completed":False,"effort":2},
  {"task_id":"T6","goal_id":"G1","title":"Draw diagrams","est_mins":30,"act_mins":0,"completed":False,"effort":5},
  {"task_id":"T7","goal_id":"G1","title":"Peer discussion","est_mins":20,"act_mins":0,"completed":False,"effort":3},
  {"task_id":"T8","goal_id":"G2","title":"Research mitochondria","est_mins":25,"act_mins":30,"completed":True,"effort":4},
  {"task_id":"T9","goal_id":"G2","title":"Write explanation","est_mins":20,"act_mins":25,"completed":True,"effort":5},
  {"task_id":"T10","goal_id":"G2","title":"Self-test","est_mins":15,"act_mins":12,"completed":True,"effort":2},
  {"task_id":"T11","goal_id":"G3","title":"Study cell parts","est_mins":20,"act_mins":22,"completed":True,"effort":3},
  {"task_id":"T12","goal_id":"G3","title":"Practice drawing","est_mins":30,"act_mins":35,"completed":True,"effort":5},
  {"task_id":"T13","goal_id":"G3","title":"Label practice","est_mins":15,"act_mins":18,"completed":True,"effort":2},
  {"task_id":"T14","goal_id":"G3","title":"Color and refine","est_mins":25,"act_mins":0,"completed":False,"effort":4},
  {"task_id":"T15","goal_id":"G3","title":"Get feedback","est_mins":10,"act_mins":0,"completed":False,"effort":2},
]

ATTEMPTS = [
  {"attempt_id":"A1","goal_id":"G1","activity_title":"Cell comparison quiz 1","timestamp":"2025-10-22T10:00:00","score":56,"error_tags":["misconception-membrane","labeling-error"],"time_spent_mins":12},
  {"attempt_id":"A2","goal_id":"G1","activity_title":"Cell comparison quiz 2","timestamp":"2025-10-25T14:30:00","score":61,"error_tags":["misconception-membrane","incomplete-answer"],"time_spent_mins":15},
  {"attempt_id":"A3","goal_id":"G1","activity_title":"Plant vs animal test","timestamp":"2025-10-28T09:15:00","score":74,"error_tags":["labeling-error"],"time_spent_mins":18},
  {"attempt_id":"A4","goal_id":"G2","activity_title":"Mitochondria quiz","timestamp":"2025-10-30T11:00:00","score":79,"error_tags":["incomplete-answer"],"time_spent_mins":14},
  {"attempt_id":"A5","goal_id":"G1","activity_title":"Final cell quiz","timestamp":"2025-11-02T13:20:00","score":82,"error_tags":[],"time_spent_mins":20},
  {"attempt_id":"A6","goal_id":"G3","activity_title":"Diagram practice 1","timestamp":"2025-10-24T16:00:00","score":68,"error_tags":["labeling-error","proportion-error"],"time_spent_mins":22},
  {"attempt_id":"A7","goal_id":"G3","activity_title":"Diagram practice 2","timestamp":"2025-10-27T10:30:00","score":75,"error_tags":["proportion-error"],"time_spent_mins":19},
  {"attempt_id":"A8","goal_id":"G3","activity_title":"Label test","timestamp":"2025-11-01T15:45:00","score":81,"error_tags":["minor-detail"],"time_spent_mins":16},
  {"attempt_id":"A9","goal_id":"G1","activity_title":"Review quiz","timestamp":"2025-11-03T09:00:00","score":88,"error_tags":[],"time_spent_mins":18},
  {"attempt_id":"A10","goal_id":"G2","activity_title":"Mitochondria retest","timestamp":"2025-11-04T14:00:00","score":92,"error_tags":[],"time_spent_mins":15},
]

REFLECTIONS = [
  {"reflection_id":"R1","goal_id":"G1","activity_title":"Cell comparison quiz 1","timestamp":"2025-10-22T10:30:00","free_text":"I struggled with membrane functions. Need to draw more diagrams to understand the differences visually.","self_eval_confidence":2,"self_eval_difficulty":4,"self_eval_satisfaction":2,"strategy_tags":["re-reading notes","drawing diagrams"],"sentiment":-0.1},
  {"reflection_id":"R2","goal_id":"G1","activity_title":"Cell comparison quiz 2","timestamp":"2025-10-25T15:00:00","free_text":"Drawing helped! I can now picture the differences. Self-testing revealed gaps in chloroplast knowledge.","self_eval_confidence":3,"self_eval_difficulty":3,"self_eval_satisfaction":4,"strategy_tags":["drawing diagrams","self-testing"],"sentiment":0.4},
  {"reflection_id":"R3","goal_id":"G1","activity_title":"Plant vs animal test","timestamp":"2025-10-28T10:00:00","free_text":"Much better! Explaining concepts aloud to myself really solidified my understanding. Felt confident.","self_eval_confidence":4,"self_eval_difficulty":2,"self_eval_satisfaction":5,"strategy_tags":["explaining aloud","drawing diagrams","self-testing"],"sentiment":0.6},
  {"reflection_id":"R4","goal_id":"G2","activity_title":"Mitochondria quiz","timestamp":"2025-10-30T11:30:00","free_text":"Summarizing the steps of cellular respiration in my own words was key. Need to stop just scrolling through notes.","self_eval_confidence":4,"self_eval_difficulty":3,"self_eval_satisfaction":4,"strategy_tags":["summarising steps","scrolling quickly"],"sentiment":0.3},
  {"reflection_id":"R5","goal_id":"G3","activity_title":"Diagram practice 2","timestamp":"2025-10-27T11:00:00","free_text":"Drawing repeatedly is tedious but effective. I notice patterns now. Guessing label positions is not working.","self_eval_confidence":3,"self_eval_difficulty":3,"self_eval_satisfaction":3,"strategy_tags":["drawing diagrams","guessing answers"],"sentiment":0.2},
  {"reflection_id":"R6","goal_id":"G3","activity_title":"Label test","timestamp":"2025-11-01T16:15:00","free_text":"Self-testing with blank diagrams was perfect preparation. Confidence is high now. Ready for the real test!","self_eval_confidence":5,"self_eval_difficulty":2,"self_eval_satisfaction":5,"strategy_tags":["self-testing","drawing diagrams","explaining aloud"],"sentiment":0.5},
]

def within_range(ts, start, end):
    return pd.to_datetime(ts) >= pd.to_datetime(start) and pd.to_datetime(ts) <= pd.to_datetime(end)

def goal_progress(goals, tasks):
    rows = []
    for g in goals:
        g_tasks = [t for t in tasks if t["goal_id"] == g["goal_id"]]
        total_effort = sum(t["effort"] for t in g_tasks) or 1
        done_effort = sum(t["effort"] for t in g_tasks if t["completed"])
        pct = (done_effort / total_effort) * 100.0
        rows.append({**g, "totalEffort": total_effort, "doneEffort": done_effort, "pct": pct})
    return pd.DataFrame(rows)

def error_frequency(attempts, start, end):
    counts = {}
    for a in attempts:
        if within_range(a["timestamp"], start, end):
            for tag in a["error_tags"]:
                counts.setdefault(tag, []).append({
                    "activity": a["activity_title"],
                    "date": pd.to_datetime(a["timestamp"]).strftime("%b %d"),
                    "goal_id": a["goal_id"]
                })
    data = [{"error": k, "count": len(v), "details": v} for k, v in counts.items()]
    return pd.DataFrame(data)

def time_by_goal(attempts, goals):
    rows = []
    for g in goals:
        g_attempts = [a for a in attempts if a["goal_id"] == g["goal_id"]]
        time_sum = sum(a["time_spent_mins"] for a in g_attempts)
        rows.append({"goal_id": g["goal_id"], "title": g["title"], "time": time_sum, "attempts": len(g_attempts)})
    return pd.DataFrame(rows)

def self_eval_for_goal(reflections, goal_id):
    rs = [r for r in reflections if r["goal_id"] == goal_id]
    if not rs:
        return {"confidence": 0, "difficulty": 0, "satisfaction": 0}
    avg_conf = np.mean([r["self_eval_confidence"] for r in rs]) / 5.0 * 100
    avg_diff = np.mean([r["self_eval_difficulty"] for r in rs]) / 5.0 * 100
    avg_sat  = np.mean([r["self_eval_satisfaction"] for r in rs]) / 5.0 * 100
    return {"confidence": avg_conf, "difficulty": avg_diff, "satisfaction": avg_sat}

def actual_radar(tasks, attempts, reflections, start, end):
    total = len(tasks)
    complete = len([t for t in tasks if t["completed"]])
    fore = (complete / total) * 100 if total else 0
    filt_attempts = [a for a in attempts if within_range(a["timestamp"], start, end)]
    last10 = filt_attempts[-10:]
    errorfree = len([a for a in last10 if len(a["error_tags"]) == 0])
    perf = (errorfree / len(last10) * 100) if last10 else 0
    filt_refl = [r for r in reflections if within_range(r["timestamp"], start, end)]
    pos = len([r for r in filt_refl if r["sentiment"] > 0])
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

# ===== Chat limiter & seeds =====
if "chat" not in st.session_state:
    st.session_state.chat = {"overview": [], "forethought": [], "performance": [], "reflection": []}
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "cooldown_until" not in st.session_state:
    st.session_state.cooldown_until = None
if "seed_done" not in st.session_state:
    st.session_state.seed_done = False

seed_dialog = {
    "overview": [
        ("agent","What part of the dashboard would you like summarized—Radar, Self-Eval, or Sentiment?"),
        ("user","Summarize everything."),
        ("agent","Radar shows Expected vs Actual; Self-Eval averages confidence/difficulty/satisfaction; Sentiment trends your reflection tone.")
    ],
    "forethought":[
        ("agent","Set today's focus—pick 1 goal. Why this one?"),
        ("user","G1—confused about plant vs animal differences."),
        ("agent","Rate confidence 1–5 and state your first step.")
    ],
    "performance":[
        ("agent","Looking at your error patterns, which type appears most frequently?"),
        ("user","Labeling errors appear most."),
        ("agent","Pick that to reduce next attempt—do you want a 10‑min timed review?")
    ],
    "reflection":[
        ("agent","Which strategy helped most for your chosen goal?"),
        ("user","Drawing diagrams helped the most."),
        ("agent","Name one you'll drop next time—and why.")
    ]
}

def seed_once():
    if not st.session_state.seed_done:
        st.session_state.chat = {k:list(v) for k,v in seed_dialog.items()}
        st.session_state.seed_done = True

def limiter_status():
    limit = 15
    blocked = False
    remaining = max(0, limit - st.session_state.chat_count)
    minutes_left = 0
    if st.session_state.cooldown_until:
        now = datetime.utcnow()
        if now < st.session_state.cooldown_until:
            blocked = True
            delta = st.session_state.cooldown_until - now
            minutes_left = max(1, int((delta.total_seconds()+59)//60))
        else:
            st.session_state.cooldown_until = None
            st.session_state.chat_count = 0
            remaining = limit
    return {"blocked": blocked, "remaining": remaining, "minutes_left": minutes_left}

def record_send():
    st.session_state.chat_count += 1
    if st.session_state.chat_count >= 15:
        st.session_state.cooldown_until = datetime.utcnow() + timedelta(hours=1)

def chat_tab(phase):
    status = limiter_status()
    st.write(f"**{phase.capitalize()} Coach** — 3 turns")
    if status["blocked"]:
        st.warning(f"Chat paused. Cooldown ~{status['minutes_left']} minutes or seek teacher assistance.")
    msgs = st.session_state.chat[phase]
    if not msgs:
        seed_once()
        msgs = st.session_state.chat[phase]
    for role, text in msgs:
        st.write(f"**{'Agent' if role=='agent' else 'You'}:** {text}")
    user = st.text_input(f"Your reply ({phase})", disabled=status['blocked'], key=f"in_{phase}")
    turns = sum(1 for r,_ in msgs if r=='user')
    if st.button(f"Send ({phase})", disabled=status['blocked'] or turns>=3 or not user.strip()):
        msgs.append(("user", user.strip()))
        scripted = {
            "overview":["Radar compares Expected vs Actual; Self‑Eval averages confidence/difficulty/satisfaction.","Which goal should we focus on next?"],
            "forethought":["How confident are you (1–5) and what's your first step?","Set a time box. I'll check back in Performance."],
            "performance":["Pick one error type to reduce next attempt.","Do you want a 10‑min timed review block?"],
            "reflection":["Name one you'll drop next time—and why.","Write a 1‑sentence takeaway I can pin to Overview."]
        }
        idx = min(turns, 1)
        msgs.append(("agent", scripted[phase][idx]))
        st.session_state.chat[phase] = msgs
        record_send()
        st.experimental_rerun()
    st.caption(f"Turns used: {turns}/3 • {status['remaining']} chats left / hr")

# ===== Controls =====
st.title("Self-Regulated Learning Dashboard (Streamlit)")
st.caption("Forethought → Performance → Reflection, with dialogic coaching and analytics")

colA, colB, colC = st.columns([1,1,1])
with colA:
    goal_options = ["ALL"] + [g["goal_id"] for g in GOALS]
    sel_goal = st.selectbox("Select Goal", goal_options, index=1)
with colB:
    start = st.date_input("Start Date", value=pd.to_datetime("2025-10-22"))
with colC:
    end = st.date_input("End Date", value=pd.to_datetime("2025-11-04"))

start_str = pd.to_datetime(start).strftime("%Y-%m-%d")
end_str = pd.to_datetime(end).strftime("%Y-%m-%d")

# ===== Overview =====
st.subheader("SRL Radar (Expected vs Actual)")
expected = [{"phase":"Forethought","score":80},{"phase":"Performance","score":85},{"phase":"Reflection","score":75}]
actual = actual_radar(TASKS, ATTEMPTS, REFLECTIONS, start_str, end_str)

def radar_trace(data, name, color):
    theta = [pt["phase"] for pt in data] + [data[0]["phase"]]
    r = [pt["score"] for pt in data] + [data[0]["score"]]
    return go.Scatterpolar(r=r, theta=theta, fill='toself', name=name, line=dict(color=color))

fig = go.Figure()
fig.add_trace(radar_trace(expected, "Expected", "rgba(100,116,139,0.6)"))
fig.add_trace(radar_trace(actual,   "Actual",   "rgba(245,158,11,0.6)"))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=True, margin=dict(l=20,r=20,t=20,b=20))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Self-Evaluation (Selected Goal)")
goal_for_eval = sel_goal if sel_goal != "ALL" else "G1"
sev = self_eval_for_goal(REFLECTIONS, goal_for_eval)
sev_df = pd.DataFrame([sev])
fig_sev = px.bar(sev_df, barmode="group")
fig_sev.update_yaxes(range=[0,100])
st.plotly_chart(fig_sev, use_container_width=True)

st.subheader("Sentiment Over Time (Reflections)")
sent_series = [{"idx": i+1, "sentiment": r["sentiment"]} for i, r in enumerate(REFLECTIONS)]
fig_sent = px.line(pd.DataFrame(sent_series), x="idx", y="sentiment", markers=True)
fig_sent.update_yaxes(range=[-1,1])
st.plotly_chart(fig_sent, use_container_width=True)

# ===== Forethought =====
st.header("Phase 1: Forethought (Goal Setting & Planning)")
prog_df = goal_progress(GOALS, TASKS)
st.dataframe(prog_df[["goal_id","title","pct","doneEffort","totalEffort"]])

st.subheader("Progress by Activity (Selected Goal)")
g = next((x for x in GOALS if x["goal_id"] == (sel_goal if sel_goal != "ALL" else "G1")), GOALS[0])
window_days = max(1, (pd.to_datetime(min(g["target_date"], end_str)) - pd.to_datetime(max(g["start_date"], start_str))).days or 1)
sel_tasks = [t for t in TASKS if t["goal_id"] == g["goal_id"]]
total_effort = sum(t["effort"] for t in sel_tasks) or 1
rows = []
for t in sel_tasks:
    share = (t["effort"] / total_effort)
    est_days = window_days * share
    ratio = (t["act_mins"] / t["est_mins"]) if t["est_mins"] else 0
    act_days = min(est_days, est_days * ratio)
    rows.append({"task": t["title"], "EstDays": est_days, "ActDays": act_days})
bars_df = pd.DataFrame(rows)
bars_df = bars_df.melt(id_vars=["task"], value_vars=["EstDays","ActDays"], var_name="Type", value_name="Days")
fig_bars = px.bar(bars_df, x="Days", y="task", color="Type", orientation="h")
st.plotly_chart(fig_bars, use_container_width=True)

# ===== Performance =====
st.header("Phase 2: Performance (Monitoring & Feedback)")
ef_df = error_frequency(ATTEMPTS, start_str, end_str)
if not ef_df.empty:
    fig_err = px.bar(ef_df.sort_values("count", ascending=True), x="count", y="error", orientation="h")
    st.plotly_chart(fig_err, use_container_width=True)
else:
    st.info("No errors recorded in the selected range.")

tbg_df = time_by_goal(ATTEMPTS, GOALS)
fig_time = px.bar(tbg_df, x="goal_id", y="time", hover_data=["title","attempts"])
st.plotly_chart(fig_time, use_container_width=True)

# ===== Reflection =====
st.header("Phase 3: Self-Reflection (Strategies & Sentiment)")
c1, c2 = st.columns([1,1])
with c1:
    st.subheader("Strategy Word Cloud")
    img = wordcloud_image(REFLECTIONS, goal_filter=None if sel_goal=="ALL" else sel_goal)
    st.image(img, caption="Green=effective, Red=less effective (legend conceptual)")
with c2:
    st.subheader("Reflections")
    st.dataframe(pd.DataFrame(REFLECTIONS)[["goal_id","activity_title","sentiment","strategy_tags","free_text"]])

# ===== Chats =====
st.header("Dialogic Coaches (max 15 interactions/hour across all)")
tab_over, tab_fore, tab_perf, tab_refl = st.tabs(["Overview", "Forethought", "Performance", "Reflection"])
with tab_over:    chat_tab("overview")
with tab_fore:    chat_tab("forethought")
with tab_perf:    chat_tab("performance")
with tab_refl:    chat_tab("reflection")

st.caption("ⓘ Data provenance: goals/tasks/attempts/reflections drive visuals. Expected radar values are preset; Actual uses completion (tasks), error‑free attempts, and positive sentiment share.")
