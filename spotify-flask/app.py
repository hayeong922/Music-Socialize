from flask import render_template, Flask, redirect, g, request, Response, make_response
import spotify
import requests
import base64
import urllib
import json
import spotify
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.json_util import loads
import time
import collections

app = Flask(__name__)
mongo = PyMongo(app)

#  Client Keys
CLIENT_ID = "630b86f26d9e4839a970cc2057c7f5c5"
CLIENT_SECRET = "e193ee961de84c59951786769cb35969"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://localhost"
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)

SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

# Set the USER_ID
USER_ID = None

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
    print(mongo.db.test.find_one())
    print(dumps(mongo.db.test.find({'x':10})))

    user_id = request.cookies.get('user')  
    # print(user_id)
    playlist = collections.defaultdict(list)
    for play_list in mongo.db.playlist.find().limit(6):

        # print(play_list['playlist_id'], type(play_list['playlist_information']))
        data = play_list['playlist_information']
        # data = data.replace('\'','\"')
        # data = data.replace('u\'','\'')
        jsondata = json.loads(data.decode('string-escape').strip('"'))
        print(type(jsondata))
        print(jsondata['images'][0]['url'])
        playlist['playlist_id'].append(play_list['playlist_id'])
        playlist['images'].append(jsondata['images'][0]['url'])
        # print(data['tracks'])
    # play_list = 
    # print(playlist)
    print(playlist)
    if playlist:
        playlist = json.dumps(playlist)
        print(type(playlist))
        html = render_template('homepage.html', playlist=playlist)
    else:
        html = render_template('homepage.html')
    return html

@app.route('/login')
def login():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/callback")
def callback():
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
    #print(authorization_header)
    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)

    profile_data = json.loads(profile_response.text)
    #print(profile_data)
    user_id = profile_data["id"]
    # if USER_ID is None:
    #     USER_ID = user_id
    #     print("User ID", USER_ID)
    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    #playlist_data = json.loads(playlists_response.text)
    playlist_data=playlists_response.json()
    # print(playlist_data)

    # print 'try to get playlist'
    #print(playlist_data)

    #print 'try to get playlist'
    playlist_item=playlist_data[u'items']
    playlist_ids=[]
    
    for item in playlist_item:
        # print item
        playlist_ids.append(item[u'external_urls'][u'spotify'].split('/')[-1])
        #print item

    playlist_track=[]
    playlist_file=open('playlist_file', 'w')
    playlist_file.write(user_id)
    playlist_file.write('\n')
    for playlist_id in playlist_ids:
        playlist_file.write(playlist_id+'\n')
        playlist=requests.get('https://api.spotify.com/v1/users/{id}/playlists/{id2}'.format(id=user_id, id2=playlist_id), headers=authorization_header)
        playlist_file.write(str(playlist.json())+'\n')
        mongo.db.playlist.insert({'user_id':user_id,'playlist_id':playlist_id,'playlist_information':json.dumps(playlist.text)})
        #playlist_track.append(track_response.json())
    #print playlist_track
    #playlist_ite=playlist_data[u'items'][0][u'external_urls'][u'spotify']
    
    #playlists=spotify.get_user_playlists(playlist_api_endpoint, authorization_header)
    #print playlists
    #print mongo.db.test.find({playlist_id})
    # cur = mongo.db.test.find({}, {"playlist_information": 1, "_id": 0})

    # for doc in cur:
    #     print ''
    #     p2 = json.loads(str(doc[u'playlist_information']))
    #     print type(p2)
    #     print p2

    #mongo.db.student.find({}, {playlist_id: 1, _id: 0}).pretty();



    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    playlist = collections.defaultdict(list)
    for play_list in mongo.db.playlist.find().limit(6):

        print(play_list['playlist_id'], type(play_list['playlist_information']))
        data = play_list['playlist_information']
        # data = data.replace('\'','\"')
        # data = data.replace('u\'','\'')
        jsondata = json.loads(data.decode('string-escape').strip('"'))
        print(type(jsondata))
        print(jsondata['images'][0]['url'])
        playlist['playlist_id'].append(play_list['playlist_id'])
        playlist['images'].append(jsondata['images'][0]['url'])
    # res = Response("You have log in<a href='/'>Home page</a>")
    playlist = json.dumps(playlist)
    res = make_response(render_template("homepage.html",sorted_array=display_arr, user_id=user_id, playlist=playlist))
    res.set_cookie(key='user', value=user_id, expires=time.time()+6*60000)
    return res
    # return render_template("homepage.html",sorted_array=display_arr, user_id=user_id)

@app.route('/search/<name>')
def search(name):
    user_id = request.cookies.get('user')  
    data = spotify.search_by_artist_name(name)
    api_url = data['artists']['href']
    items = data['artists']['items']
    html = render_template('search.html',
                            artist_name=name,
                            results=items,
                            api_url=api_url,
                            user_id=user_id)
    return html


@app.route('/artist/<id>')
def artist(id):
    user_id = request.cookies.get('user')  
    artist = spotify.get_artist(id)

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
                            tracks=tracks,
                            user_id=user_id)
    return html




@app.route('/playlist/<playlist_id>')
def playlist(playlist_id):
    # print("USER_ID",user_id)

    user_id = request.cookies.get('user')  
    # playlists = spotify.get_user_playlists(user_id)
    print("This page user_id",user_id)
    # if artist['images']:
    #     image_url = artist['images'][0]['url']
    # else:
    #     image_url = 'http://placecage.com/600/400'

    # tracksdata = spotify.get_artist_top_tracks(id)
    # tracks = tracksdata['tracks']

    # artistsdata = spotify.get_related_artists(id)
    # relartists = artistsdata['artists']
    playlist = collections.defaultdict(list)
    print(playlist_id)
    the_play_list = mongo.db.playlist.find_one({'playlist_id': playlist_id})
    # print(the_play_list)
    data = the_play_list['playlist_information']
    jsondata = json.loads(data.decode('string-escape').strip('"'))
    print("img: ",jsondata['images'][0]['url'])
    img_url = jsondata['images'][0]['url']
    # res = Response("You have log in<a href='/'>Home page</a>")
    # print(jsondata)
    playlist_name = jsondata['name']
    tracks = jsondata['tracks']['items']
    url = jsondata['external_urls']['spotify']
    print(tracks)
    for t in tracks:
        print(t)
    # print(type(tracks))
    html = render_template('playlist.html',
                            img_url=img_url,
                            playlist_name=playlist_name,
                            tracks=tracks,
                            url=url,
                            user_id=user_id)
    return html



if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, port=PORT)


