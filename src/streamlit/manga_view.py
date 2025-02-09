import streamlit as st
import pandas as pd
import altair as alt


def manga_view():
    volume_dim = pd.read_csv("data/dim_volume.csv")
    titles = volume_dim["clean_title"].unique().tolist()
    # Manga selector
    selected_manga = st.selectbox(
        "# Pick a manga", titles, index=95, key="selected_manga"
    )
    filtered_manga = volume_dim[volume_dim["clean_title"] == selected_manga]
    st.header(f"Characters per volume: {selected_manga}")
    bar_chart_chars = (
        alt.Chart(filtered_manga)
        .mark_bar()
        .encode(
            x=alt.X("volume_number:N", title="Volume #"),
            y=alt.Y("length:Q", title="# of characters"),
            tooltip=[
                alt.Tooltip("volume_number:N", title="Volume #"),
                alt.Tooltip("length:Q", title="# of characters", format=","),
            ],
        )
    )
    st.altair_chart(bar_chart_chars)
