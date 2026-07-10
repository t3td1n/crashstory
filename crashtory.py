import streamlit as st
import hashlib
import hmac
import pandas as pd
from collections import Counter

st.set_page_config(
    page_title="Crashtory",
    layout="wide"
)

st.title("🎲 Crashtory")
st.subheader("Stake Crash Historical Generator")

seed = st.text_input(
    "Seed",
    placeholder="Enter seed"
)

latest_hash = st.text_input(
    "Latest Hash",
    placeholder="Enter latest hash"
)

rounds = st.number_input(
    "Number of historical outputs",
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


def calculate_multiplier(hash_value, seed_value):
    digest = hmac.new(
        hash_value.encode(),
        seed_value.encode(),
        hashlib.sha256
    ).hexdigest()

    value = int(digest[:8], 16)

    return (
        (2 ** 32) /
        (value + 1)
    ) * 0.99


if st.button("Generate"):

    if not seed.strip():
        st.error("Seed is required.")
        st.stop()

    if not latest_hash.strip():
        st.error("Latest hash is required.")
        st.stop()

    current_hash = latest_hash.strip().lower()

    data = []
    multipliers = []

    progress = st.progress(0)

    for i in range(rounds):

        multiplier = calculate_multiplier(
            current_hash,
            seed
        )

        multipliers.append(multiplier)

        data.append({
            "Round": i + 1,
            "Hash": current_hash,
            "Multiplier": f"{int(multiplier * 100) / 100:.2f}x"
        })

        current_hash = hashlib.sha256(
            current_hash.encode()
        ).hexdigest()

        if i % max(1, rounds // 100) == 0:
            progress.progress(
                min((i + 1) / rounds, 1.0)
            )

    df = pd.DataFrame(data)

    if not show_hashes:
        df = df.drop(columns=["Hash"])

    def color_multiplier(val):
        num = float(str(val).replace("x", ""))

        if num >= 2:
            return "color: #00ff66; font-weight: bold;"
        else:
            return "color: gray;"

    styled_df = df.style.map(
        color_multiplier,
        subset=["Multiplier"]
    )

    st.success(
        f"Generated {len(df):,} historical outputs"
    )

    if show_stats:

        st.header("📊 Statistics")

        avg_multiplier = sum(multipliers) / len(multipliers)
        highest_multiplier = max(multipliers)
        median_multiplier = sorted(multipliers)[
            len(multipliers) // 2
        ]

        hit_2x = sum(1 for x in multipliers if x >= 2)
        hit_10x = sum(1 for x in multipliers if x >= 10)
        hit_100x = sum(1 for x in multipliers if x >= 100)

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

        st.subheader("🔥 < 2x Streak Analysis")

        streaks = []
        current_streak = 0

        for value in multipliers:

            if value < 2:
                current_streak += 1
            else:

                if current_streak > 0:
                    streaks.append(current_streak)

                current_streak = 0

        if current_streak > 0:
            streaks.append(current_streak)

        if streaks:

            streak_counter = Counter(streaks)

            streak_df = pd.DataFrame(
                sorted(
                    streak_counter.items()
                ),
                columns=[
                    "Streak Length",
                    "Occurrences"
                ]
            )

            st.dataframe(
                streak_df,
                use_container_width=True
            )

            st.metric(
                "Maximum <2x Streak",
                max(streaks)
            )

    st.header("📜 Historical Outputs")

    st.write(styled_df)

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "crashtory.csv",
        "text/csv"
    )
