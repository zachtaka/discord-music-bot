import discord
import os
from discord.ext.commands import Bot
import time
import ffmpeg
import youtube_dl
from pathlib import Path
import threading
api_key = "AIzaSyAglY6Zsl4AS9ard47fIjB4hvBeLQpGRm8"
from apiclient.discovery import build
youtube = build('youtube', 'v3', developerKey=api_key)
from shutil import copy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import aiofiles as aiof

CURRENT_PATH = "C:/Users/zachtaka/Desktop/git/music-bot"




birdy_uri = 'spotify:artist:64Eb4jttIVIP6T2qVBP8wh'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
bot = Bot(command_prefix='!')
global_context = []
skip_l = []
song_order_l = []

def my_after(error):
  coro = vc.disconnect()



def reset():
  for file in os.listdir(f"{CURRENT_PATH}/queue"):
    os.remove(f"{CURRENT_PATH}/queue/{file}")
  global_context = []
  skip_l = []
  song_order_l = []

def get_voice_client(context):
  return discord.utils.get(context.bot.voice_clients, guild=context.guild)

def is_connected(context):
  voice_client = get_voice_client(context)
  return voice_client and voice_client.is_connected()

def is_playing(context):
  voice_client = get_voice_client(context)
  return voice_client and voice_client.is_playing()

def is_youtube_link(str):
  if "youtube.com" in str:
    return 1
  else: 
    return 0

def is_spotify_link(str):
  if "spotify" in str:
    return 1
  else: 
    return 0

def get_spotify_playlist(str):
  track_l = []
  results = spotify.search(q=str, type='playlist')
  # print(results)
  for track in results['tracks']:
    # print('track    : ' + track['name'])
    # print()
    track_l.append(track['name'])
  return [track_l]

def exists(video_title):
  for file in os.listdir(f"{CURRENT_PATH}/archive"):
    if video_title in file:
      song_order_l.append(video_title)
      copy(f"{CURRENT_PATH}/archive/{file}", f"{CURRENT_PATH}/queue")
      return 1
  return 0

def search_youtube(str):
  request = youtube.search().list(q=str,part='snippet',type='video')
  # print(type(request))
  res = request.execute()
  
  for item in res['items']:
    if (len(item['id']['videoId']) == 0):
      return ""

    # print(item['id']['videoId'])
    video_id = item['id']['videoId']
    video_title = item['snippet']['title']
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    # print(youtube_url)
    return [youtube_url, video_title]

      

def drain_music():
  # Whenever there is a file in the folder, play it
  while (1):
    for file in os.listdir(f"{CURRENT_PATH}/queue"):
      if file.endswith(".mp3"):
        # print(f"Start playing file: {file}")
        file_path = f"{CURRENT_PATH}/queue/{file}"
        if len(global_context) > 0: 

          context = global_context[0]
          voice_client = get_voice_client(context)
          voice_client.play(discord.FFmpegPCMAudio(file_path))
          
          while is_playing(context) and (len(skip_l) == 0):
            time.sleep(1)


          if (len(skip_l) > 0):
            voice_client.stop()
            skip_l.pop(0)
            time.sleep(0.5)


          os.remove(file_path)
          
    time.sleep(1)

def download_audio(url_str):
  # Download audio file
  ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url_str, download=False)
    video_title = info.get('title', None)  
    video_id = info.get("id", None)
    ydl.download([url_str])

  # Move it to the queue and archive folder
  for file in os.listdir("./"):
        if file.endswith(".mp3"):
            song_order_l.append(video_title)
            os.rename(file, f"{CURRENT_PATH}/archive/{video_title}.mp3")
            copy(f"{CURRENT_PATH}/archive/{video_title}.mp3", f"{CURRENT_PATH}/queue")

  

@bot.event
async def on_ready():

  reset()

  t = threading.Thread(target=drain_music, args=())
  t.start()

@bot.command()
async def play(context, *argv):

  user_string = ' '.join(argv)

  # Connect to users channel
  channel = context.message.author.voice.channel
  if not is_connected(context):
    vc = await channel.connect()

  global_context.append(context)

  video_title = "12345678asdfghjxcvbnm"
  if not is_spotify_link(user_string):
    [youtube_url, video_title] = search_youtube(user_string)

  # Check if audio exists in cache
  if not exists(video_title):
    # Download audio
    if is_youtube_link(user_string):
      download_audio(user_string)
    elif is_spotify_link(user_string):
      song_l = get_spotify_playlist(user_string)
      # print(song_l)
      for song in song_l:
        [youtube_url2, video_title2] = search_youtube(user_string)
        if not exists(video_title2):
          download_audio(youtube_url2)
    else: # user provided title
      if len(youtube_url) > 0:
        download_audio(youtube_url)
      else: 
        await context.send("Didn't find anything interesting in youtube...")



@bot.command()
async def leave(context):
  if is_connected(context):
    voice_client = get_voice_client(context)
    await voice_client.disconnect()
  else:
    await context.send("The bot is not connected to a voice channel.")


@bot.command()
async def skip(context):
  voice_client = get_voice_client(context)
  if voice_client.is_playing():
    skip = 1
  else:
    await context.send("Currently no audio is playing.")


@bot.command()
async def pause(context):
  voice_client = get_voice_client(context)
  if voice_client.is_playing():
    voice_client.pause()
  else:
    await context.send("Currently no audio is playing.")


@bot.command()
async def resume(context):
  voice_client = get_voice_client(context)
  if voice_client.is_paused():
    voice_client.resume()
  else:
    await context.send("The audio is not paused.")

@bot.command()
async def stop(context):
  voice_client = get_voice_client(context)
  voice_client.stop()


@bot.command()
async def next(context):
  skip_l.append(1)


@bot.command()
async def queue(context):
  song_l = ["```", "Songs in queue:"]

  for idx, song in enumerate(song_order_l):
    song_l.append(f"\t{idx+1}) {song}")
  
  song_l.append("```")
  song_l_str = "\n".join(song_l)
  await context.send(song_l_str)


@bot.command()
async def reset(context):
  reset()
    
bot.run("ODE1NTk3NjM3ODIyNTc4NzA4.YDuufQ.OthY8Z1G1BcEfgQBBVWfcn7KJhI")