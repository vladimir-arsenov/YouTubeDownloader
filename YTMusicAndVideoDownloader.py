import os
import sys
import urllib.request
import eyed3
import moviepy.editor
from eyed3.id3.frames import ImageFrame
from pytube import YouTube, Playlist


def get_as_video(url, path):
    video = YouTube(url, on_progress_callback=progress_func)
    print(f'Download of \"{video.title}\" is started.')
    video.streams.get_highest_resolution().download(path)
    print(f"\n\"{video.title}\" is downloaded.")


def get_as_audio(url, path):
    path += '' if path[-1] == '\\' else '\\'
    mp4_path = path + 'mp4\\'
    mp3_path = path + 'mp3\\'
    png_path = path + 'png\\'
    if not os.path.isdir(mp3_path):
        os.makedirs(mp3_path)
    if not os.path.isdir(png_path):
        os.makedirs(png_path)

    # mp4 download
    yt_video = YouTube(url, on_progress_callback=progress_func)
    yt_video_title = name(yt_video.title)
    print(f'Download of \"{yt_video_title}\" is started.')
    yt_video.streams.get_highest_resolution().download(mp4_path)

    # converting mp4 to mp3
    os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
    mp4_file_path = f"{mp4_path}{yt_video_title}.mp4"
    mp3_file_path = f"{mp3_path}{yt_video_title}.mp3"
    video = moviepy.editor.VideoFileClip(mp4_file_path)
    audio = video.audio
    audio.write_audiofile(mp3_file_path)

    # setting up mp3 file
    png_file_path = png_path + yt_video_title + '.png'
    # video.save_frame(png_file_path)
    urllib.request.urlretrieve(yt_video.thumbnail_url, png_file_path)
    audiofile = eyed3.load(mp3_file_path)
    if audiofile.tag is None:
        audiofile.initTag()
    audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(png_file_path, 'rb').read(), 'image/png')
    audiofile.tag.artist = name(yt_video.author)
    audiofile.tag.save(version=eyed3.id3.ID3_V2_3)

    print(f"\"{yt_video_title}\" is downloaded as audio.")


def get_playlist_as_video(url, path):
    playlist = Playlist(url)
    size = len(playlist.video_urls)
    failed = []
    download_attempts = 0
    print(f'Download of playlist \"{playlist.title}\" is started.')
    print(f'Tracks in playlist: {str(size)}.')
    print('===================================')
    try:
        for i, video in enumerate(playlist.videos):
            try:
                video.streams.get_highest_resolution().download(path)
                print(f'\"{name(video.title)}\" is downloaded. Progress {str(i + 1)}/{str(size)}.')
                print('-----------------------------------')
                download_attempts = i+1
            except Exception:
                failed.append(name(video.title))
    except KeyboardInterrupt:
        print('Download was interrupted.')
    print_results(download_attempts, failed)


