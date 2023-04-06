import requests
import json
def upload_to_tiktok(access_token, open_id, video_file_path):
    url = f'https://open-api.tiktok.com/share/video/upload/?access_token={access_token}&open_id={open_id}'

    with open(video_file_path, 'rb') as video_file:
        files = {'video': video_file}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        data = response.json()
        if data['data']['error_code'] == 0:
            print("Video uploaded successfully.")
            print("Share ID:", data['data']['share_id'])
        else:
            print("Error uploading video:", data['data']['error_msg'])
    else:
        print("Request failed with status code:", response.status_code)


# Load the access_token and open_id from the JSON file.
with open('tiktok_credentials.json', 'r') as f:
    tiktok_credentials = json.load(f)

access_token = tiktok_credentials['access_token']
open_id = tiktok_credentials['open_id']

video_file_path = r"C:\repos\reddit-video-gen\OutputVideos\2023-04-06-12acoep.mp4"

upload_to_tiktok(access_token, open_id, video_file_path)
