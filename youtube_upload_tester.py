import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

def upload_video(file_path, title, description, tags, category_id):
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    # Load OAuth2 credentials from a file
    credentials = Credentials.from_authorized_user_file('authorized_user.json', scopes)


    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public'  # Set the privacy status of the video
        }
    }

    media_file = googleapiclient.http.MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if response is not None:
            if 'id' in response:
                print(f"Video uploaded successfully. Video ID: {response['id']}")
            else:
                exit("The upload failed with an unexpected response: %s" % response)

if __name__ == "__main__":
    video_file_path =  r"C:\repos\reddit-video-gen\OutputVideos\achess.mp4"  # Replace with the path to your video file
    video_title = "Test Video Title"
    video_description = "This is a test video description."
    video_tags = ["test", "video", "upload"]
    video_category_id = "22"  # Category ID for "People & Blogs"

    upload_video(video_file_path, video_title, video_description, video_tags, video_category_id)
