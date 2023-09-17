from requests import post, get
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
import apis
import pickle

os.chdir('/Users/ashleyyan/Downloads/spotify-project')
# loading the model
pickle_path = "/Users/ashleyyan/Downloads/spotify-project/song_mood_classifier.pkl"
with open(pickle_path, "rb") as file:
    model = pickle.load(file)

load_dotenv() 
app = Flask(__name__, template_folder='templates', static_folder = 'static')
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/analyze_playlist', methods=['POST'])
def analyze_playlist():
    playlist_id = request.form.get('playlist_id')
    return redirect(url_for('dashboard_page', id=playlist_id))

@app.route('/get_playlist_data/<playlist_id>')
def get_playlist_data(playlist_id):
    si_value = request.args.get('si')
    playlist_id = playlist_id + '?si=' + si_value
    audio_features_df = apis.get_audio_features_df(playlist_id)
    mood_distribution = apis.get_mood_distribution(model, audio_features_df)

    playlist = apis.get_playlist(apis.get_token(), playlist_id) #intermediate
    ids = apis.get_track_ids(playlist[0]) #intermediate
    song_info_list = apis.get_song_info_list(apis.get_token(), ids) #intermediate
    artist_and_popularity_df = apis.get_artist_and_popularity(song_info_list)
    artist_info_df = apis.get_artist_info(artist_and_popularity_df)

    data = {'audio_features': audio_features_df.to_dict(orient='list'), 
            'mood_distribution': mood_distribution, 
            'artist_and_popularity': artist_and_popularity_df.to_dict(orient='list'), 
            'artist_info': artist_info_df.to_dict(orient='list')}
    return data


@app.route('/dashboard')
def dashboard_page():
    playlist_id = request.args.get('id')
    #print(playlist_id)
    '''
    audio_features_df = apis.get_audio_features_df(playlist_id)
    mood_distribution = apis.get_mood_distribution(model, audio_features_df)

    playlist = apis.get_playlist(apis.get_token(), playlist_id) #intermediate
    ids = apis.get_track_ids(playlist[0]) #intermediate
    song_info_list = apis.get_song_info_list(apis.get_token(), ids) #intermediate
    artist_and_popularity_df = apis.get_artist_and_popularity(song_info_list)
    artist_info_df = apis.get_artist_info(artist_and_popularity_df)
    '''
    return render_template('dashboard.html', id=playlist_id)

if __name__ == '__main__':
    app.run(debug=True)
