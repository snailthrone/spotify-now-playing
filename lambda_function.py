import os
import requests
import time
import boto3
import json

client_id = os.getenv('CLIENT_ID')
base64client = os.getenv('BASE_64_CLIENT')
refresh_token = os.getenv('REFRESH_TOKEN')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SpotifyListenings')

def get_new_token():
  data = { 'grant_type': 'refresh_token', 'refresh_token': refresh_token }
  headers = { 'Authorization': f'Basic {base64client}' }
  
  p = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
  return p.json()

def get_data(uri, token):
  headers = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Accept': 'application/json' }
  r = requests.get(uri, headers=headers)
  return r.json()
  
def get_recent_listening(token):
  data = get_data('https://api.spotify.com/v1/me/player/recently-played', token)
  
  try:
    song = data['items'][0]['track']['name']
    artist = data['items'][0]['track']['artists'][0]['name']
    return { 'artist': artist, 'song': song, 'message': f'Last listened to {song} by {artist}' }

  except:
    pass
  
def get_current_listening(token):
  data = get_data('https://api.spotify.com/v1/me/player/currently-playing', token)
  
  try:
    song = data['item']['name']
    isPlaying = data['is_playing']
    artist = data['item']['artists'][0]['name']
    
    if (isPlaying):
      return { 'artist': artist, 'song': song, 'message': f'Currently listening to {song} by {artist}' }

  except:
    pass
  
  if not isPlaying:
    return get_recent_listening(token)
  
def lambda_handler(event, context):
  response = 'Not listening to Spotify now.'
  song = 'n/a'
  artist = 'n/a'
  
  dbResponse = table.get_item(Key={'spotify': 'prod'})
  expiresAt = dbResponse['Item']['expiresAt']
  
  if expiresAt <= time.time():
    new_token = get_new_token()
    table.put_item(Item={'spotify': 'prod', 'expiresAt': int(time.time()) + new_token['expires_in'], 'accessToken': new_token['access_token'] })
  
  dbResponse = table.get_item(Key={'spotify': 'prod'})
  accessToken = dbResponse['Item']['accessToken']
  
  listening = get_current_listening(accessToken)
  
  artist = listening['artist']
  song = listening['song']
  response = listening['message']
  
  return response