def get_playlist_as_audio(url, path):
    path += '' if path[-1] == '\\' else '\\'
    mp4_path = path + 'mp4\\'
    mp3_path = path + 'mp3\\'
    png_path = path + 'png\\'

    playlist = Playlist(url)
    playlist_title = name(playlist.title.replace('Album - ', ''))
    size = len(playlist.video_urls)
    failed = []
    download_attempts = 0
    print(f'Download of playlist \"{playlist_title}\" is started.')
    print(f'Tracks in playlist: {str(size)}.')
    print('===================================')
    try:
        for i, yt_video in enumerate(playlist.videos):
            yt_video_author = name(yt_video.author)
            yt_video_title = name(yt_video.title)
            mp4_file_path = f'{mp4_path}{yt_video_author}\\{yt_video_title}.mp4'
            mp3_file_path = f'{mp3_path}{yt_video_author}\\{yt_video_title}.mp3'
            png_file_path = f'{png_path}{yt_video_author}\\{yt_video_title}.png'
            if not os.path.isdir(mp3_path + yt_video_author):
                os.makedirs(mp3_path + yt_video_author)
            if not os.path.isdir(png_path + yt_video_author):
                os.makedirs(png_path + yt_video_author)

            try:
                # mp4 download
                yt_video.streams.get_highest_resolution().download(f"{mp4_path}\\{yt_video_author}")

                # converting mp4 to mp3
                os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
                video = moviepy.editor.VideoFileClip(mp4_file_path)
                audio = video.audio
                audio.write_audiofile(mp3_file_path)

                # setting up mp3 file
                video.save_frame(png_file_path)
                audiofile = eyed3.load(mp3_file_path)
                if audiofile.tag is None:
                    audiofile.initTag()
                audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(png_file_path, 'rb').read(), 'image/png')
                audiofile.tag.artist = name(yt_video.author)
                audiofile.tag.album = name(playlist_title)
                audiofile.tag.save()

                print(f'\"{yt_video_title}\" is downloaded as audio. Progress {str(i+1)}/{str(size)}.')
                print('-----------------------------------')
                download_attempts = i + 1
            except Exception:
                failed.append(yt_video_title)
    except KeyboardInterrupt:
        print('Download was interrupted.')
    print_results(download_attempts, failed)


def print_results(successful_downloads, failed):
    print(f'Downloaded {str(successful_downloads)} videos.')
    if failed:

        print(f'Failed to download {str(len(failed))} videos: ')
        for v in failed:
            print(f' - {v}')


# callback function for pytube to show progress
def progress_func(stream, chunk, bytes_remaining):
    curr = stream.filesize - bytes_remaining
    done = int(50 * curr / stream.filesize)
    sys.stdout.write("\r[{}{}] ".format('=' * done, ' ' * (50-done)))
    sys.stdout.flush()


# returns a valid name for file
def name(value: str):
    return (value
            .replace('\'', '')
            .replace(',', '')
            .replace('\"', '')
            .replace('?', '')
            .replace('.', ''))

def mp4_to_mp3(mp4_file_path: str):
    os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
    mp3_file_path = mp4_file_path.replace("mp4", "mp3")
    video = moviepy.editor.VideoFileClip(mp4_file_path)
    audio = video.audio
    audio.write_audiofile(mp3_file_path)

# GO TO TERMINAL AND WRITE:
# pip install pytube
# pip install moviepy
# pip install eyed3

# SET THIS UP:
# url must be YT url, path may not exist (presumably):
URL = "https://youtu.be/DtmwtjOoSYU?si=nXRaGG5fWJldY7zH"
PATH = "D:\\Music1\\y"

# UNCOMMENT AND RUN ONE OF THE FOLLOWING METHODS:
#get_as_audio(URL, PATH)
# YTMusicAndVideoDownloader.get_as_audio(URL, PATH)
# YTMusicAndVideoDownloader.get_playlist_as_video(URL, PATH)
# get_playlist_as_audio(URL, PATH)

mp4_to_mp3("D:\Music1\y\mp4\Dr Robert Sapolsky Science of Stress Testosterone & Free Will.mp4")

# HINTS:
# 1) replace 'music' to 'www' in YTMusic path, and you'll get YT url
# 2) if playlist is user generated, it must be public
# 3) to add all files from auto generated 'Likes' playlist: create playlist,
# go to YTMusic, to 'Likes' - here you'll have 'select' option -
# select tracks/videos that you need and add to the playlist you've created
# 4) do not download to the project folder

# FLAWS:
# 1) if name contains characters that are not allowed by the file system (', ", /, \, ?, etc.),
# the characters will be omitted
# For audio download:
# 2) program does not set up album for mp3 tracks
# 3) if file is a video in YTMusic, the cover of the resulting mp3 will be plain black picture
# 4) program downloads video even when get_audio and get_playlist_as_audio are called ->
# -> video and png files must be deleted manually (saved in folders: 'mp4', 'png')

