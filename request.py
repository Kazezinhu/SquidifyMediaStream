import requests
import json

# u, t, s, f, v, c
stream_url_parameter = ['Guest', '2dc98a10999257c14a0920f57d129b02', '318fe6', 'json', '1.8.0', 'NavidromeUI']


def request_data():
    url = "https://www.squidify.org/api/song/"
    response = requests.get(url)
    f = open("data.json", "w")
    f.write(response.content.decode("utf-8"))
    f.close()
    return json.loads(response.content)


def retrieve_data():
    f = open("data.json", "r")
    data = json.loads(f.read())
    f.close()
    return data


def index_data():
    data = retrieve_data()
    songs = {}
    albums = {}
    for i in data:
        songs[i.get('id')] = i.get('title')
        albums[i.get('albumId')] = i.get('album')

    f = open("index.json", "w")
    index = json.dumps({'song': songs, 'album': albums})
    f.write(index)
    f.close()
    return json.loads(index)


def retrieve_index():
    f = open("index.json", "r")
    index = json.loads(f.read())
    f.close()
    return index


def request_album_data(id: str):
    url = "https://www.squidify.org/api/song/?_sort=album&_start=0&_end=0&album_id=" + id
    print(url)
    response = requests.get(url)
    return json.loads(response.content)


def request_song_data(id: str):
    if id.rfind(" ") != -1:
        return None
    url = "https://www.squidify.org/api/song/" + id
    print(url)
    response = requests.get(url)
    return json.loads(response.content)


def get_url(id: str):
    return f"https://www.squidify.org/rest/stream?u={stream_url_parameter[0]}&t={stream_url_parameter[1]}&s={stream_url_parameter[2]}&f={stream_url_parameter[3]}&v={stream_url_parameter[4]}&c={stream_url_parameter[5]}&id={id}"


async def song_dl(id: str):
    info = request_song_data(id)
    if info is None or info.get('error') is not None:
        return
    url = get_url(id)
    response = requests.get(url)
    f = open(info.get('title') + ".flac", "wb")
    f.write(response.content)
    f.close()
