import datetime

import vlc
import asyncio
import request as rq

instance = vlc.Instance()
player = instance.media_list_player_new()
player.get_media_player().audio_set_track(1)
player.get_media_player().audio_set_volume(50)
instance.log_unset()
medialist = instance.media_list_new()
medialist.retain()
player.set_media_list(medialist)


global t_duration, t_id, t_album, t_title

mediaplaylist = []
current = -1

current_prompt = ""


def player_free():
    state = player.get_state()
    return state in (vlc.State.Stopped, vlc.State.NothingSpecial, vlc.State.Ended, vlc.State.Error)


def set_play():
    track = mediaplaylist[current]
    global t_duration, t_id, t_album, t_title
    t_id = track.get('id')
    t_album = track.get('album')
    t_title = track.get('title')
    # media = instance.media_new(rq.get_url(t_id))
    # player.set_media(media)
    t_duration = str(datetime.timedelta(seconds=track.get('duration')))[:-7]


async def play():
    player.play()


def song_ended(self, event):
    print('smth')


def media_list_ended(self, event):
    print("Playlist ended.")


def next_item_set(self, event):
    global current
    current += 1
    set_play()
    print(f"Now playing: \n Album: {t_album}\n Title: {t_title}\n Duration: {t_duration}")
    print(current_prompt)


# checks if the player is playing and then clears the playlist
def check_player():
    global medialist, current
    if player.get_state() == vlc.State.Ended or player.get_state() == vlc.State.Stopped:
        mediaplaylist.clear()
        medialist = instance.media_list_new()
        current = -1


async def play_album(album):
    check_player()
    for track in album:
        medialist.add_media(rq.get_url(track.get('id')))
        mediaplaylist.append(track)
    if player_free():
        player.next()
        await play()
    else:
        print("Queued: " + album[0].get('album'))


async def play_track(track):
    check_player()

    medialist.add_media(rq.get_url(track.get('id')))
    mediaplaylist.append(track)
    if player.is_playing():
        print("Queued: " + track.get('title'))
    else:
        player.next()
        await play()


async def show_album_tracks(album):
    for i, song in enumerate(album, start=1):
        duration = str(datetime.timedelta(seconds=song.get('duration')))[:-7]
        print(f"{i} - {song.get('title')} | {duration}")


def stop():
    player.stop()
    global medialist
    medialist = instance.media_list_new()
    player.set_media_list(medialist)
    mediaplaylist.clear()


def show_list():
    print("Current playlist:")
    for i in range(0, len(mediaplaylist)):
        track = mediaplaylist[i]
        msg = f"{i} : {track.get('title')}"
        if current == i:
            msg = msg + " - Playing"
        print(msg)


async def search():
    global current_prompt

    current_prompt = "What do you want to search?\n1: Album\n2: Song\n0: Exit\nSelection: "
    is_album = False

    while True:
        search_type = input("What do you want to search?\n1: Album\n2: Song\n0: Exit\nSelection: ")

        match search_type:
            case '0':
                return
            case '1':
                is_album = True
                break
            case '2':
                is_album = False
                break
            case _:
                continue

    current_prompt = "Search: "
    print("Type 'exit' to exit.")
    value = input("Search: ")

    if value == "exit":
        return

    result = rq.search_result(value, is_album)

    if result is None:
        print("No results found.")
        return

    for index, item in enumerate(result, start=1):
        if is_album:
            content = item.get("name") + ", by " + item.get("albumArtist") + ", " + str(item.get("songCount")) + " tracks, released in " + item.get("date")
        else:
            content = item.get("title") + ", from " + item.get("album") + ", by " + item.get("artist") + ", released in " + item.get("date")
        print(f"{index} - {content}")

    current_prompt = "Select result: "
    while True:
        print("Type '0' to return to search, 'q' to return to main program.")
        value = input("Select result: ")

        if value == "0":
            await search()
            break
        if value == "q":
            break

        try:
            selected = int(value) - 1
        except ValueError:
            continue

        if selected < 0 or selected + 1 >= len(result):
            continue

        current_prompt = "Select option: "
        if not is_album:
            track_id = result[selected].get("id")
            print("Options:\n1: Play\n2: Download\n0: Exit")
            while True:
                value = input("Select option: ")

                match value:
                    case "0":
                        return
                    case "1":
                        await play_track(rq.request_song_data(track_id))
                        break
                    case "2":
                        await rq.song_dl(track_id)
                        break
                    case _:
                        continue
        else:
            album = rq.request_album_data(result[selected].get("id"))
            while True:
                print("Options:\n1: Play\n2: Show Tracks\n0: Exit")
                value = input("Select option: ")
                match value:
                    case "0":
                        return
                    case "1":
                        await play_album(album)
                        break
                    case "2":
                        await show_album_tracks(album)
                    case _:
                        continue

        break

    return


async def main():
    global medialist, current, current_prompt
    event_manager = player.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, song_ended, 1)
    event_manager.event_attach(vlc.EventType.MediaListEndReached, media_list_ended, 1)
    event_manager.event_attach(vlc.EventType.MediaListPlayerNextItemSet, next_item_set, 1)
    close = False
    print("Enter 'q' to quit.")
    print("Enter 'p' to pause/resume and 'volume' to change volume.")
    print("Enter 'stop' to stop and clear playlist.")
    print("Enter 'next' and 'prev' to control player.")
    print("Enter 'list' to view the current playlist.")
    print("Enter 'search' to search.")
    # Test types using id: a - album, t - track, get - get album tracks, dl - download track
    while close is False:

        current_prompt = "Enter action type: "
        request_type = input("Enter action type: ")

        match request_type:

            case 'a':
                request_id = input("Enter album id: ")
            case 't':
                request_id = input("Enter track id: ")
            case 'get':
                request_id = input('Album id: ')
            case 'p':
                if player.get_state() == vlc.State.Paused:
                    print("Resuming")
                else:
                    print("Pausing")
                player.pause()
                continue
            case 'stop':
                stop()
                continue
            case 'next':
                player.next()
                continue
            case 'prev':
                global current
                current -= 2
                player.previous()
                continue
            case 'status':
                if player.get_state() == vlc.State.Playing:
                    print(f"Now playing: \n Album: {t_album}\n Title: {t_title}\n Volume: {player.get_media_player().audio_get_volume()}\n Current: {str(datetime.timedelta(seconds=player.get_media_player().get_time() / 1000))[:-7]}\n Duration: {t_duration}\n Index: {current}")
                else:
                    print("Nothing is playing.")
                continue
            case 'list':
                show_list()
                continue
            case 'dl':
                request_id = input("Enter track id to download: ")
                await asyncio.create_task(rq.song_dl(request_id))
                continue
            case 'volume':
                vol = int(input('Enter volume: '))
                player.get_media_player().audio_set_volume(vol)
                continue
            case 'search':
                await search()
                continue
            case 'q':
                break
            case _:
                print('Invalid id type.')
                continue

        if request_type == 'get':
            album = rq.request_album_data(request_id)

            if album is None:
                print('Album not found.')
                continue

            await show_album_tracks(album)

        if request_type == 'a':
            album = rq.request_album_data(request_id)

            if album is None:
                print('Album not found.')
                continue

            if album[0] is None:
                print('Album not found.')
                continue

            if album[0].get('error') is not None:
                print('Album not found.')
                continue

            await play_album(album)

        if request_type == 't':
            track = rq.request_song_data(request_id)

            if track is None:
                print('Track not found.')
                continue

            if track.get('error') is not None:
                print('Track not found.')
                continue

            await play_track(track)

    player.stop()

asyncio.run(main())
