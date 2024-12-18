import datetime

import vlc
import asyncio
import request as rq

from threading import Thread

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
current = -1  # to be set to the previous index when changing tracks
current_prompt = " "


def set_play():
    track = mediaplaylist[current]
    global t_duration, t_id, t_album, t_title
    t_id = track.get('id')
    t_album = track.get('album')
    t_title = track.get('title')
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
    if current < len(mediaplaylist):
        player.pause()
    else:
        set_play()
        print(f"\nNow playing: \n Album: {t_album}\n Title: {t_title}\n Duration: {t_duration}\n")
        if current_prompt != " ":
            print(current_prompt)


# checks if the player is playing and then clears the playlist
def check_player():
    global medialist, current
    if player.get_state() == vlc.State.Ended or player.get_state() == vlc.State.Stopped:
        mediaplaylist.clear()
        medialist = instance.media_list_new()
        medialist.retain()
        player.set_media_list(medialist)
        current = -1


async def play_album(album):
    check_player()
    for track in album:
        await queue_track(track)
    if player.is_playing() or player.get_state() == vlc.State.Paused:
        print("Queued: " + album[0].get('album'))
    else:
        player.next()
        await play()


async def play_track(track):
    check_player()
    await queue_track(track)
    mediaplaylist.append(track)
    if player.is_playing() or player.get_state() == vlc.State.Paused:
        print("Queued: " + track.get('title'))
    else:
        player.next()
        await play()

async def queue_track(track):
    path = rq.check_dl(track.get('title'), track.get('album'))

    if path is not None:
        medialist.add_media(path)
    else:
        medialist.add_media(rq.get_url(track.get('id')))
    mediaplaylist.append(track)


async def show_album_tracks(album):
    for i, song in enumerate(album, start=1):
        duration = str(datetime.timedelta(seconds=song.get('duration')))[:-7]
        print(f"{i} - {song.get('title')} | {duration}")


def stop():
    player.stop()
    global medialist
    medialist = instance.media_list_new()
    mediaplaylist.clear()


def jump():
    print("\nEnter q to exit.")
    global current_prompt, current
    current_prompt = "Enter the track index: "
    while True:
        input_string = input("Enter the track index: ")
        if input_string == 'q':
            return
        try:
            target = int(input_string)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if target < 0 or target >= len(mediaplaylist):
            print("Please enter a valid index.")
            continue
        current = target - 2
        set_play()
        current_prompt = " "
        player.play_item_at_index(target)
        return


def show_list():
    print("\nCurrent playlist:")
    for i in range(0, len(mediaplaylist)):
        track = mediaplaylist[i]
        duration = str(datetime.timedelta(seconds=track.get('duration')))[:-7]
        msg = f"{i + 1} : {track.get('title')} - {duration}"
        if current == i:
            msg = msg + " -- Playing"
        print(msg)


async def search():
    global current_prompt

    current_prompt = "What do you want to search?\n1: Album\n2: Song\n0: Exit\nSelection: "
    is_album = False

    while True:
        search_type = input("\nWhat do you want to search?\n1: Album\n2: Song\n0: Exit\nSelection: ")

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
    print("\nType 'exit' to exit.")
    value = input("Search: ")

    if value == "exit":
        return

    result = rq.search_result(value, is_album)

    if result is None:
        print("\nNo results found.")
        return

    print("")
    for index, item in enumerate(result, start=1):
        if is_album:
            content = item.get("name") + ", by " + item.get("albumArtist") + ", " + str(
                item.get("songCount")) + " tracks, released in " + item.get("date")
        else:
            content = item.get("title") + ", from " + item.get("album") + ", by " + item.get(
                "artist") + ", released in " + item.get("date")
        print(f"{index} - {content}")

    current_prompt = "Select result: "
    print("Type '0' to return to search, 'q' to return to main program.")
    while True:
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

        if selected < 0 or selected + 1 > len(result):
            continue

        current_prompt = "Select option: "
        if not is_album:
            track_id = result[selected].get("id")
            print("\nSelected track: " + result[selected].get("title"))
            print("Options:\n1: Play\n2: Download\n0: Exit")
            while True:
                value = input("Select option: ")

                match value:
                    case "0":
                        return
                    case "1":
                        current_prompt = " "
                        await play_track(rq.request_song_data(track_id))
                        break
                    case "2":
                        thread = Thread(target = rq.song_dl, args=(track_id, result[selected].get("title"), result[selected].get("album")))
                        thread.daemon = True
                        thread.start()
                        break
                    case _:
                        continue
        else:
            album = rq.request_album_data(result[selected].get("id"))
            while True:
                print("\nSelected album: " + album[0].get("album"))
                print("Options:\n1: Play\n2: Show Tracks\n3: Download\n0: Exit")
                value = input("Select option: ")
                match value:
                    case "0":
                        return
                    case "1":
                        current_prompt = " "
                        await play_album(album)
                        break
                    case "2":
                        await show_album_tracks(album)
                    case "3":
                        print("\nDownloading -- " + album[0].get("album"))
                        thread = Thread(target = rq.album_dl, args=(album, ))
                        thread.daemon = True
                        thread.start()
                        break
                    case _:
                        continue

        break

    return


def show_help():
    print("Enter 'q' to quit.")
    print("Enter 'p' to pause/resume and 'volume' to change volume.")
    print("Enter 'stop' to stop and clear playlist.")
    print("Enter 'next' and 'prev' to control player.")
    print("Enter 'jump' to jump to a track in the playlist.")
    print("Enter 'list' to view the current playlist.")
    print("Enter 'search' to search.")
    print("Enter 'help' to show this message.")
    # Test types using id: a - play album, t - play track, get - get album tracks, dl - download track


async def main():
    global medialist, current, current_prompt
    event_manager = player.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, song_ended, 1)
    event_manager.event_attach(vlc.EventType.MediaListEndReached, media_list_ended, 1)
    event_manager.event_attach(vlc.EventType.MediaListPlayerNextItemSet, next_item_set, 1)
    close = False
    show_help()
    while close is False:

        current_prompt = "Enter action type: "
        request_type = input("\nEnter action type: ")

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
                current_prompt = " "
                player.next()
                continue
            case 'prev':
                global current
                current -= 2
                current_prompt = " "
                player.previous()
                continue
            case 'jump':
                if not mediaplaylist:
                    print("The playlist is empty.")
                else:
                    jump()
                continue
            case 'status':
                if player.get_state() == vlc.State.Playing or player.get_state() == vlc.State.Paused:
                    print(
                        f"\nNow playing: \n Album: {t_album}\n Title: {t_title}\n Volume: {player.get_media_player().audio_get_volume()}\n Current: {str(datetime.timedelta(seconds=player.get_media_player().get_time() / 1000))[:-7]}\n Duration: {t_duration}\n Index: {current + 1}")
                else:
                    print("Nothing is playing.")
                continue
            case 'list':
                show_list()
                continue
            case 'dl':
                request_id = input("Enter track id to download: ")
                info = rq.request_song_data(request_id)
                if info is None or info.get('error') is not None:
                    print("Error downloading track.")
                    continue
                await asyncio.create_task(rq.song_dl(request_id, info.get('title'), info.get('album')))
                continue
            case 'volume':
                vol = int(input('Enter volume: '))
                player.get_media_player().audio_set_volume(vol)
                continue
            case 'search':
                await search()
                continue
            case 'help':
                show_help()
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
