from flask import Flask, request

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Load the datasets
titles_df = pd.read_csv('CleanTitles.csv')
credits_df = pd.read_csv('credits.csv')

# Merge the datasets based on title ID
merged_df = pd.merge(titles_df, credits_df, on='id')

# Preprocess the data
features = ['release_year', 'imdb_score', 'runtime']
merged_df['combined_features'] = merged_df[features].astype(str).apply(lambda x: ' '.join(x), axis=1)

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(merged_df['combined_features'])

# Fit the KNN model
knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
knn_model.fit(tfidf_matrix)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        release_year = request.form['release_year']
        imdb_score = request.form['imdb_score']
        runtime = request.form['runtime']

        # User input
        user_input = {
            'release_year': [release_year],
            'imdb_score': [imdb_score],
            'runtime': [runtime]
        }
        user_data = ' '.join([str(value) for value in user_input.values()])
        user_tfidf = vectorizer.transform([user_data])

        # Find nearest neighbors
        distances, indices = knn_model.kneighbors(user_tfidf, n_neighbors=1)

        recommendations = merged_df.iloc[indices[0]][['title', 'imdb_score', 'type', 'description']]

        if recommendations.empty:
            return "There are no recommendations."
        else:
            output = ""
            for _, row in recommendations.iterrows():
                output += "Title: " + row['title'] + "<br>"
                output += "IMDb Score: " + str(row['imdb_score']) + "<br>"
                output += "Type: " + row['type'] + "<br>"
                output += "Description: " + row['description'] + "<br><br>"
            return output
    else:
        return '''
        <form method="POST">
            <label for="release_year">Release Year:</label>
            <input type="text" id="release_year" name="release_year"><br><br>

            <label for="imdb_score">imdb_score:</label>
            <input type="text" id="imdb_score" name="imdb_score"><br><br>

            <label for="runtime">Runtime:</label>
            <input type="text" id="runtime" name="runtime"><br><br>

            <input type="submit" value="Submit">
        </form>
        '''


if __name__ == '__main__':
    app.run(debug=True)
