import streamlit as st
import pandas as pd
from home_view import home_view
from manga_view import manga_view
from general_view import general_view

st.set_page_config(
    layout="wide", page_title="MangaDB - jpdb but for manga", page_icon="📖"
)

# Big title
st.title("MangaDB - Stats on your favorite manga")
manga_dim = pd.read_csv("data/dim_manga.csv")
titles = manga_dim["clean_title"].unique().tolist()
st.sidebar.metric("Number of titles in the dataset", len(titles))

pg = st.navigation(
    [
        st.Page(general_view, title="General"),
        st.Page(home_view, title="Manga -- stats on manga"),
        st.Page(manga_view, title="Volume -- stats per volume"),
    ]
)
pg.run()
