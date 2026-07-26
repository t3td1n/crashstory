import streamlit as st
import hashlib
import hmac
import pandas as pd
import math
from datetime import datetime, timedelta
from collections import Counter

st.set_page_config(
    page_title="Crashtory V3.1",
    layout="wide"
)

st.title("🎲 Crashtory V3.1")
st.subheader(
    "Stake Crash Historical Generator With Estimated Timestamps"
)

# ==========================
# INPUTS
# ==========================

latest_hash = st.text_input(
    "Latest Hash",
    placeholder="Enter latest hash"
)

seed = st.text_input(
    "Seed",
    placeholder="Enter seed"
)

st.subheader("🕒 Reference Timestamp")

col1, col2 = st.columns(2)

with col1:
    known_date = st.date_input(
        "Date of Latest Hash"
    )

with col2:
    known_time = st.time_input(
        "Time of Latest Hash"
    )

generate_timestamps = st.checkbox(
    "Generate Estimated Timestamps",
    value=True
)

rounds = st.number_input(
    "Number of Historical Outputs",
    min_value=1,
    max_value=50000,
    value=1000
)

show_hashes = st.checkbox(
    "Show Hashes",
    value=False
)

show_stats = st.checkbox(
    "Show Statistics",
    value=True
)

# ==========================
# FUNCTIONS
# ==========================

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

    return (
        ((2 ** 32) / (value + 1))
        * 0.99
    )

def estimate_round_duration(
    multiplier
):
    base_time = 18

    growth_time = (
        8 *
        math.log(
            max(multiplier, 1)
        )
    )

    return (
        base_time +
        growth_time
    )

def color_multiplier(val):

    try:

        num = float(
            str(val)
            .replace("x", "")
        )

        if num >= 2:

            return (
                "color:#00ff66;"
                "font-weight:bold;"
            )

        return "color:gray;"

    except:

        return ""

# ==========================
# GENERATE
# ==========================

if st.button("Generate"):

    if not latest_hash.strip():

        st.error(
            "Latest Hash is required."
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

            timestamp_value = (
                current_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            current_time -= timedelta(
                seconds=
                estimate_round_duration(
                    multiplier
                )
            )

        data.append(
            {
                "Round": i + 1,
                "Timestamp": timestamp_value,
                "Hash": current_hash,
                "Multiplier":
                    f"{multiplier:.2f}x"
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
                    (i + 1) / rounds,
                    1.0
                )
            )

    # Continue with your statistics, streak analysis,
    # timeline analysis, styled dataframe and CSV export.
