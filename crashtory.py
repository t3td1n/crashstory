import streamlit as st
import hashlib
import hmac
import pandas as pd

st.set_page_config(page_title="Stake Crash History Generator", layout="wide")

st.title("Stake Crash Historical Output Generator")

seed = st.text_input("Seed")
latest_hash = st.text_input("Latest Hash")
rounds = st.number_input("Number of historical outputs", min_value=1, max_value=50000, value=1000)


def multiplier(hash_value, seed_value):
    digest = hmac.new(
        seed_value.encode(),
        hash_value.encode(),
        hashlib.sha256
    ).hexdigest()

    n = int(digest[:8], 16)
    return (2**32 / (n + 1)) * 0.99


if st.button("Generate"):
    if not seed or not latest_hash:
        st.error("Provide seed and latest hash")
    else:
        rows = []
        current_hash = latest_hash.strip().lower()

        progress = st.progress(0)

        for i in range(int(rounds)):
            rows.append([
                i + 1,
                current_hash,
                round(multiplier(current_hash, seed), 8)
            ])

            current_hash = hashlib.sha256(current_hash.encode()).hexdigest()

            if i % max(1, rounds // 100) == 0:
                progress.progress(min((i + 1) / rounds, 1.0))

        df = pd.DataFrame(rows, columns=["Round", "Hash", "Multiplier"])

        st.success(f"Generated {len(df):,} historical outputs")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download CSV",
            csv_data,
            file_name="stake_crash_history.csv",
            mime="text/csv"
        )
