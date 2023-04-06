import requests
import webbrowser
import json

# Replace these values with your App ID, Client key, and Client secret.
APP_ID = ''
CLIENT_KEY = ''
CLIENT_SECRET = ''

# Set your desired redirect URI.
REDIRECT_URI = "???"

# TODO:
# https://developers.tiktok.com/doc/web-video-kit-with-web?enter_method=left_navigation
# https://developers.tiktok.com/doc/login-kit-web?enter_method=embed


# Construct the authorization URL.
AUTH_URL = f'https://open-api.tiktok.com/platform/oauth/connect/?client_key={CLIENT_KEY}&response_type=code&scope=video.upload&redirect_uri={REDIRECT_URI}&state=your_custom_state'

# Open the authorization URL in the user's browser.
webbrowser.open(AUTH_URL)

# Prompt the user to enter the temporary code received in the redirect.
code = input('Enter the temporary code from the URL redirected to: ')

# Exchange the temporary code for an access_token and open_id.
token_url = 'https://open-api.tiktok.com/oauth/access_token/'
token_data = {
    'client_key': CLIENT_KEY,
    'client_secret': CLIENT_SECRET,
    'code': code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI,
}

response = requests.post(token_url, data=token_data)
response_json = response.json()

# Extract the access_token and open_id from the response.
access_token = response_json['data']['access_token']
open_id = response_json['data']['open_id']

# Print the access_token and open_id.
print(f'Access token: {access_token}')
print(f'Open ID: {open_id}')



# Save the access_token and open_id to a JSON file.
with open('tiktok_credentials.json', 'w') as f:
    json.dump({'access_token': access_token, 'open_id': open_id}, f)

print('TikTok credentials saved to tiktok_credentials.json.')

