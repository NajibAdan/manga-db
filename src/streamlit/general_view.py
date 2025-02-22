import streamlit as st
import pandas as pd
import altair as alt


def clean_data(df):
    df["start_year"] = df["start_year"].fillna(0)
    df["start_year"] = df["start_year"].astype(int)
    return df[df["start_year"] > 0]


def filter_data(df, years, genres):
    if genres:
        return df[
            (df["start_year"] >= years[0])
            & (df["start_year"] <= years[1])
            & (df["genres"].isin(genres))
        ]
    return df[(df["start_year"] >= years[0]) & (df["start_year"] <= years[1])]


def general_view():
    # Query the table
    st.header(
        "This page shows the average number of characters, unique number of Kanji across years & different genres."
    )
    manga_dim = pd.read_csv("data/dim_manga.csv")
    manga_details = pd.read_json("data/anilist_data.jsonl", lines=True)
    merged_data = clean_data(manga_details.merge(manga_dim, how="inner")).explode(
        "genres"
    )
    genres_df = merged_data[["title_uuid", "genres"]].explode("genres").dropna()
    years = st.sidebar.slider(
        "Year of Publication",
        merged_data["start_year"].min(),
        merged_data["start_year"].max(),
        (2000, 2024),
    )
    genres = st.sidebar.multiselect("Manga genre", genres_df["genres"].unique())
    columns = [
        "title_uuid",
        "romanji_title",
        "start_year",
        "score",
        "genres",
        "volume_count",
        "page_count",
        "num_of_unique_chrs",
        "num_of_chrs",
        "avg_chr_per_page",
        "avg_chr_per_volume",
    ]
    merged_data = merged_data[columns]
    merged_data = filter_data(merged_data, years, genres)
    chr_columns = [
        "title_uuid",
        "score",
        "romanji_title",
        "start_year",
        "num_of_unique_chrs",
        "num_of_chrs",
        "avg_chr_per_page",
        "avg_chr_per_volume",
    ]
    grp_year = (
        merged_data[chr_columns]
        .drop_duplicates()
        .groupby("start_year")
        .agg(
            {
                "avg_chr_per_volume": "mean",
                "avg_chr_per_page": "mean",
                "score": "mean",
                "num_of_unique_chrs": "mean",
                "title_uuid": "nunique",
            }
        )
        .reset_index()
    )
    col1, col2 = st.columns(2, vertical_alignment="bottom", border=True)
    col3, col4 = st.columns(2, vertical_alignment="bottom", border=True)
    with col1:
        st.markdown("#### Average characters per volume across the years")
        avg_page_chart = (
            alt.Chart(grp_year)
            .mark_bar()
            .encode(
                y=alt.Y("avg_chr_per_volume:Q", title="Average characters per volume"),
                x=alt.X("start_year:N", title="Publication Year"),
                tooltip=[
                    alt.Tooltip(
                        "title_uuid:Q",
                        title="Number of mangas",
                        format=",.0f",
                    ),
                    alt.Tooltip(
                        "avg_chr_per_volume:Q",
                        title="Average characters per volume",
                        format=",.0f",
                        bin=alt.Bin(maxbins=75),
                    ),
                ],
            )
        )
        st.altair_chart(avg_page_chart, use_container_width=True)
    with col2:
        st.markdown("#### Average number of unique Kanji across the years")
        avg_page_chart = (
            alt.Chart(grp_year)
            .mark_bar()
            .encode(
                y=alt.Y("num_of_unique_chrs:Q", title="Average number of unique kanji"),
                x=alt.X("start_year:N", title="Publication Year"),
                tooltip=[
                    alt.Tooltip(
                        "title_uuid:Q",
                        title="Number of mangas",
                        format=",.0f",
                    ),
                    alt.Tooltip(
                        "num_of_unique_chrs:Q",
                        title="Number of unique characters",
                        format=",.0f",
                        bin=alt.Bin(maxbins=75),
                    ),
                ],
            )
        )
        st.altair_chart(avg_page_chart, use_container_width=True)
    genres_columns = [
        "title_uuid",
        "genres",
        "score",
        "romanji_title",
        "start_year",
        "num_of_unique_chrs",
        "num_of_chrs",
        "avg_chr_per_page",
        "avg_chr_per_volume",
    ]
    grp_genres = (
        merged_data[genres_columns]
        .drop_duplicates()
        .groupby("genres")
        .agg(
            {
                "avg_chr_per_volume": "mean",
                "avg_chr_per_page": "mean",
                "score": "mean",
                "num_of_unique_chrs": "mean",
                "title_uuid": "nunique",
            }
        )
        .reset_index()
    )
    with col3:
        st.markdown("#### Average characters per volume across genres")
        avg_page_chart = (
            alt.Chart(grp_genres)
            .mark_bar()
            .encode(
                x=alt.X("avg_chr_per_volume:Q", title="Average characters per volume"),
                y=alt.Y("genres:N", title="Genre"),
                tooltip=[
                    alt.Tooltip(
                        "title_uuid:Q",
                        title="Number of mangas",
                        format=",.0f",
                    ),
                    alt.Tooltip(
                        "avg_chr_per_volume:Q",
                        title="Average characters per volume",
                        format=",.0f",
                        bin=alt.Bin(maxbins=75),
                    ),
                ],
            )
        )
        st.altair_chart(avg_page_chart, use_container_width=True)
    with col4:
        st.markdown("#### Average number of unique Kanji across across genres")
        avg_page_chart = (
            alt.Chart(grp_genres)
            .mark_bar()
            .encode(
                x=alt.X("num_of_unique_chrs:Q", title="Average number of unique Kanji"),
                y=alt.Y("genres:N", title="Genre"),
                tooltip=[
                    alt.Tooltip(
                        "title_uuid:Q",
                        title="Number of mangas",
                        format=",.0f",
                    ),
                    alt.Tooltip(
                        "num_of_unique_chrs:Q",
                        title="Number of unique characters",
                        format=",.0f",
                        bin=alt.Bin(maxbins=75),
                    ),
                ],
            )
        )
        st.altair_chart(avg_page_chart, use_container_width=True)
