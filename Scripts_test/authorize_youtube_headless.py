from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

def get_youtube_credentials():
    client_secrets_file = "/home/ubuntu/Scripts_test/client_secrets_desktop.json"
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    credentials_file = "/home/ubuntu/Scripts_test/credentials.json"

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

    # Set the authorization and token endpoints of the Google API
    flow.oauth2session.auth.authorization_url = 'https://accounts.google.com/o/oauth2/auth'
    flow.oauth2session.auth.token_url = 'https://oauth2.googleapis.com/token'

    authorization_url, state = flow.authorization_url(prompt='consent')
    print('Please go to this URL to authorize the application: {}\n'.format(authorization_url))

    authorization_code = input('Enter the authorization code: ').strip()
    flow.fetch_token(code=authorization_code)

    credentials = flow.credentials
    Credentials.to_json(credentials)
    with open(credentials_file, "w") as f:
        f.write(credentials.to_json())

if __name__ == "__main__":
    get_youtube_credentials()
