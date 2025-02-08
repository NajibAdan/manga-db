import streamlit as st
import pandas as pd
import sqlite3
import altair as alt


# Query the table
manga_dim = pd.read_csv("data/dim_manga.csv")

# Pick out the titles
titles = manga_dim["clean_title"].unique().tolist()

# Set the page title and layout to wide
st.set_page_config(
    layout="wide", page_title="MangaDB - jpdb but for manga", page_icon="📖"
)

# Big title
st.title("MangaDB - Stats on your favorite manga")

# Manga selector
selected_manga = st.sidebar.multiselect(
    "Pick a manga", titles, default=["Berserk", "Bleach", "Naruto", "Dragon Ball"]
)

# 4 columns to show the bar charts
col1, col2 = st.columns(2, vertical_alignment="bottom", border=True)
col3, col4 = st.columns(2, vertical_alignment="bottom", border=True)

filtered_manga = manga_dim[manga_dim["clean_title"].isin(selected_manga)]

# Show a bar chart of mangas & num of characters
with col1:
    st.header("Numbers of characters")
    bar_chart_chars = (
        alt.Chart(filtered_manga)
        .mark_bar()
        .encode(
            x=alt.X("clean_title:N", title="Manga"),
            y=alt.Y("num_of_chrs:Q", title="# of characters"),
            tooltip=[
                alt.Tooltip("clean_title:N", title="Manga"),
                alt.Tooltip("num_of_chrs:Q", title="# of characters", format=","),
                alt.Tooltip("volume_count:Q", title="# of volumes", format=","),
            ],
        )
    )
    st.altair_chart(bar_chart_chars)

# Show a bar chart of mangas & num of unique kanji
with col2:
    st.header("Number of unique kanji")
    unique_kanji_chart = (
        alt.Chart(filtered_manga)
        .mark_bar()
        .encode(
            x=alt.X("clean_title:N", title="Manga"),
            y=alt.Y("num_of_unique_chrs:Q", title="# of unique kanji"),
            tooltip=[
                alt.Tooltip("clean_title:N", title="Manga"),
                alt.Tooltip(
                    "num_of_unique_chrs:Q", title="# of unique kanji", format=","
                ),
                alt.Tooltip("volume_count:Q", title="# of volumes", format=","),
            ],
        )
    )
    st.altair_chart(unique_kanji_chart, use_container_width=True)


# show a bar chart of mangas & avg chrs per volume
with col3:
    st.header("Avg characters per volume")
    avg_volume_chart = (
        alt.Chart(filtered_manga)
        .mark_bar()
        .encode(
            x=alt.X("clean_title:N", title="Manga"),
            y=alt.Y("avg_chr_per_volume:Q", title="Average characters per volume"),
            tooltip=[
                alt.Tooltip("clean_title:N", title="Manga"),
                alt.Tooltip(
                    "avg_chr_per_volume:Q",
                    title="Average characters per volume",
                    format=",.0f",
                ),
                alt.Tooltip("volume_count:Q", title="# of volumes", format=","),
            ],
        )
    )
    st.altair_chart(avg_volume_chart, use_container_width=True)


# show a bar chart of mangas & avg chrs per page
with col4:
    st.header("Avg characters per page")
    avg_page_chart = (
        alt.Chart(filtered_manga)
        .mark_bar()
        .encode(
            x=alt.X("clean_title:N", title="Manga"),
            y=alt.Y("avg_chr_per_page:Q", title="Average characters per page"),
            tooltip=[
                alt.Tooltip("clean_title:N", title="Manga"),
                alt.Tooltip(
                    "avg_chr_per_page:Q",
                    title="Average characters per page",
                    format=",.0f",
                ),
                alt.Tooltip("volume_count:Q", title="# of volumes", format=","),
            ],
        )
    )
    st.altair_chart(avg_page_chart, use_container_width=True)


# Show a scatter plot of num of chars & num of unique kanji
scatter = (
    alt.Chart(filtered_manga)
    .mark_point(size=100)
    .encode(
        x=alt.X("num_of_chrs:Q", title="# of characters"),
        y=alt.Y("num_of_unique_chrs:Q", title="# of unique kanji"),
        tooltip=[
            alt.Tooltip("num_of_chrs:Q", title="# of characters", format=","),
            alt.Tooltip("volume_count:Q", title="# of volumes", format=","),
            alt.Tooltip("num_of_unique_chrs:Q", title="# of unique kanji", format=","),
            alt.Tooltip("clean_title:N", title="Manga"),
        ],
    )
)

# Create the text labels that will appear below the dots
text = (
    alt.Chart(filtered_manga)
    .mark_text(align="center", baseline="top", dy=7, color="white")
    .encode(
        x=alt.X("num_of_chrs:Q"),
        y=alt.Y("num_of_unique_chrs:Q"),
        text=alt.Text("clean_title:N"),
        tooltip=alt.value(None),
    )
)

# Combine both layers into one chart
chart = scatter + text

# Display the combined chart in Streamlit
st.markdown("---")
st.header("Number of Characters vs. Unique Kanji")
st.altair_chart(chart, use_container_width=True)
