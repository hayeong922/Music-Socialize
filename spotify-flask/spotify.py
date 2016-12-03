import requests

GET_ARTIST_ENDPOINT = 'https://api.spotify.com/v1/artists/{id}'
SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search'
RELATED_ARTISTS_ENDPOINT = 'https://api.spotify.com/v1/artists/{id}/related-artists'
TOP_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/artists/{id}/top-tracks'
GET_USER_PLAYLISTS = 'https://api.spotify.com/v1/users/{id}/playlists'
GET_PLAYLISTS = 'https://api.spotify.com/v1/users/{user_id}/playlists/{playlist_id}'

# https://developer.spotify.com/web-api/get-artist/
def get_artist(artist_id):
    url = GET_ARTIST_ENDPOINT.format(id=artist_id)
    resp = requests.get(url)
    print 'get artist'
    return resp.json()


# https://developer.spotify.com/web-api/search-item/
def search_by_artist_name(name):
    myparams = {'type': 'artist'}
    myparams['q'] = name
    resp = requests.get(SEARCH_ENDPOINT, params=myparams)
    return resp.json()


# https://developer.spotify.com/web-api/get-related-artists/
def get_related_artists(artist_id):
    url = RELATED_ARTISTS_ENDPOINT.format(id=artist_id)
    resp = requests.get(url)
    return resp.json()

# https://developer.spotify.com/web-api/get-artists-top-tracks/
def get_artist_top_tracks(artist_id, country='US'):
    url = TOP_TRACKS_ENDPOINT.format(id=artist_id)
    myparams = {'country': country}
    resp = requests.get(url, params=myparams)
    return resp.json()

def get_user_playlists(user_id):
    url = GET_USER_PLAYLISTS.format(id=user_id)
    resp=requests.get(url)
    print 'get playlists'
    print resp.json()
    return resp.json()

