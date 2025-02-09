import streamlit as st
import pandas as pd
import altair as alt


def home_view():
    # Query the table
    manga_dim = pd.read_csv("data/dim_manga.csv")

    titles = manga_dim["clean_title"].unique().tolist()
    # Manga selector
    selected_manga = st.multiselect(
        "# Pick a manga", titles, default=["Berserk", "Bleach", "Naruto", "Dragon Ball"]
    )

    # st.sidebar.metric("Number of titles in the dataset", len(titles))
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
            size=alt.Size("volume_count:Q", title="# of volumes"),
            tooltip=[
                alt.Tooltip("num_of_chrs:Q", title="# of characters", format=","),
                alt.Tooltip("volume_count:Q", title="# of volumes", format=","),
                alt.Tooltip(
                    "num_of_unique_chrs:Q", title="# of unique kanji", format=","
                ),
                alt.Tooltip("clean_title:N", title="Manga"),
            ],
        )
    )

    st.header("Distribution of average characters per volume in the dataset")
    avg_page_chart = (
        alt.Chart(manga_dim)
        .mark_bar()
        .encode(
            x=alt.X(
                "avg_chr_per_volume:Q",
                title="Average characters per volume",
                bin=alt.Bin(maxbins=75),
            ),
            y="count()",
            tooltip=[
                alt.Tooltip(
                    "count():Q",
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
    st.markdown(
        "This data is based on the selected mangas and doesn't show all the mangas in the dataset"
    )
    st.altair_chart(chart, use_container_width=True)
