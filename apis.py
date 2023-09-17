from requests import post, get
import os
import pandas as pd
import json
import base64
import math
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_playlist(token, playlist_id):
    results = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    if result.status_code != 200:
        print(f'{playlist_id} error') 
    json_result = json.loads(result.content)['tracks']
    results.append(json_result)
    
    total = json_result['total']
    calls = math.ceil(total/100.0) - 1
    for x in range(calls):
        url = json_result['next']
        result = get(url, headers = headers)
        if result.status_code != 200:
            print(f'{playlist_id} error') 
        results.append(json.loads(result.content))
    return(results)

def get_track_ids(playlist):
    ids = []
    for track in playlist['items']:
        if track['track'] is not None:
            id = track['track']['id']
        ids.append(id)
    return ids
    
def get_audio_features(token, track_id):
    url = f'https://api.spotify.com/v1/audio-features/{track_id}'
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    if result is None:
            print(f'{track_id} error') 
    json_result = json.loads(result.content)
    return json_result

def get_song_info(token, track_id):
    url = f'https://api.spotify.com/v1/audio-features/{track_id}'
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    if result is None:
            print(f'{track_id} error') 
    json_result = json.loads(result.content)
    return json_result

def get_audio_features_df(playlist_id):
    token = get_token()
    playlist = get_playlist(token, playlist_id)
    ids = get_track_ids(playlist[0])
    features = []
    for track in ids:
        info = get_audio_features(token, track)
        features.append(info)
        
    # create dataframe
    duration = []
    danceability = []
    energy = []
    loudness = []
    speechiness = []
    acousticness = []
    instrumentalness = []
    liveness = []
    valence = []
    tempo = []
    uri = []

    for song in features:
        try: 
            duration.append(song['duration_ms'])
            danceability.append(song['danceability'])
            energy.append(song['energy'])
            loudness.append(song['loudness'])
            speechiness.append(song['speechiness'])
            acousticness.append(song['acousticness'])
            instrumentalness.append(song['instrumentalness'])
            liveness.append(song['liveness'])
            valence.append(song['valence'])
            tempo.append(song['tempo'])
            uri.append(song['uri'])
        except:
            duration.append(None)
            danceability.append(None)
            energy.append(None)
            loudness.append(None)
            speechiness.append(None)
            acousticness.append(None)
            instrumentalness.append(None)
            liveness.append(None)
            valence.append(None)
            tempo.append(None)
            uri.append(None)
    dictionary = {'duration_ms': duration, 'danceability': danceability, 'energy': energy, 'loudness': loudness,
              'speechiness': speechiness, 'acousticness': acousticness, 'instrumentalness': instrumentalness, 
              'liveness': liveness, 'valence': valence, 'tempo': tempo, 'uri': uri}
    df = pd.DataFrame(dictionary)
    return df

def get_mood_distribution(model, df):
    df = df.drop(['uri'], axis=1)
    predictions = model.predict(df)
    result = [0] * 4
    for pred in predictions:
        if pred == 0:
            result[0] += 1
        elif pred == 1:
            result[1] += 1
        elif pred == 2:
            result[2] += 1
        else:
            result[3] += 1
    return result

def get_song_info_list(token, track_ids):
    all_tracks = []
    batches = [track_ids[i:i + 50] for i in range(0, len(track_ids), 50)]
    headers = get_auth_header(token)
    for batch in batches:
        params = {
            'ids': ','.join(batch)
        }
        response = get('https://api.spotify.com/v1/tracks', headers=headers, params=params)
        all_tracks.append(response.json()['tracks'])
    return all_tracks

def get_artist_and_popularity(song_info_list):
    song_names = []
    artists = []
    popularities = []
    artist_id = []
    for batch in song_info_list:
        for song in batch:
            song_names.append(song['name'])
            artists.append(song['album']['artists'][0]['name'])
            artist_id.append(song['artists'][0]['id'])
            popularities.append(song['popularity'])
    dictionary = {'song_name':song_names, 'artist':artists, 'song_popularity':popularities, 'artist_id':artist_id}
    return pd.DataFrame(dictionary)

def get_artist_info(artist_df):
    names = []
    followers = []
    genres = []
    popularities = []
    counts = []

    token = get_token()
    headers = get_auth_header(token)
    artist_ids = artist_df['artist_id'].to_list()
    
    artist_info_cache = {}
    artist_counts = artist_df['artist_id'].value_counts().to_dict()
    
    for id, count in artist_counts.items():
        if id not in artist_info_cache:
            url = f'https://api.spotify.com/v1/artists/{id}'
            response = get(url, headers=headers).json()
            artist_info_cache[id] = {
                'name': response['name'],
                'followers': response['followers']['total'],
                'genres': response['genres'],
                'popularity': response['popularity']
            }
            
            names.append(artist_info_cache[id]['name'])
            followers.append(artist_info_cache[id]['followers'])
            genres.append(artist_info_cache[id]['genres'])
            popularities.append(artist_info_cache[id]['popularity'])
            counts.append(count)
    dictionary = {'name': names, 'followers': followers, 'genres': genres, 'popularity': popularities,
                  'count': counts}
    return pd.DataFrame(dictionary)