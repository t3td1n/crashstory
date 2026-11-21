import streamlit as st
import hashlib
import hmac
import pandas as pd
import math
from datetime import datetime, timedelta
from collections import Counter

st.set_page_config(
    page_title="Crashtory V3.4",
    layout="wide"
)

# =====================================================================
# THEME (cyberpunk / matrix, minimalist)
# To change the accent colour, edit --neon below AND primaryColor in
# .streamlit/config.toml
# =====================================================================
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;800&display=swap');

:root {
    --bg: #05080a;
    --panel: #0b1110;
    --line: #12352a;
    --neon: #00ff9c;
    --text: #b8f5d8;
    --muted: #5f7a6e;
}

/* ---------- base ---------- */
.stApp {
    background-color: var(--bg);
    background-image:
        linear-gradient(rgba(0,255,156,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,156,0.035) 1px, transparent 1px);
    background-size: 32px 32px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
}

/* subtle CRT scanlines */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        rgba(0,0,0,0.18) 0px,
        rgba(0,0,0,0.18) 1px,
        transparent 1px,
        transparent 3px
    );
    z-index: 9999;
}

.block-container {
    max-width: 1100px;
    padding-top: 2.5rem;
}

/* hide streamlit chrome */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

/* ---------- hero ---------- */
.ct-hero { margin-bottom: 2.2rem; }
.ct-tag {
    color: var(--muted);
    font-size: 0.72rem;
    letter-spacing: 0.3em;
}
.ct-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.2rem;
    font-weight: 800;
    color: var(--neon);
    letter-spacing: 0.12em;
    line-height: 1.1;
    margin: 0.3rem 0;
    text-shadow: 0 0 8px rgba(0,255,156,0.55), 0 0 28px rgba(0,255,156,0.25);
}
.ct-sub {
    color: var(--text);
    font-size: 0.95rem;
    opacity: 0.85;
}
.ct-cursor {
    color: var(--neon);
    animation: ct-blink 1s steps(1) infinite;
}
@keyframes ct-blink { 50% { opacity: 0; } }

/* ---------- section headers ---------- */
.ct-section {
    font-family: 'JetBrains Mono', monospace;
    color: var(--neon);
    font-size: 0.85rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--line);
    padding-bottom: 0.45rem;
    margin: 2rem 0 1rem 0;
}
.ct-section span { color: var(--muted); }

/* ---------- labels ---------- */
[data-testid="stWidgetLabel"] p {
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.72rem !important;
}

/* ---------- inputs ---------- */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"] > div {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 2px !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--neon) !important;
    box-shadow: 0 0 0 1px var(--neon), 0 0 12px rgba(0,255,156,0.25) !important;
}
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: var(--panel) !important;
    color: var(--neon) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ---------- buttons ---------- */
.stButton > button,
.stDownloadButton > button {
    background: transparent;
    color: var(--neon);
    border: 1px solid var(--neon);
    border-radius: 2px;
    padding: 0.6rem 2.2rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-weight: 600;
    transition: all 0.15s ease;
}
.stButton > button p,
.stDownloadButton > button p {
    font-family: 'JetBrains Mono', monospace;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stButton > button:focus:not(:active) {
    background: var(--neon);
    color: var(--bg);
    border-color: var(--neon);
    box-shadow: 0 0 18px rgba(0,255,156,0.55);
}
.stButton > button:hover p,
.stDownloadButton > button:hover p { color: var(--bg) !important; }
.stButton > button:active { transform: translateY(1px); }

/* ---------- metrics ---------- */
[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 2px solid var(--neon);
    border-radius: 2px;
    padding: 0.9rem 1rem;
}
[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.7rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--neon) !important;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    text-shadow: 0 0 10px rgba(0,255,156,0.35);
}

/* ---------- progress bar ---------- */
.stProgress > div > div > div > div {
    background: var(--neon) !important;
    box-shadow: 0 0 10px var(--neon);
}

/* ---------- alerts & tables ---------- */
[data-testid="stAlert"] {
    background: var(--panel) !important;
    border: 1px solid var(--line);
    border-radius: 2px;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 2px;
}

/* ---------- scrollbar ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--line); }
::-webkit-scrollbar-thumb:hover { background: var(--neon); }

/* ---------- footer ---------- */
.ct-foot {
    color: var(--muted);
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-align: center;
    margin-top: 3rem;
    opacity: 0.7;
}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)


