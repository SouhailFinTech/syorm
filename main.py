import streamlit as st
import google.generativeai as genai
from datetime import datetime
import random

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AlgoQuant AI Coach",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── STYLING ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
* { font-family: 'Space Grotesk', sans-serif; }
html, body, [data-testid="stAppViewContainer"] { background:#080B10; color:#E2E8F0; }
[data-testid="stHeader"] { background:transparent; }
#MainMenu, footer { visibility:hidden; }

.topbar {
    display:flex; align-items:center; justify-content:space-between;
    padding:1.2rem 0 1.8rem 0;
    border-bottom:1px solid #1A2030; margin-bottom:1.8rem;
}
.logo { font-size:1.1rem; font-weight:700; letter-spacing:.08em; color:#00FFB2; }
.logo span { color:#E2E8F0; }
.badge {
    font-size:.7rem; font-weight:600; letter-spacing:.1em; color:#00FFB2;
    border:1px solid #00FFB230; padding:3px 10px; border-radius:20px; background:#00FFB208;
}
.section-label {
    font-size:.7rem; font-weight:700; letter-spacing:.1em;
    color:#4A5568; text-transform:uppercase; margin-bottom:.5rem;
}
.card {
    background:#0D1117; border:1px solid #1A2030;
    border-radius:12px; padding:1.2rem;
    position:relative; margin-bottom:1rem;
}
.card-accent::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#00FFB2,#0088FF);
    border-radius:12px 12px 0 0;
}
.tag {
    display:inline-block; font-size:.65rem; font-weight:700;
    letter-spacing:.1em; text-transform:uppercase;
    color:#00FFB2; border:1px solid #00FFB230;
    padding:2px 8px; border-radius:4px; margin-bottom:.8rem;
}
.topic-card {
    background:#0D1117; border:1px solid #1A2030; border-radius:10px;
    padding:12px 14px; cursor:pointer; margin-bottom:8px;
    transition:border-color .15s;
}
.topic-card:hover { border-color:#00FFB240; }
.topic-title { font-size:.88rem; font-weight:600; color:#E2E8F0; }
.topic-why { font-size:.75rem; color:#4A5568; margin-top:3px; }
.platform-pill {
    display:inline-block; font-size:.65rem; font-weight:600;
    background:#13191F; border:1px solid #1A2030;
    color:#6B7280; padding:2px 8px; border-radius:20px; margin:2px;
}
.stButton>button {
    background:#00FFB2 !important; color:#080B10 !important;
    border:none !important; border-radius:8px !important;
    font-weight:700 !important; font-size:.88rem !important;
    width:100% !important; transition:opacity .15s !important;
}
.stButton>button:hover { opacity:.85 !important; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#0D1117 !important; border:1px solid #1A2030 !important;
    border-radius:8px !important; color:#E2E8F0 !important;
    font-family:'Space Grotesk',sans-serif !important;
}
.stSelectbox>div>div {
    background:#0D1117 !important; border:1px solid #1A2030 !important;
    border-radius:8px !important; color:#E2E8F0 !important;
}
.stRadio>div { gap:.5rem; }
.stRadio label { font-size:.85rem !important; }
</style>
""", unsafe_allow_html=True)

# ── SYSTEM PROMPT ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are the personal AI Sales Manager and Content Strategist for @AlgoQuantTrading.

ABOUT THE BRAND:
- Creator: Quantitative Finance Engineer, Master's degree, Morocco-based
- Building: Novantix Capital (multi-strategy algo trading firm)
- Channel: @AlgoQuantTrading on YouTube (1 month old, growing fast)
- Products: Free MT5 EA (Triple EMA+ATR), future Python→MQL5 SaaS, paid EA versions, trading courses

TARGET AUDIENCE (all levels, all traders):
- Python developers who want MT5 automation
- MT4/MT5 retail traders who want algos but can't code  
- Quant-curious traders tired of indicators
- Professional quants interested in systematic strategies
- They have money. They've bought courses. They're skeptical of hype.
- They respond to: PROOF, specificity, technical credibility, real results
- They ignore: vague claims, "financial freedom", fake screenshots

YOUR 4 SELLING GOALS (always serve one of these per output):
1. Drive traffic to YouTube channel (@AlgoQuantTrading)
2. Drive downloads of the free EA (Gumroad)
3. Sell future paid EA / course
4. Build SaaS waitlist (Python→MQL5 converter)

SALES PRINCIPLES YOU ALWAYS APPLY:
1. SPECIFICITY SELLS — "9/21/55 EMA with ATR(14)" beats "advanced algorithm"
2. PROOF OVER CLAIMS — real numbers, real screenshots, real outcomes
3. TEACH TO SELL — the tutorial IS the pitch
4. RETENTION LOOPS — every post makes them want the next thing
5. RISK REVERSAL — free, demo only, no friction
6. PLATFORM-NATIVE — each platform has its own format and rhythm

PLATFORM WRITING RULES:
- YouTube: Hook in 3 seconds. Value delivery. Strong CTA at end.
- Twitter/X: Thread format. First tweet must stop the scroll. End with CTA.
- Threads: Conversational, slightly longer than X, story-driven
- Facebook (Business): Educational tone, community feel, question-based CTAs
- TikTok: Script only. Fast cuts. Text overlay cues. Hook in first 2 seconds.
- Reddit: NO selling language. Be helpful first. Subtle brand mention only.
- Medium: Long-form. Technical depth. SEO-friendly headers. CTA at end only.

OUTPUT FORMAT (always follow this):
🔍 DIAGNOSIS — what's the angle/goal (2 lines max)
✍️ [PLATFORM NAME] OUTPUT — ready to copy-paste
🧠 WHY IT SELLS — the psychology behind it (3 lines)
⚡ POWER MOVE — one tip to amplify

TONE RULES:
- Never use: "financial freedom", "passive income", "life-changing", "amazing", "game-changer"
- Always use: specific numbers, direct verbs, short punchy sentences
- Write like a quant who knows how to sell: credible AND compelling
- Every sentence must earn its place or be cut
"""

TOPIC_POOL = [
    {"title": "I automated my trading strategy in 48 hours — here's exactly how",
     "why": "Process story → high trust, drives YouTube",
     "angle": "YouTube traffic"},
    {"title": "Why 90% of backtests are lies (and how to spot them)",
     "why": "Controversy + education = high engagement",
     "angle": "Authority building"},
    {"title": "Python traders: you're 1 script away from a live MT5 bot",
     "why": "Direct pain point for Python devs",
     "angle": "SaaS waitlist"},
    {"title": "I gave away a free trading bot. Here's what happened.",
     "why": "Story + social proof + drives EA downloads",
     "angle": "EA download"},
    {"title": "The Triple EMA strategy that actually works on BTC (with data)",
     "why": "Specific + proof-based = high credibility",
     "angle": "YouTube traffic"},
    {"title": "Building a quant firm from Morocco with $0 — week by week",
     "why": "Personal story = massive retention",
     "angle": "Channel growth"},
    {"title": "Stop using fixed stop losses. Here's why ATR is better.",
     "why": "Educational, challenges common belief",
     "angle": "YouTube traffic"},
    {"title": "How I protect my EA source code from being stolen",
     "why": "Unique technical topic no one covers",
     "angle": "Authority + YouTube"},
    {"title": "MQL5 vs Python: which one should algo traders learn first?",
     "why": "High search volume debate topic",
     "angle": "YouTube traffic"},
    {"title": "I analyzed 182 Polymarket crypto markets. Here's what I found.",
     "why": "Data-driven = instant credibility",
     "angle": "Authority building"},
    {"title": "Risk management that saved my account (ATR-based position sizing)",
     "why": "Fear-based hook, universal pain point",
     "angle": "YouTube traffic"},
    {"title": "The 3 reasons most trading bots fail in live markets",
     "why": "Problem-focused, high relevance",
     "angle": "EA + course sales"},
]

PLATFORMS = ["YouTube", "Twitter/X", "Threads", "Facebook Business", "TikTok", "Reddit", "Medium"]

GOALS = {
    "🎯 Drive YouTube traffic": "Drive viewers to subscribe to @AlgoQuantTrading YouTube channel",
    "📥 Drive EA downloads": "Get people to download the free Triple EMA+ATR EA from Gumroad",
    "💰 Sell paid product": "Build interest and intent to buy future paid EA or course",
    "🛠️ Build SaaS waitlist": "Get signups for the Python→MQL5 converter SaaS",
}

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for k, v in {
    "page": "home",
    "daily_topics": [],
    "selected_topic": None,
    "selected_goal": None,
    "history": [],
    "total_gen": 0,
    "api_key": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ────────────────────────────────────────────────────────────────────
def get_api_key():
    # Checks Streamlit Cloud Secrets FIRST, then falls back to Sidebar input
    return st.secrets.get("GEMINI_API_KEY", "") or st.session_state.api_key

def get_model():
    key = get_api_key()
    if not key:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)

def call_gemini(prompt: str) -> str:
    model = get_model()
    if not model:
        return "⚠️ No API key found. Please add 'GEMINI_API_KEY' to Streamlit Secrets or the sidebar."
    try:
        response = model.generate_content(prompt)
        st.session_state.total_gen += 1
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

def gen_daily_topics():
    st.session_state.daily_topics = random.sample(TOPIC_POOL, min(2, len(TOPIC_POOL)))

def save_history(mode, label, output):
    st.session_state.history.insert(0, {
        "mode": mode, "label": label[:55],
        "output": output,
        "time": datetime.now().strftime("%H:%M")
    })
    if len(st.session_state.history) > 20:
        st.session_state.history = st.session_state.history[:20]

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    key_input = st.text_input("Gemini API Key (Optional if set in Secrets)", type="password",
                               value=st.session_state.api_key,
                               placeholder="AIza...")
    if key_input != st.session_state.api_key:
        st.session_state.api_key = key_input

    st.markdown("---")
    st.markdown(f"**Generated:** {st.session_state.total_gen}")
    st.markdown(f"**History:** {len(st.session_state.history)} items")
    st.markdown("---")
    st.markdown("**Navigation**")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("💡 Daily Topics", use_container_width=True):
        st.session_state.page = "topics"
        if not st.session_state.daily_topics:
            gen_daily_topics()
        st.rerun()
    if st.button("✍️ Script Review", use_container_width=True):
        st.session_state.page = "review"
        st.rerun()
    if st.button("📜 History", use_container_width=True):
        st.session_state.page = "history"
        st.rerun()

# ── TOP BAR ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="logo">ALGO<span>QUANT</span> · AI COACH</div>
    <div class="badge">NOVANTIX CAPITAL</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    st.markdown("## 👋 What do you want to do today?")
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("""
        <div class="card card-accent" style="min-height:140px">
            <div class="tag">PART 1</div>
            <div style="font-size:1.1rem; font-weight:700; margin-bottom:.4rem">💡 Daily Topics</div>
            <div style="font-size:.85rem; color:#6B7280; line-height:1.6">
                Get 2 topic ideas every day.<br>
                Pick one → AI generates content<br>
                for all 7 platforms instantly.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Daily Topics →", key="h_topics"):
            st.session_state.page = "topics"
            if not st.session_state.daily_topics:
                gen_daily_topics()
            st.rerun()

    with c2:
        st.markdown("""
        <div class="card card-accent" style="min-height:140px">
            <div class="tag">PART 2</div>
            <div style="font-size:1.1rem; font-weight:700; margin-bottom:.4rem">✍️ Script Review</div>
            <div style="font-size:.85rem; color:#6B7280; line-height:1.6">
                Paste your script or content.<br>
                AI diagnoses weaknesses and<br>
                rewrites it to sell.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Script Review →", key="h_review"):
            st.session_state.page = "review"
            st.rerun()

    # Stats
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, val, label in zip(
        [s1, s2, s3, s4],
        [st.session_state.total_gen, len(st.session_state.history), 7, 4],
        ["Generated", "Saved", "Platforms", "Goals"]
    ):
        col.markdown(f"""
        <div class="card" style="text-align:center; padding:.9rem">
            <div style="font-size:1.6rem; font-weight:700; color:#00FFB2;
                        font-family:'JetBrains Mono',monospace">{val}</div>
            <div style="font-size:.7rem; color:#4A5568; margin-top:2px">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DAILY TOPICS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "topics":

    st.markdown("## 💡 Today's Topic Ideas")
    today = datetime.now().strftime("%A, %B %d")
    st.markdown(f"<div style='color:#4A5568; font-size:.85rem; margin-bottom:1.5rem'>{today}</div>",
                unsafe_allow_html=True)

    col_refresh, _ = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refresh Topics"):
            gen_daily_topics()
            st.session_state.selected_topic = None
            st.rerun()

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # Show 2 topic cards
    for i, topic in enumerate(st.session_state.daily_topics):
        is_selected = st.session_state.selected_topic == i
        border = "#00FFB2" if is_selected else "#1A2030"
        bg = "#00FFB208" if is_selected else "#0D1117"

        st.markdown(f"""
        <div style="background:{bg}; border:1px solid {border}; border-radius:12px;
                    padding:16px 18px; margin-bottom:10px;">
            <div style="font-size:.95rem; font-weight:700; color:#E2E8F0; margin-bottom:6px">
                {topic['title']}
            </div>
            <div style="font-size:.75rem; color:#4A5568; margin-bottom:8px">
                {topic['why']}
            </div>
            <div style="display:flex; gap:6px; flex-wrap:wrap">
                <span style="font-size:.65rem; color:#00FFB2; background:#00FFB210;
                             border:1px solid #00FFB230; padding:2px 8px; border-radius:20px">
                    {topic['angle']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"{'✅ Selected' if is_selected else 'Select this topic'}", key=f"topic_{i}"):
            st.session_state.selected_topic = i
            st.rerun()

    # ── After topic selected ──
    if st.session_state.selected_topic is not None:
        topic = st.session_state.daily_topics[st.session_state.selected_topic]

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Step 2 — What's the goal of this content?")

        goal_choice = st.radio(
            "",
            list(GOALS.keys()),
            label_visibility="collapsed"
        )

        st.markdown("### Step 3 — Which platforms?")
        selected_platforms = st.multiselect(
            "",
            PLATFORMS,
            default=["YouTube", "Twitter/X", "TikTok"],
            label_visibility="collapsed"
        )

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        if st.button("⚡ Generate Content for All Selected Platforms"):
            if not get_api_key():
                st.error("Add your Gemini API key in Streamlit Secrets or the sidebar first.")
            elif not selected_platforms:
                st.warning("Select at least one platform.")
            else:
                goal_desc = GOALS[goal_choice]
                platforms_str = ", ".join(selected_platforms)

                prompt = f"""
TOPIC: {topic['title']}
SELLING GOAL: {goal_desc}
PLATFORMS TO WRITE FOR: {platforms_str}

For EACH platform listed, write complete ready-to-post content.
Follow the platform writing rules exactly.
Each platform output must be clearly separated with the platform name as header.
All content must serve the selling goal: {goal_desc}
"""
                with st.spinner("Generating content for all platforms..."):
                    output = call_gemini(prompt)

                save_history("Daily Topics", topic['title'], output)

                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card card-accent">
                    <div class="tag">OUTPUT — {", ".join(selected_platforms)}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(output)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SCRIPT REVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "review":

    st.markdown("## ✍️ Script Review & Rewrite")
    st.markdown("<div style='color:#4A5568; font-size:.85rem; margin-bottom:1.5rem'>Paste anything — script, tweet, description, hook. AI will ask what you're selling first, then rewrite to convert.</div>",
                unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="section-label">What are you promoting?</div>', unsafe_allow_html=True)
        goal_choice = st.radio(
            "",
            list(GOALS.keys()),
            label_visibility="collapsed"
        )

        st.markdown('<div class="section-label" style="margin-top:1rem">Platform / Content type</div>',
                    unsafe_allow_html=True)
        platform = st.selectbox("", PLATFORMS + ["Email", "Gumroad Page", "Other"],
                                 label_visibility="collapsed")

        st.markdown('<div class="section-label" style="margin-top:1rem">Your content (paste here)</div>',
                    unsafe_allow_html=True)
        user_content = st.text_area("", height=250,
                                     placeholder="Paste your script, tweet, description, hook, email...",
                                     label_visibility="collapsed")

        st.markdown('<div class="section-label" style="margin-top:.75rem">Extra instructions (optional)</div>',
                    unsafe_allow_html=True)
        extra = st.text_input("", placeholder="e.g. keep under 60 sec, more urgency, simpler language...",
                               label_visibility="collapsed")

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        run_review = st.button("⚡ Review & Rewrite")

    with right:
        st.markdown('<div class="section-label">Output</div>', unsafe_allow_html=True)

        if run_review:
            if not get_api_key():
                st.error("Add your Gemini API key in Streamlit Secrets or the sidebar first.")
            elif not user_content.strip():
                st.warning("Paste your content on the left first.")
            else:
                goal_desc = GOALS[goal_choice]
                prompt = f"""
TASK: Review and rewrite the following content.
PLATFORM: {platform}
SELLING GOAL: {goal_desc}
EXTRA INSTRUCTIONS: {extra if extra else 'None'}

CONTENT TO REVIEW:
{user_content}

Follow the output format:
🔍 DIAGNOSIS — what's weak and why
✍️ REWRITE — complete rewrite ready to copy-paste
🧠 WHY IT SELLS — psychology behind your choices
⚡ POWER MOVE — one extra tip to amplify
"""
                with st.spinner("Reviewing..."):
                    output = call_gemini(prompt)

                save_history("Script Review", user_content[:55], output)

                st.markdown(f"""
                <div class="card card-accent">
                    <div class="tag">REVIEWED — {platform}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(output)

        elif st.session_state.history:
            last = next((h for h in st.session_state.history if h["mode"] == "Script Review"), None)
            if last:
                st.markdown(f"""
                <div class="card card-accent">
                    <div class="tag">LAST REVIEW — {last['time']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(last["output"])
            else:
                st.markdown("""
                <div class="card" style="min-height:300px; display:flex;
                     align-items:center; justify-content:center; flex-direction:column">
                    <div style="font-size:2rem; margin-bottom:1rem">✍️</div>
                    <div style="color:#4A5568; font-size:.85rem; text-align:center">
                        Paste your content on the left<br>and hit Review & Rewrite.
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "history":
    st.markdown("## 📜 History")

    if not st.session_state.history:
        st.markdown("""
        <div class="card" style="text-align:center; padding:2rem">
            <div style="color:#4A5568">No history yet. Start generating content.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for item in st.session_state.history:
            with st.expander(f"[{item['time']}] {item['mode']} — {item['label']}"):
                st.markdown(item["output"])
