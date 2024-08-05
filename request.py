import requests
import json

# u, t, s, f, v, c
stream_url_parameter = ['Guest', '2dc98a10999257c14a0920f57d129b02', '318fe6', 'json', '1.8.0', 'NavidromeUI']


def request_album_data(id: str):
    url = "https://www.squidify.org/api/song/?_sort=album&_start=0&_end=0&album_id=" + id
    response = requests.get(url)
    return json.loads(response.content)


def request_song_data(id: str):
    if id.rfind(" ") != -1:
        return None
    url = "https://www.squidify.org/api/song/" + id
    response = requests.get(url)
    return json.loads(response.content)


def get_url(song_id: str):
    return f"https://www.squidify.org/rest/stream?u={stream_url_parameter[0]}&t={stream_url_parameter[1]}&s={stream_url_parameter[2]}&f={stream_url_parameter[3]}&v={stream_url_parameter[4]}&c={stream_url_parameter[5]}&id={song_id}"


def search_result(arg: str, is_album: bool):
    if is_album:
        response = requests.get(f"https://www.squidify.org/api/album?_end=36&_order=ASC&_sort=name&_start=0&name={arg}")
    else:
        response = requests.get(f"https://www.squidify.org/api/song?_end=15&_order=ASC&_sort=title&_start=0&title={arg}")
    return json.loads(response.content)


async def song_dl(song_id: str):
    info = request_song_data(song_id)
    if info is None or info.get('error') is not None:
        print("Error downloading track")
        return
    url = get_url(song_id)
    response = requests.get(url)
    f = open(info.get('title') + ".flac", "wb")
    f.write(response.content)
    f.close()
