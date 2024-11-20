import requests
import json
import os

from dotenv import load_dotenv

load_dotenv()

# u, t, s, f, v, c
stream_url_parameter = [os.getenv('u'), os.getenv('t'), os.getenv('s'), 'json', '1.8.0', 'NavidromeUI']

path = "lib/"


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
        response = requests.get(f"https://www.squidify.org/api/album?_end=72&_order=ASC&_sort=name&_start=0&name={arg}")
    else:
        response = requests.get(
            f"https://www.squidify.org/api/song?_end=72&_order=ASC&_sort=title&_start=0&title={arg}")
    return json.loads(response.content)


def check_title(title: str):
    if title.__contains__("/"):
        title = title.replace("/", "-")
    return title

# Checks if the song is already downloaded
def check_dl(title: str, album: str):
    title = check_title(title)
    final_path = path + album + "/" + title + ".flac"
    if os.path.exists(final_path):
        return final_path
    return None

def album_dl(album):
    for track in album:
        song_dl(track.get("id"), track.get("title"), album[0].get("album"))
    print("Downloaded all tracks -- " + album.get("name"))


def song_dl(song_id: str, title: str, album: str):
    url = get_url(song_id)
    response = requests.get(url)
    album = album + "/"
    if not os.path.exists(path + album):
        os.makedirs(path + album)
    full_path = path + album + check_title(title) + ".flac"
    if os.path.exists(full_path):
        print("Already downloaded -- " + title)
        return

    f = open(path + album + check_title(title) + ".flac", "wb")
    f.write(response.content)
    f.close()
    print("Downloaded -- " + title)
