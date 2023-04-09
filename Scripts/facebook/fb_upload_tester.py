import os
import requests
from Secrets.fb_secrets import FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID
import os
import facebook


def upload_video_to_facebook(video_file_path, title, description, access_token, page_id):
    graph = facebook.GraphAPI(access_token)
    file_size = os.path.getsize(video_file_path)

    start_upload_response = graph.request(
        f"{page_id}/videos",
        args={
            "upload_phase": "start",
            "file_size": file_size,
            "creative_folder_id": "803346404544574"
        },
        method="POST"
    )


    if "start_offset" not in start_upload_response:
        print("Error: 'start_offset' not found in the response.")
        print(start_upload_response)
        return

    start_offset = int(start_upload_response.get("start_offset"))
    end_offset = int(start_upload_response.get("end_offset"))
    upload_session_id = start_upload_response.get("upload_session_id")


    # Step 2: Upload the video file in chunks
    with open(video_file_path, "rb") as video_file:
        while start_offset < end_offset:
            video_file.seek(start_offset)
            chunk = video_file.read(end_offset - start_offset)
            chunk_upload_url = f"https://graph-video.facebook.com/v16.0/{page_id}/videos"
            chunk_upload_params = {
                "upload_phase": "transfer",
                "access_token": access_token,
                "upload_session_id": upload_session_id,
                "start_offset": start_offset,
            }
            chunk_upload_files = {"video_file_chunk": (os.path.basename(video_file_path), chunk)}
            chunk_upload_response = requests.post(chunk_upload_url, params=chunk_upload_params, files=chunk_upload_files).json()
            start_offset = int(chunk_upload_response.get("start_offset"))
            end_offset = int(chunk_upload_response.get("end_offset"))

    # Step 3: Finish the upload session
    finish_upload_url = f"https://graph-video.facebook.com/v16.0/{page_id}/videos"
    finish_upload_params = {
        "upload_phase": "finish",
        "access_token": access_token,
        "upload_session_id": upload_session_id,
        "title": title,
        "description": description,
    }

    finish_upload_response = requests.post(finish_upload_url, params=finish_upload_params).json()
    return finish_upload_response

if __name__ == "__main__":
    video_file_path = "OutputVideos/06-12br1id.mp4"
    title = "Example Title"
    description = "Example Description"

    response = upload_video_to_facebook(video_file_path, title, description, FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID)
    print("Video uploaded with response:", response)

