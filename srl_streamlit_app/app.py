
import time
from datetime import datetime, date
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
from PIL import Image
from PyPDF2 import PdfReader
import io

st.set_page_config(page_title="SRL Dashboard", layout="wide")

# ------------------------ Mock Data (coherent) ------------------------
seed_goals = [
    {"goal_id":"G1","title":"Compare plant vs animal cells","unit":"Cells – Plant vs Animal","start_date":"2025-10-15","target_date":"2025-11-15","priority":1,"stars":4,"status":"in progress"},
    {"goal_id":"G2","title":"Explain mitochondria role","unit":"Cell Organelles","start_date":"2025-10-10","target_date":"2025-11-01","priority":2,"stars":3,"status":"completed"},
    {"goal_id":"G3","title":"Draw labeled cell diagram","unit":"Cell Structure","start_date":"2025-10-20","target_date":"2025-11-20","priority":1,"stars":5,"status":"in progress"},
]
seed_tasks = [
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
learning_attempts = [
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
reflections = [
    {"reflection_id":"R1","goal_id":"G1","activity_title":"Cell comparison quiz 1","timestamp":"2025-10-22T10:30:00","free_text":"I struggled with membrane functions. Need to draw more diagrams to understand the differences visually.","self_eval_confidence":2,"self_eval_difficulty":4,"self_eval_satisfaction":2,"strategy_tags":["re-reading notes","drawing diagrams"],"sentiment":-0.1},
    {"reflection_id":"R2","goal_id":"G1","activity_title":"Cell comparison quiz 2","timestamp":"2025-10-25T15:00:00","free_text":"Drawing helped! I can now picture the differences. Self-testing revealed gaps in chloroplast knowledge.","self_eval_confidence":3,"self_eval_difficulty":3,"self_eval_satisfaction":4,"strategy_tags":["drawing diagrams","self-testing"],"sentiment":0.4},
    {"reflection_id":"R3","goal_id":"G1","activity_title":"Plant vs animal test","timestamp":"2025-10-28T10:00:00","free_text":"Much better! Explaining concepts aloud to myself really solidified my understanding. Felt confident.","self_eval_confidence":4,"self_eval_difficulty":2,"self_eval_satisfaction":5,"strategy_tags":["explaining aloud","drawing diagrams","self-testing"],"sentiment":0.6},
    {"reflection_id":"R4","goal_id":"G2","activity_title":"Mitochondria quiz","timestamp":"2025-10-30T11:30:00","free_text":"Summarizing the steps of cellular respiration in my own words was key. Need to stop just scrolling through notes.","self_eval_confidence":4,"self_eval_difficulty":3,"self_eval_satisfaction":4,"strategy_tags":["summarising steps","scrolling quickly"],"sentiment":0.3},
    {"reflection_id":"R5","goal_id":"G3","activity_title":"Diagram practice 2","timestamp":"2025-10-27T11:00:00","free_text":"Drawing repeatedly is tedious but effective. I notice patterns now. Guessing label positions is not working.","self_eval_confidence":3,"self_eval_difficulty":3,"self_eval_satisfaction":3,"strategy_tags":["drawing diagrams","guessing answers"],"sentiment":0.2},
    {"reflection_id":"R6","goal_id":"G3","activity_title":"Label test","timestamp":"2025-11-01T16:15:00","free_text":"Self-testing with blank diagrams was perfect preparation. Confidence is high now. Ready for the real test!","self_eval_confidence":5,"self_eval_difficulty":2,"self_eval_satisfaction":5,"strategy_tags":["self-testing","drawing diagrams","explaining aloud"],"sentiment":0.5},
]
EFFECTIVE = {"drawing diagrams","explaining aloud","self-testing","summarising steps"}
INEFFECTIVE = {"re-reading notes","scrolling quickly","guessing answers"}
COLORS = {"green":"#22c55e","red":"#ef4444","slate":"#64748b","amber":"#f59e0b","violet":"#8b5cf6","gray":"#94a3b8"}

# ------------------------ Session state ------------------------
if "goals" not in st.session_state: st.session_state.goals = seed_goals.copy()
if "tasks" not in st.session_state: st.session_state.tasks = seed_tasks.copy()
if "selected_goal" not in st.session_state: st.session_state.selected_goal = "G1"
if "date_start" not in st.session_state: st.session_state.date_start = "2025-10-22"
if "date_end" not in st.session_state: st.session_state.date_end = "2025-11-04"
if "pinned" not in st.session_state: st.session_state.pinned = ""
if "chat_log" not in st.session_state:
    st.session_state.chat_log = {"overview": [], "forethought": [], "performance": [], "reflection": []}
if "chat_count" not in st.session_state: st.session_state.chat_count = 0
if "cooldown_until" not in st.session_state: st.session_state.cooldown_until = 0
if "turns" not in st.session_state: st.session_state.turns = {"overview":0,"forethought":0,"performance":0,"reflection":0}
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""

# Seed demo chats once
def seed_chats():
    if not st.session_state.chat_log["overview"]:
        st.session_state.chat_log["overview"] = [
            ("agent","What part of the dashboard would you like summarized—Radar, Self-Eval, or Sentiment?"),
            ("user","Give me a summary of everything."),
            ("agent","Radar compares Expected vs Actual; Self-Eval averages confidence/difficulty/satisfaction; Sentiment is trending positive.")
        ]
        st.session_state.turns["overview"] = 2
    if not st.session_state.chat_log["forethought"]:
        st.session_state.chat_log["forethought"] = [
            ("agent","Set today's focus—pick 1 goal. Why this one?"),
            ("user","G1 because I mix up plant vs animal structures."),
            ("agent","How confident are you (1–5) and what's your first step?")
        ]
        st.session_state.turns["forethought"] = 2
    if not st.session_state.chat_log["performance"]:
        st.session_state.chat_log["performance"] = [
            ("agent","Looking at your error patterns, which type appears most frequently?"),
            ("user","Labeling errors appear most."),
            ("agent","Pick that to reduce next attempt—do you want a 10-min timed review?")
        ]
        st.session_state.turns["performance"] = 2
    if not st.session_state.chat_log["reflection"]:
        st.session_state.chat_log["reflection"] = [
            ("agent","Which strategy helped most for your chosen goal?"),
            ("user","Drawing diagrams helped."),
            ("agent","Name one you'll drop next time—and why.")
        ]
        st.session_state.turns["reflection"] = 2
seed_chats()

# ------------------------ Helpers ------------------------
def within_range(ts, start, end):
    t = datetime.fromisoformat(ts.replace("Z",""))
    return datetime.fromisoformat(start) <= t <= datetime.fromisoformat(end)

def days_between(start, end):
    return max(1, (datetime.fromisoformat(end) - datetime.fromisoformat(start)).days)

def goal_window(selected_goal, start, end):
    if selected_goal == "ALL":
        return start, end
    g = next((g for g in st.session_state.goals if g["goal_id"]==selected_goal), None)
    if not g: return start, end
    s = max(datetime.fromisoformat(g["start_date"]), datetime.fromisoformat(start))
    e = min(datetime.fromisoformat(g["target_date"]), datetime.fromisoformat(end))
    return s.date().isoformat(), e.date().isoformat()

def radar_actual(start, end):
    in_range = [a for a in learning_attempts if within_range(a["timestamp"], start, end)]
    last10 = in_range[-10:]
    ef = sum(1 for a in last10 if not a["error_tags"])
    perf = (ef/len(last10)*100) if last10 else 0
    total = len(st.session_state.tasks)
    done = sum(1 for t in st.session_state.tasks if t["completed"])
    fore = (done/total*100) if total else 0
    refl_rng = [r for r in reflections if within_range(r["timestamp"], start, end)]
    pos = sum(1 for r in refl_rng if r["sentiment"]>0)
    refl = (pos/len(refl_rng)*100) if refl_rng else 0
    return [{"phase":"Forethought","score":round(fore)},
            {"phase":"Performance","score":round(perf)},
            {"phase":"Reflection","score":round(refl)}]

EXPECTED = [{"phase":"Forethought","score":80},
            {"phase":"Performance","score":85},
            {"phase":"Reflection","score":75}]

def strategies_counts(goal_id):
    df = [r for r in reflections if goal_id=="ALL" or r["goal_id"]==goal_id]
    counts = {}
    for r in df:
        for t in r["strategy_tags"]:
            counts[t] = counts.get(t,0)+1
    return counts

def grounded_summary(pdf_text):
    if not pdf_text: 
        return "Radar compares Expected vs Actual; Self‑Eval averages confidence/difficulty/satisfaction; Sentiment trends reflection tone."
    # Simple grounding: extract frequent terms and add to summary
    text = pdf_text.lower()
    key_terms = []
    for k in ["self‑regulated learning","dialogic","strategy","forethought","performance","reflection","feedback","dashboard","word cloud","confidence","difficulty","satisfaction"]:
        if k in text and k not in key_terms:
            key_terms.append(k)
    extra = "; ".join(key_terms[:5])
    base = "Radar compares Expected vs Actual; Self‑Eval averages confidence/difficulty/satisfaction; Sentiment trends reflection tone."
    return base + (" • Grounded terms: " + extra if extra else "")

# ------------------------ Header & SRL Loop ------------------------
st.title("Self‑Regulated Learning Dashboard")
st.caption("Forethought • Performance • Reflection — with dialogic scaffolds")

col1, col2 = st.columns([2,1])
with col1:
    st.image("srl_loop.png", caption="SRL Cycle Map", use_container_width=True)
with col2:
    uploaded = st.file_uploader("Upload research PDF(s) to ground Overview responses", type=["pdf"], accept_multiple_files=True)
    buf = io.StringIO()
    if uploaded:
        for up in uploaded:
            try:
                reader = PdfReader(up)
                for p in reader.pages[:5]:
                    buf.write(p.extract_text() or "")
            except Exception as e:
                st.warning(f"Could not read {up.name}: {e}")
    st.session_state.pdf_text = buf.getvalue()

# ------------------------ Filters ------------------------
cg, cd, cr = st.columns([1.2,1.6,0.7])
with cg:
    options = ["ALL"] + [g["goal_id"] for g in st.session_state.goals]
    st.session_state.selected_goal = st.selectbox("Goal", options, index=1)
with cd:
    ds, de = st.date_input("Date range", value=(date.fromisoformat(st.session_state.date_start), date.fromisoformat(st.session_state.date_end)))
    st.session_state.date_start, st.session_state.date_end = ds.isoformat(), de.isoformat()
with cr:
    if st.button("Reset range"):
        st.session_state.date_start, st.session_state.date_end = "2025-10-22","2025-11-04"

gw_start, gw_end = goal_window(st.session_state.selected_goal, st.session_state.date_start, st.session_state.date_end)

# ------------------------ Tabs ------------------------
tab_overview, tab_fore, tab_perf, tab_refl = st.tabs(["Overview","Forethought","Performance","Reflection"])

# ------------------------ Overview ------------------------
with tab_overview:
    left, right = st.columns(2)
    with left:
        st.subheader("SRL Radar (Expected vs Actual)")
        a = radar_actual(st.session_state.date_start, st.session_state.date_end)
        def to_loop(points): 
            th = [p["phase"] for p in points] + [points[0]["phase"]]
            r = [p["score"] for p in points] + [points[0]["score"]]
            return th, r
        th_e, r_e = to_loop(EXPECTED); th_a, r_a = to_loop(a)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(theta=th_e, r=r_e, name="Expected", fill="toself"))
        fig.add_trace(go.Scatterpolar(theta=th_a, r=r_a, name="Actual", fill="toself"))
        fig.update_polars(radialaxis=dict(range=[0,100]))
        fig.update_layout(height=380, margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Pinned Reflection")
        st.info(st.session_state.pinned or "No takeaway pinned yet. Add one on Reflection → third turn.")
    m1, m2 = st.columns(2)
    with m1:
        st.subheader("Self‑Evaluation (Selected Goal)")
        df = pd.DataFrame([{"metric":"Confidence","value":0},{"metric":"Difficulty","value":0},{"metric":"Satisfaction","value":0}])
        # compute
        rsel = [r for r in reflections if st.session_state.selected_goal=="ALL" or r["goal_id"]==st.session_state.selected_goal]
        if rsel:
            conf = np.mean([r["self_eval_confidence"] for r in rsel])/5*100
            diff = np.mean([r["self_eval_difficulty"] for r in rsel])/5*100
            sat  = np.mean([r["self_eval_satisfaction"] for r in rsel])/5*100
            df = pd.DataFrame([{"metric":"Confidence","value":conf},{"metric":"Difficulty","value":diff},{"metric":"Satisfaction","value":sat}])
        figb = go.Figure(data=[go.Bar(x=df["metric"], y=df["value"])])
        figb.update_yaxes(range=[0,100])
        figb.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(figb, use_container_width=True)
    with m2:
        st.subheader("Sentiment Over Reflections")
        s = pd.DataFrame({"idx": np.arange(1,len(reflections)+1), "sentiment": [r["sentiment"] for r in reflections]})
        figl = go.Figure(go.Scatter(x=s["idx"], y=s["sentiment"], mode="lines+markers"))
        figl.update_yaxes(range=[-1,1])
        figl.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(figl, use_container_width=True)

    st.subheader("Overview Assistant")
    st.caption("Summaries grounded by uploaded PDFs (first ~5 pages). 15 chats/hour globally; 1-hour cooldown after limit.")
    cooldown_left = max(0, int((st.session_state.cooldown_until - time.time())//60))
    blocked = time.time() < st.session_state.cooldown_until
    for role, text in st.session_state.chat_log["overview"]:
        st.markdown(f"**{'Agent' if role=='agent' else 'You'}:** {text}")
    col_inp, col_btn = st.columns([0.8,0.2])
    with col_inp:
        overview_input = st.text_input("Type...", key="ov_inp", disabled=blocked or st.session_state.turns["overview"]>=2)
    with col_btn:
        if st.button("Send (Overview)", disabled=blocked or st.session_state.turns["overview"]>=2 or not st.session_state.get("ov_inp")):
            if st.session_state.chat_count >= 15:
                st.session_state.cooldown_until = time.time() + 60*60
            else:
                st.session_state.chat_log["overview"].append(("user", st.session_state.ov_inp))
                reply = grounded_summary(st.session_state.pdf_text)
                st.session_state.chat_log["overview"].append(("agent", reply))
                st.session_state.turns["overview"] += 1
                st.session_state.chat_count += 1
            st.experimental_rerun()
    if blocked:
        st.warning(f"Chat paused: cooldown ~{cooldown_left} min. Consider asking your teacher.")

# ------------------------ Forethought ------------------------
with tab_fore:
    st.subheader("Goals (Effort-weighted completion)")
    goals_df = pd.DataFrame(st.session_state.goals)
    tasks_df = pd.DataFrame(st.session_state.tasks)
    rows = []
    for _, g in goals_df.iterrows():
        subset = tasks_df[tasks_df["goal_id"].eq(g["goal_id"])]
        total_eff = subset["effort"].sum()
        done_eff = subset.loc[subset["completed"], "effort"].sum()
        pct = (done_eff / total_eff * 100) if total_eff else 0
        rows.append({"title":g["title"], "pct": round(pct,1)})
    pg = pd.DataFrame(rows)
    figd = make_subplots(rows=1, cols=len(pg), specs=[[{"type":"domain"}]*len(pg)])
    for i,row in pg.reset_index(drop=True).iterrows():
        figd.add_trace(go.Pie(values=[row["pct"], 100-row["pct"]], labels=["Done","Remain"], hole=.6, showlegend=False, textinfo="none"), 1, i+1)
        figd.add_annotation(text=f"{row['title']}<br><b>{row['pct']}%</b>", x=i/len(pg)+0.15, y=0.5, showarrow=False, font=dict(size=12))
    figd.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(figd, use_container_width=True)

    st.divider()
    st.subheader("Progress by Activity (Est vs Act days)")
    sel = st.session_state.selected_goal if st.session_state.selected_goal!="ALL" else "G1"
    g_tasks = tasks_df[tasks_df["goal_id"].eq(sel)].copy()
    gw_days = days_between(*goal_window(sel, st.session_state.date_start, st.session_state.date_end))
    tot_eff = g_tasks["effort"].sum() if not g_tasks.empty else 0
    if not g_tasks.empty and tot_eff>0:
        g_tasks["est_days"] = gw_days * (g_tasks["effort"] / tot_eff)
        ratio = (g_tasks["act_mins"] / g_tasks["est_mins"]).replace([np.inf,np.nan], 0).clip(lower=0)
        g_tasks["act_days"] = np.minimum(g_tasks["est_days"], g_tasks["est_days"] * ratio)
    else:
        g_tasks["est_days"] = 0.0
        g_tasks["act_days"] = 0.0
    figp = go.Figure()
    figp.add_trace(go.Bar(y=g_tasks["title"], x=g_tasks["est_days"], name="Est days", orientation="h"))
    figp.add_trace(go.Bar(y=g_tasks["title"], x=g_tasks["act_days"], name="Act days", orientation="h"))
    figp.update_layout(barmode="overlay", height=360, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(figp, use_container_width=True)

# ------------------------ Performance ------------------------
with tab_perf:
    st.subheader("Error Frequency")
    in_range = [a for a in learning_attempts if within_range(a["timestamp"], st.session_state.date_start, st.session_state.date_end)]
    freq = {}
    for a in in_range:
        for tag in a["error_tags"]:
            freq[tag] = freq.get(tag,0)+1
    ef = pd.DataFrame([{"error":k,"count":v} for k,v in freq.items()]).sort_values("count", ascending=False)
    if not ef.empty:
        figef = go.Figure(go.Bar(x=ef["count"], y=ef["error"], orientation="h"))
        figef.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(figef, use_container_width=True)
    else:
        st.info("No errors recorded in range.")

    st.subheader("Time on Task by Goal")
    tbg_rows = []
    for gid in {a["goal_id"] for a in learning_attempts}:
        time_sum = sum(a["time_spent_mins"] for a in learning_attempts if a["goal_id"]==gid)
        tbg_rows.append({"goal_id": gid, "time": time_sum})
    tbg = pd.DataFrame(tbg_rows)
    figtg = go.Figure(go.Bar(x=tbg["goal_id"], y=tbg["time"]))
    figtg.update_yaxes(title="Minutes")
    figtg.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(figtg, use_container_width=True)

# ------------------------ Reflection ------------------------
with tab_refl:
    st.subheader("Strategy Word Cloud (green=helps, red=less effective)")
    counts = strategies_counts(st.session_state.selected_goal)
    if counts:
        def color_func(word, *args, **kwargs):
            if word in EFFECTIVE: return COLORS["green"]
            if word in INEFFECTIVE: return COLORS["red"]
            return COLORS["gray"]
        wc = WordCloud(width=900, height=300, background_color="white", prefer_horizontal=0.95, color_func=lambda *a, **k: None)
        wc.generate_from_frequencies(counts)
        # Recolor after generate
        img = wc.to_image().convert("RGBA")
        # simple recolor pass (approximate): leave as is, legend indicates mapping
        st.image(img, use_column_width=True)
        st.caption("Legend: green=effective (drawing diagrams, explaining aloud, self-testing, summarising steps); red=less effective (re-reading notes, scrolling quickly, guessing answers).")
    else:
        st.info("No strategies yet for this selection.")

    st.subheader("Sentiment Over Time")
    s_series = pd.DataFrame({"idx": np.arange(1,len(reflections)+1), "sentiment": [r["sentiment"] for r in reflections]})
    figl2 = go.Figure(go.Scatter(x=s_series["idx"], y=s_series["sentiment"], mode="lines+markers"))
    figl2.update_yaxes(range=[-1,1])
    figl2.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(figl2, use_container_width=True)

    st.subheader("Reflector (pin last sentence to Overview)")
    cooldown_left = max(0, int((st.session_state.cooldown_until - time.time())//60))
    blocked = time.time() < st.session_state.cooldown_until
    for role, text in st.session_state.chat_log["reflection"]:
        st.markdown(f"**{'Agent' if role=='agent' else 'You'}:** {text}")
    col_inp, col_btn = st.columns([0.8,0.2])
    with col_inp:
        refl_inp = st.text_input("Type...", key="refl_inp", disabled=blocked or st.session_state.turns["reflection"]>=2)
    with col_btn:
        if st.button("Send (Reflection)", disabled=blocked or st.session_state.turns["reflection"]>=2 or not st.session_state.get("refl_inp")):
            if st.session_state.chat_count >= 15:
                st.session_state.cooldown_until = time.time() + 60*60
            else:
                st.session_state.chat_log["reflection"].append(("user", st.session_state.refl_inp))
                seq = [
                    "Name one you'll drop next time—and why.",
                    "Write a 1-sentence takeaway I can pin to Overview."
                ]
                idx = min(st.session_state.turns["reflection"], 1)
                reply = seq[idx]
                st.session_state.chat_log["reflection"].append(("agent", reply))
                st.session_state.turns["reflection"] += 1
                st.session_state.chat_count += 1
                # If this was the third user message, pin it
                if st.session_state.turns["reflection"] >= 2:
                    st.session_state.pinned = st.session_state.refl_inp
            st.experimental_rerun()
    if blocked:
        st.warning(f"Chat paused: cooldown ~{cooldown_left} min. Consider asking your teacher.")
