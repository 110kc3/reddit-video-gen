from google_auth_oauthlib.flow import InstalledAppFlow

def get_youtube_credentials():
    client_secrets_file = "client_secrets_desktop.json"
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    
    with open("authorized_user.json", "w") as f:
        f.write(credentials.to_json())

if __name__ == "__main__":
    get_youtube_credentials()
