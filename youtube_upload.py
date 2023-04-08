from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import sys 

def upload_video(file_path, title, description, tags, category_id):
    # Truncate the title if it's longer than 100 characters
    if len(title) > 100:
        title = title[:96] + "..."

    try:
        credentials = Credentials.from_authorized_user_file('authorized_user.json', ['https://www.googleapis.com/auth/youtube.upload'])
        youtube = build('youtube', 'v3', credentials=credentials)

        # Convert the tags list to a single string with tags prepended with '#' and separated by spaces
        tags_str = " ".join([f"#{tag}" for tag in tags])

        # Add the tags string to the end of the description
        description += f"\n\n{tags_str}"
        # Truncate the description if it's longer than 4500 characters (max 5k in yt)
        if len(description) > 4500:
            description = description[:4450] + "..."


        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': 'public'
            }
        }

        with open(file_path, 'rb') as video_file:
            request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
            )
            response = request.execute()

        print(f"Video uploaded to YouTube with video ID: {response['id']}")
    except HttpError as e:
        print(f"An error occurred: {e}")
        print("Video was not uploaded to YouTube.")
        sys.exit(1)
