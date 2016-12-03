from flask import render_template, Flask, redirect, request
import json
import base64
import spotify
import urllib
import requests

app = Flask(__name__)

#  Client Keys
CLIENT_ID = "fcc4d01a6c754883bdb67d47659894aa"
CLIENT_SECRET = "e766e969056f404c98a7376fd95c8ff3"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route('/')
def homepage():
    url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)
    #html = render_template('homepage.html')
    #return html

@app.route("/callback/q")
def callback():
    print 'call callback function'
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)
    print profile_data

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get('https://api.spotify.com/v1/users/zhch6639/playlists', headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)
    print playlists_response.json()
    
    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return render_template("homepage.html",sorted_array=display_arr)

@app.route('/search/<name>')
def search(name):
    data = spotify.search_by_artist_name(name)
    api_url = data['artists']['href']
    items = data['artists']['items']
    html = render_template('search.html',
                            artist_name=name,
                            results=items,
                            api_url=api_url)
    return html




@app.route('/artist/<id>')
def artist(id):
    artist = spotify.get_artist(id)
    playlists = spotify.get_user_playlists('zhch6639')

    if artist['images']:
        image_url = artist['images'][0]['url']
    else:
        image_url = 'http://placecage.com/600/400'

    tracksdata = spotify.get_artist_top_tracks(id)
    tracks = tracksdata['tracks']

    artistsdata = spotify.get_related_artists(id)
    relartists = artistsdata['artists']
    html = render_template('artist.html',
                            artist=artist,
                            related_artists=relartists,
                            image_url=image_url,
                            tracks=tracks)
    return html



if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)


