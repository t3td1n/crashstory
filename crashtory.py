import streamlit as st
import hashlib
import hmac
import pandas as pd
import math
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Crashtory V3",
    layout="wide"
)

st.title("🎲 Crashtory V3")
st.subheader("Stake Crash Historical Generator With Estimated Timestamps")

seed = st.text_input(
    "Seed",
    placeholder="Enter seed"
)

latest_hash = st.text_input(
    "Latest Hash",
    placeholder="Enter latest hash"
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
    value=True
)

show_stats = st.checkbox(
    "Show Statistics",
    value=True
)

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
        (2 ** 32) /
        (value + 1)
    ) * 0.99

def estimate_round_duration(
    multiplier
):
    """
    Estimated round duration
    in seconds.
    """

    if multiplier <= 1:
        return 10

    return max(
        10,
        12 + (
            6 *
            math.log(
                multiplier
            )
        )
    )

if st.button(
    "Generate"
):

    if not seed.strip():
        st.error(
            "Seed is required."
        )
        st.stop()

    if not latest_hash.strip():
        st.error(
            "Latest Hash is required."
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

    progress = st.progress(
        0
    )

    for i in range(
        rounds
    ):
        multiplier = (
            calculate_multiplier(
                current_hash,
                seed
            )
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

            duration_seconds = (
                estimate_round_duration(
                    multiplier
                )
            )

            current_time -= timedelta(
                seconds=
                duration_seconds
            )

        data.append(
            {
                "Round":
                    i + 1,

                "Timestamp":
                    timestamp_value,

                "Hash":
                    current_hash,

                "Multiplier":
                    f"{int(multiplier * 100) / 100:.2f}x"
            }
        )

        current_hash = (
            hashlib.sha256(
                current_hash.encode()
            )
            .hexdigest()
        )

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

    df = pd.DataFrame(
        data
    )

    if not show_hashes:
        df = df.drop(
            columns=["Hash"]
        )

    st.success(
        f"Generated {len(df):,} historical outputs"
    )

    if show_stats:

        st.header(
            "📊 Statistics"
        )

        avg_multiplier = (
            sum(multipliers)
            /
            len(multipliers)
        )

        highest_multiplier = max(
            multipliers
        )

        median_multiplier = (
            pd.Series(
                multipliers
            ).median()
        )

        col1, col2, col3 = st.columns(
            3
        )

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

        with col3:
            st.metric(
                "Generated Rounds",
                f"{len(multipliers):,}"
            )

        if generate_timestamps:

            st.header(
                "🕒 Timeline"
            )

            timespan = (
                parsed_timestamp
                -
                current_time
            )

            c1, c2, c3 = st.columns(
                3
            )

            with c1:

                st.metric(
                    "Latest Timestamp",
                    parsed_timestamp.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )

            with c2:

                st.metric(
                    "Earliest Estimate",
                    current_time.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )

            with c3:

                st.metric(
                    "Estimated Timespan",
                    str(
                        timespan
                    ).split(
                        "."
                    )[0]
                )

    st.header(
        "📜 Historical Outputs"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = (
        df.to_csv(
            index=False
        )
        .encode(
            "utf-8"
        )
    )

    st.download_button(
        "Download CSV",
        csv,
        "crashtory_v3.csv",
        "text/csv"
    )
