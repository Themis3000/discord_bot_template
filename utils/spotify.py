"""Retrieves various bits of information from spotify (just playlists for now)"""
import requests
from utils.time import get_current_milliseconds


class Spotify:
    def __init__(self):
        self.access_token = ""
        self.access_token_expiration = 0

    def get_access_token(self):
        # In the case that the access token has not yet expired
        if get_current_milliseconds() < self.access_token_expiration:
            return self.access_token

        response = requests.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player")

        if response.status_code != 200:
            print("Failed to get access code")
            return None

        response_json = response.json()
        self.access_token = response_json["accessToken"]
        self.access_token_expiration = response_json["accessTokenExpirationTimestampMs"]
        return self.access_token

    def get_playlist_tracks(self, url: str):
        start_schema = "https://open.spotify.com/playlist/"

        token = self.get_access_token()

        if token is None or not url.startswith(start_schema):
            return None

        playlist_id = url[len(start_schema):].split("?", 1)[0]

        response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", params={
            "offset": "0",
            "limit": "100",
            "additional_types": "track,episode"
        }, headers={
            "authorization": f"Bearer {token}"
        })

        if response.status_code == 200:
            return response.json()
        return None
