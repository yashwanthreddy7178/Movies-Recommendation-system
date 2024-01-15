from flask import Flask, render_template, request
import pickle
import requests

app = Flask(__name__)
watched_indices = set()  # Initialize watched indices set
watched_titles = set()  # Initialize watched titles set

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# Update the recommend function
def recommend(movie, exclude_indices=None, exclude_titles=None):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    watched_indices_set = set(exclude_indices)
    watched_titles_set = set(exclude_titles)
    recommended_movie_names = []
    recommended_movie_posters = []
    i = 0  # Counter for recommended movies
    j = 0  # Counter for distances

    # Skip the selected movie
    while movies.iloc[distances[j][0]].title == movie:
        j += 1

    while i < 5:
        movie_id = movies.iloc[distances[j][0]].movie_id
        current_movie_title = movies.iloc[distances[j][0]].title
        if j not in watched_indices_set and current_movie_title not in watched_titles_set:
            recommended_movie_names.append(current_movie_title)
            recommended_movie_posters.append(fetch_poster(movie_id))
            i += 1
        j += 1

    #print(f"Input Movie: {movie}")
    #print(f"Exclude Indices: {exclude_indices}")
    #print(f"Exclude Titles: {exclude_titles}")
    #print(f"Recommendation - Movie Names: {recommended_movie_names}")
    #print(f"Recommendation - Movie Posters: {recommended_movie_posters}")

    return recommended_movie_names, recommended_movie_posters


@app.route('/', methods=['GET', 'POST'])
def movie_recommender():
    global watched_indices, watched_titles, recommended_movie_names  # Keep track of watched movie indices, titles, and recommended names

    if request.method == 'POST':
        selected_movie = request.form['selected_movie']

        # Update the Flask app code
        if 'watched_button' in request.form:
            watched_index = int(request.form['watched_button'])
            watched_movie = recommended_movie_names[watched_index]
            print(f"Watched Movie: {watched_movie}")
            watched_indices.add(watched_index)
            watched_titles.add(watched_movie)

        # Remove watched movies from recommendations
        exclude_indices = list(watched_indices)[-5:]
        exclude_titles = list(watched_titles)
        #print(f"Excluding indices: {exclude_indices}")
        #print(f"Excluding titles: {exclude_titles}")
        new_recommendation = recommend(selected_movie, exclude_indices=exclude_indices, exclude_titles=exclude_titles)
        recommended_movie_names = new_recommendation[0]
        recommended_movie_posters = new_recommendation[1]
        #print(f"Recommended Movie Names: {recommended_movie_names}")
        #print(f"Recommended Movie Posters: {recommended_movie_posters}")

    else:
        selected_movie = None
        recommended_movie_names, recommended_movie_posters = [], []

    return render_template('index.html', movie_list=movie_list, selected_movie=selected_movie,
                           recommended_movie_names=recommended_movie_names, recommended_movie_posters=recommended_movie_posters,
                           watched_indices=watched_indices)

if __name__ == '__main__':
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
    movie_list = movies['title'].values
    app.run(debug=True)