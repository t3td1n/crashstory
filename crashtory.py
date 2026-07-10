import streamlit as st
import hashlib
import hmac
import pandas as pd

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


def calculate_multiplier(hash_value, seed_value):
    """
    Stake formula based on your verification page:
    HMAC_SHA256(hash, seed)
    """

    digest = hmac.new(
        hash_value.encode(),
        seed_value.encode(),
        hashlib.sha256
    ).hexdigest()

    first_8 = digest[:8]
    decimal_value = int(first_8, 16)

    result = (
        (2 ** 32) /
        (decimal_value + 1)
    ) * 0.99

    return result


if st.button("Generate"):

    if not seed.strip():
        st.error("Seed is required.")
        st.stop()

    if not latest_hash.strip():
        st.error("Latest hash is required.")
        st.stop()

    current_hash = latest_hash.strip().lower()

    data = []

    progress = st.progress(0)

    for i in range(rounds):

        multiplier = calculate_multiplier(
            current_hash,
            seed
        )

        data.append(
            {
                "Round": i + 1,
                "Hash": current_hash,
                "Multiplier": round(multiplier, 8)
            }
        )

        # Older round
        current_hash = hashlib.sha256(
            current_hash.encode()
        ).hexdigest()

        if i % max(1, rounds // 100) == 0:
            progress.progress(
                min((i + 1) / rounds, 1.0)
            )

    df = pd.DataFrame(data)

    st.success(
        f"Generated {len(df):,} historical outputs"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "crashtory.csv",
        "text/csv"
    )