def section(num, label):
    st.markdown(
        f'<div class="ct-section"><span>{num}</span> // {label}</div>',
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="ct-hero">
        <div class="ct-tag">SYS://CRASHTORY  v3.4</div>
        <div class="ct-title">CRASHTORY</div>
        <div class="ct-sub">> stake crash history generator<span class="ct-cursor">_</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# INPUTS
# =====================================================================
section("01", "Input")

latest_hash = st.text_input(
    "Latest Hash",
    placeholder="paste 64-character hash"
)

seed = st.text_input(
    "Seed",
    placeholder="paste seed"
)

section("02", "Reference Time (UTC)")

col1, col2 = st.columns(2)

with col1:
    known_date = st.date_input(
        "Date of Latest Hash"
    )

with col2:
    known_time = st.time_input(
        "Time of Latest Hash",
        step=1
    )

section("03", "Options")

rounds = st.number_input(
    "Number of historical outputs",
    min_value=1,
    max_value=50000,
    value=1000
)

o1, o2, o3 = st.columns(3)

with o1:
    generate_timestamps = st.checkbox(
        "Estimated Timestamps",
        value=True
    )

with o2:
    show_hashes = st.checkbox(
        "Show Hashes",
        value=False
    )

with o3:
    show_stats = st.checkbox(
        "Show Statistics",
        value=True
    )

st.write("")


# =====================================================================
# CORE MATH (unchanged)
# =====================================================================
def calculate_multiplier(
    hash_value,
    seed_value
):
    digest = hmac.new(
        hash_value.encode(),
        seed_value.encode(),
        hashlib.sha256
    ).hexdigest()

    value = int(
        digest[:8],
        16
    )

    # Stake shows instant crashes as 1.00x, never below
    return max(1.0, ((2 ** 32) / (value + 1)) * 0.99)


# --- Duration formula ---
# Originally fitted on 3,147 real rounds across 3 days.
# DURATION_DELAY recalibrated on 1,041 matched real rounds (Nov 20-21, 2026):
# the old value drifted ~0.031s per round (-32s after 1,040 rounds).
# DURATION_K unchanged (error was constant regardless of multiplier).
DURATION_DELAY = 11.508714            # launch-pad seconds before liftoff
DURATION_K = 0.059885340656503055     # growth rate per second


def estimate_round_duration(multiplier):
    growth_time = math.log(max(multiplier, 1)) / DURATION_K
    return DURATION_DELAY + growth_time


# =====================================================================
# GENERATE
# =====================================================================
if st.button("Generate"):

    if not latest_hash.strip():
        st.error(
            "Latest hash is required."
        )
        st.stop()

    if not seed.strip():
        st.error(
            "Seed is required."
        )
        st.stop()

    parsed_timestamp = datetime.combine(
        known_date,
        known_time
    )

    current_hash = (
        latest_hash
        .strip()
        .lower()
    )

    # current_time always holds the timestamp of the round about to be
    # recorded. Round 0 (the newest) IS the anchor you typed in, so it
    # needs no offset. Every round after that is older, and the gap back
    # to it depends on THAT round's own multiplier (its own flight time).
    current_time = parsed_timestamp

    data = []
    multipliers = []

    progress = st.progress(0)

    for i in range(rounds):

        multiplier = calculate_multiplier(
            current_hash,
            seed
        )

        multipliers.append(
            multiplier
        )

        timestamp_value = ""

        if generate_timestamps:

            if i > 0:
                duration_seconds = estimate_round_duration(
                    multiplier
                )
                current_time -= timedelta(
                    seconds=duration_seconds
                )

            timestamp_value = (
                current_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        data.append(
            {
                "Round": i + 1,
                "Timestamp": timestamp_value,
                "Hash": current_hash,
                "Multiplier": (
                    f"{int(multiplier * 100) / 100:.2f}x"
                )
            }
        )

        current_hash = hashlib.sha256(
            current_hash.encode()
        ).hexdigest()

        if i % max(
            1,
            rounds // 100
        ) == 0:

            progress.progress(
                min(
                    (i + 1)
                    /
                    rounds,
                    1.0
                )
            )

    progress.progress(1.0)

    df = pd.DataFrame(data)

    if not show_hashes:

        df = df.drop(
            columns=["Hash"]
        )

    def color_multiplier(val):

        num = float(
            str(val).replace(
                "x",
                ""
            )
        )

        if num >= 2:

            return (
                "color: #00ff9c;"
                "font-weight: bold;"
            )

        return "color: #5f7a6e;"

    styled_df = df.style.map(
        color_multiplier,
        subset=["Multiplier"]
    )

    st.success(
        f"> {len(df):,} rounds generated"
    )

    if show_stats:

        section("04", "Statistics")

        avg_multiplier = (
            sum(multipliers)
            /
            len(multipliers)
        )

        highest_multiplier = max(
            multipliers
        )

        median_multiplier = (
            sorted(multipliers)[
                len(multipliers) // 2
            ]
        )

        hit_2x = sum(
            1
            for x in multipliers
            if x >= 2
        )

        hit_10x = sum(
            1
            for x in multipliers
            if x >= 10
        )

        hit_100x = sum(
            1
            for x in multipliers
            if x >= 100
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Average Multiplier",
                f"{avg_multiplier:.2f}x"
            )

            st.metric(
                "Median Multiplier",
                f"{median_multiplier:.2f}x"
            )

        with col2:

            st.metric(
                "Highest Multiplier",
                f"{highest_multiplier:.2f}x"
            )

            st.metric(
                "Hit Rate ≥2x",
                f"{(hit_2x / len(multipliers)) * 100:.2f}%"
            )

        with col3:

            st.metric(
                "Hit Rate ≥10x",
                f"{(hit_10x / len(multipliers)) * 100:.2f}%"
            )

            st.metric(
                "Hit Rate ≥100x",
                f"{(hit_100x / len(multipliers)) * 100:.2f}%"
            )

        section("05", "< 2x Streak Analysis")

        streaks = []

        current_streak = 0

        for value in multipliers:

            if value < 2:

                current_streak += 1

            else:

                if current_streak > 0:

                    streaks.append(
                        current_streak
                    )

                current_streak = 0

        if current_streak > 0:

            streaks.append(
                current_streak
            )

        if streaks:

            streak_counter = Counter(
                streaks
            )

            streak_df = pd.DataFrame(
                sorted(
                    streak_counter.items()
                ),
                columns=[
                    "Streak Length",
                    "Occurrences"
                ]
            )

            s1, s2 = st.columns([3, 1])

            with s1:
                st.dataframe(
                    streak_df,
                    use_container_width=True,
                    hide_index=True
                )

            with s2:
                st.metric(
                    "Maximum <2x Streak",
                    max(streaks)
                )

        if generate_timestamps:

            section("06", "Timeline")

            span = (
                parsed_timestamp
                -
                current_time
            )

            t1, t2, t3 = st.columns(3)

            with t1:

                st.metric(
                    "Latest Timestamp",
                    parsed_timestamp.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )

            with t2:

                st.metric(
                    "Earliest Estimate",
                    current_time.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )

            with t3:

                st.metric(
                    "Estimated Timespan",
                    str(span).split(".")[0]
                )

    section("07", "Historical Outputs")

    st.write(
        styled_df
    )

    csv = (
        df.to_csv(
            index=False
        )
        .encode("utf-8")
    )

    st.download_button(
        "Download CSV",
        csv,
        "crashtory_v3_4.csv",
        "text/csv"
    )

st.markdown(
    '<div class="ct-foot">CRASHTORY // END OF LINE</div>',
    unsafe_allow_html=True
)
File 2: theme settings (new file)
This file makes Streamlit's built-in parts match the theme: the calendar popup, checkboxes, and table colours. Without it the app still looks themed, but those parts stay in Streamlit's default style.

How to create it on GitHub:

On your repo's main page, click Add file → Create new file.
In the name box, type exactly: .streamlit/config.toml
When you type the /, GitHub automatically turns .streamlit into a folder. That's normal.
It must sit in the same place as your app file, usually the main (root) folder.
Paste this in:
[theme]
base = "dark"
primaryColor = "#00ff9c"
backgroundColor = "#05080a"
secondaryBackgroundColor = "#0b1110"
textColor = "#b8f5d8"
font = "monospace"
