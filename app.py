import streamlit as st
import pickle
import pandas as pd
import requests

# -----------------------------------
# SETTINGS
# -----------------------------------
st.set_page_config(
    page_title="MovieHub",
    page_icon="🎬",
    layout="wide"
)

API_KEY = "33bce12a1ee71e77b020e2a6f91990a4"

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# -----------------------------------
# LOAD DATA
# -----------------------------------
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

movies = pd.DataFrame(movies_dict)

# -----------------------------------
# TMDB FETCH
# -----------------------------------
def fetch_movie_data(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    data = requests.get(url).json()

    poster = None

    if data.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500/" + data["poster_path"]

    return {
        "poster": poster,
        "rating": data.get("vote_average", "N/A"),
        "year": str(data.get("release_date", ""))[:4],
        "overview": data.get("overview", "")
    }

# -----------------------------------
# RECOMMEND
# -----------------------------------
def recommend(movie, count):

    movie_index = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:count+1]

    results = []

    for i in movie_list:

        movie_id = movies.iloc[i[0]].movie_id

        title = movies.iloc[i[0]].title

        info = fetch_movie_data(movie_id)

        results.append({
            "title": title,
            "movie_id": movie_id,
            "poster": info["poster"],
            "rating": info["rating"],
            "year": info["year"],
            "overview": info["overview"]
        })

    return results

# -----------------------------------
# CSS
# -----------------------------------
st.markdown("""
<style>

.stApp{
    background: linear-gradient(#070707,#111111);
    color:white;
}

h1{
    text-align:center;
    color:#e50914;
}

.movie-card{
    background:rgba(255,255,255,0.05);
    border-radius:16px;
    padding:10px;
    text-align:center;
}

.hero{
    background:rgba(255,255,255,0.05);
    border-radius:16px;
    padding:25px;
    text-align:center;
    margin-bottom:20px;
}

img{
    border-radius:14px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------
with st.sidebar:

    st.title("🎛 Controls")

    count = st.slider(
        "Recommendations",
        5,
        10,
        5
    )

    st.subheader("⭐ Watchlist")

    if st.session_state.watchlist:

        for item in st.session_state.watchlist:
            st.write("🎬", item)

    else:
        st.write("No movies added yet")

# -----------------------------------
# TITLE
# -----------------------------------
st.markdown("<h1>🎬 MovieHub</h1>", unsafe_allow_html=True)

selected_movie = st.selectbox(
    "🔍 Search a movie",
    movies["title"].values
)

# -----------------------------------
# HERO
# -----------------------------------
selected_id = movies[movies["title"] == selected_movie].iloc[0].movie_id

selected_info = fetch_movie_data(selected_id)

if selected_info["poster"]:
    st.image(selected_info["poster"], use_container_width=True)

st.markdown(
    f"""
    <div class="hero">
        <h2>{selected_movie}</h2>
        <p>{selected_info["overview"][:200]}</p>
        <p>⭐ {selected_info["rating"]} | 📅 {selected_info["year"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# BUTTONS
# -----------------------------------
col1, col2 = st.columns(2)

with col1:
    recommend_btn = st.button("🍿 Recommend")

with col2:
    if st.button("⭐ Add to Watchlist"):

        if selected_movie not in st.session_state.watchlist:
            st.session_state.watchlist.append(selected_movie)

# -----------------------------------
# RECOMMEND
# -----------------------------------
if recommend_btn:

    with st.spinner("Finding recommendations..."):

        recommendations = recommend(
            selected_movie,
            count
        )

    st.success("Top picks for you!")

    cols = st.columns(count)

    for i in range(count):

        movie = recommendations[i]

        with cols[i]:

            if movie["poster"]:
                st.image(movie["poster"])

            st.markdown(
                f"""
                <div class="movie-card">
                    <b>{movie["title"]}</b><br><br>
                    ⭐ {movie["rating"]}<br>
                    📅 {movie["year"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander("Details"):
                st.write(movie["overview"])

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown("""
<hr>
<p style='text-align:center;color:gray;'>
Powered by TMDB 🎥
</p>
""", unsafe_allow_html=True)