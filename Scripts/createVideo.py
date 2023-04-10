from moviepy.editor import *
import shutil
import os
import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError
from Secrets.aws_secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import Scripts.aws_bucket_handler

import Scripts.reddit as reddit

import  Scripts.screenshot as screenshot, time, subprocess, random, configparser, sys, math
from Scripts.youtube_upload import upload_video




def createVideo():
    config = configparser.ConfigParser()
    config.read('config.ini')
    outputDir = config["General"]["OutputDirectory"]
    
    # Get the background videos bucket
    bg_bucket = config['S3']['BackgroundVideosBucket']
    used_bg_bucket = config["S3"]["UsedBackgroundVideosBucket"]
    # Flag to check if the video is from the used_bg_bucket
    from_used_bg_bucket = False

     # Get the background videos bucket
    output_bucket = config['S3']['OutputVideosBucket']
    uploaded_youtube_output_bucket = config["S3"]["YoutubeOutputVideosBucket"]



    startTime = time.time()

    # Initialize the S3 client
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


    # Get script from reddit
    # If a post id is listed, use that. Otherwise query top posts
    if (len(sys.argv) == 2):
        script = reddit.getContentFromId(outputDir, sys.argv[1])
    else:
        postOptionCount = int(config["Reddit"]["NumberOfPostsToSelectFrom"])
        auto_select = config.getboolean("Reddit", "AutoSelectPost")
        subreddit_name = config["Reddit"]["Subreddit"]
        time_filter = config["Reddit"]["TimeFilter"]
        script = reddit.getContent(outputDir, postOptionCount, auto_select, subreddit_name, time_filter)

        # script = reddit.getContent(outputDir, postOptionCount, auto_select)
    fileName = script.getFileName()

    # Create screenshots
    screenshot.getPostScreenshots(fileName, script)


    print("starting background bucket reading")

    # List objects in the background videos bucket
    response = s3.list_objects_v2(Bucket=bg_bucket)

    # Check if there are no videos in the bucket
    if 'Contents' not in response:
        # List objects in the used background videos bucket
        response = s3.list_objects_v2(Bucket=used_bg_bucket)
        from_used_bg_bucket = True

    # Store object keys in a list
    bg_videos = [content['Key'] for content in response['Contents']]

    # Randomly select a background video
    selected_bg_video_key = random.choice(bg_videos)

    # Download the selected background video to a temporary file
    # tmp_bg_video_file = f"/tmp/{os.path.basename(selected_bg_video_key)}" #linux

    script_dir = os.path.dirname(os.path.realpath(__file__))
    tmp_bg_video_file = os.path.join(script_dir, os.path.basename(selected_bg_video_key))

    # tmp_bg_video_file = f"/tmp/{os.path.basename(selected_bg_video_key)}".replace("\\", "/") #windows

    print("starting background bucket download")
    s3.download_file(bg_bucket, selected_bg_video_key, tmp_bg_video_file)

    # Setup background clip and loop the video if it's too short
    voiceover_duration = script.getDuration()
    raw_background_video = VideoFileClip(filename=tmp_bg_video_file, audio=False)
    bg_duration = raw_background_video.duration
    num_loops = math.ceil(voiceover_duration / bg_duration)
    backgroundVideo = raw_background_video.fx(vfx.loop, duration=voiceover_duration)
    w, h = backgroundVideo.size


    # # Setup background clip
    # bgDir = config["General"]["BackgroundDirectory"]
    # bgPrefix = config["General"]["BackgroundFilePrefix"]
    # bgCount = int(config["General"]["BackgroundVideos"])
    # # Randomize bgIndex until the video file exists
    # bgIndex=None
    # backgroundVideo = None
    # while not os.path.exists(f"{bgDir}/{bgPrefix}{bgIndex}.mp4"):
    #     bgIndex = random.randint(0, bgCount-1)

    # # bgIndex = random.randint(0, bgCount-1)

    # # Setup background clip and loop the video if it's too short
    # voiceover_duration = script.getDuration()
    # raw_background_video = VideoFileClip(
    #     filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4",
    #     audio=False)
    # bg_duration = raw_background_video.duration
    # num_loops = math.ceil(voiceover_duration / bg_duration)
    # backgroundVideo = raw_background_video.fx(vfx.loop, duration=voiceover_duration)
    # w, h = backgroundVideo.size

    def __createClip(screenShotFile, audioClip, marginSize):
        print(f"Creating clip for: {screenShotFile}")  # Add this line to print the file path

        imageClip = ImageClip(
            screenShotFile,
            duration=audioClip.duration
            ).set_position(("center", "center"))
        imageClip = imageClip.resize(width=(w-marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip

    # Create video clips
    print("Editing clips together...")
    clips = []
    marginSize = int(config["Video"]["MarginSize"])

    clips.append(__createClip(script.titleSCFile, script.titleAudioClip, marginSize))
    for comment in script.frames:
        if comment.screenShotFile:  # Add this line to check if the file path is not empty
            clips.append(__createClip(comment.screenShotFile, comment.audioClip, marginSize))

    # Merge clips into single track
    contentOverlay = concatenate_videoclips(clips).set_position(("center", "center"))

    final = CompositeVideoClip(
        clips=[backgroundVideo, contentOverlay], 
        size=backgroundVideo.size).set_audio(contentOverlay.audio.set_duration(voiceover_duration))

    final.duration = script.getDuration()
    final.set_fps(backgroundVideo.fps)

    # Write output to file
    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    safe_title = "".join([c if c.isalnum() or c.isspace() else "_" for c in script.title]) 

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")  # Replace colons with nothing in the time format
    outputFile = f"{outputDir}/{safe_title}-{timestamp}.mp4"  # Use the title and timestamp as the filename

    # outputFile = f"{outputDir}/{safe_title}-{fileName}.mp4"  # Use the title as the filename

    final.write_videofile(
        outputFile, 
        codec = 'mpeg4',
        threads = threads, 
        bitrate = bitrate
    )
    print(f"Video completed in {time.time() - startTime}")


    # Preview in VLC for approval before uploading
    if (config["General"].getboolean("PreviewBeforeUpload")):
        vlcPath = config["General"]["VLCPath"]
        p = subprocess.Popen([vlcPath, outputFile])
        print("Waiting for video review. Type anything to continue")
        wait = input()

    print("Video is ready to upload!")
    print(f"Title: {script.title}  File: {outputFile}")
    endTime = time.time()
    print(f"Total time: {endTime - startTime}")

    # Upload the video to YouTube
    video_title = script.title

    # Randomize video description   
    descriptions = [
        "We dive into some of the funniest and most outrageous questions and answers from the popular AskReddit forum. Join us as we explore the weird and wonderful world of Reddit, with entertaining and meme-worthy moments guaranteed",
        "Join us for a wild ride through the best of AskReddit as we uncover hilarious, bizarre, and downright entertaining questions and answers. Be prepared for a rollercoaster of emotions and lots of laughter!",
        "Experience the most entertaining and hilarious moments from AskReddit as we dive into the world of funny questions and outrageous answers. Get ready for a journey full of laughs and unforgettable stories!",
        "Welcome to our latest Reddit Ask video, where we dive into some of the most bizarre, funny, and downright ridiculous questions and answers from the popular AskReddit forum. ",
        "Join us for our latest Reddit Ask video, where we explore some of the most outrageous and hilarious questions and answers from the AskReddit community. From memes to viral content, we've got it all, so sit back, relax, and get ready to laugh!",
        "In this inspiring short story-telling video, we hear from people who have overcome incredible challenges and gone on to achieve amazing things. Their stories of perseverance and determination will leave you feeling motivated and ready to tackle your own challenges."
    ]
    video_description = random.choice(descriptions)

    # Randomize video tags
    all_tags = ["Reddit", "AskReddit", "AMA", "Entertainment", "Comedy", "Humor", "Memes", "Funny", "Laugh", 
                "Viral", "Storytelling", "ShortStories", "TrueStories", "Animation", "Narrated", "Inspiration", 
                "Motivation", "Heartwarming", "Emotional" , "Memes", "MemeWorthy", "RedditAsk", "funnyquestions", 
                "outrageousanswers", "meme", "entertaining", "humor", "bizarre", "hilarious", "AskReddit",
                "shortstory", "inspiring", "motivation", "perseverance", "determination", "overcomingchallenges",
                "achievement", "personalgrowth", "success",
                "RedditScreenshots", "Voiceover", "Storytelling", "Narration", "SocialMedia", 
                "InternetCulture", "FunnyPosts", "Heartwarming", "Shocking", "Memes", "ViralContent", 
                "UserGeneratedContent", "Discussion", "Debate", "Controversy", "Topical", "Insightful", 
                "Community", "Diversity", "Inclusion" ]
    
    num_tags_to_select = random.randint(12, len(all_tags))
    video_tags = random.sample(all_tags, num_tags_to_select - 1)  # Subtract 1 to account for the Shorts tag
    video_tags = validate_tags(video_tags)

    video_tags.append("Shorts")  # Add the Shorts tag back to the list of random tags
    video_category_id = "22"  # Entertainment category

    print("Starting video upload to YT")
 
    # Upload the video to YouTube
    # upload_successful = upload_video(outputFile, video_title, video_description, video_tags)
    upload_successful = True

    # Choose the appropriate S3 bucket based on the upload success
    if upload_successful:
        output_bucket = uploaded_youtube_output_bucket
    else:
        output_bucket = output_bucket

    # Upload the video to the appropriate S3 bucket
    s3.upload_file(Filename=outputFile, Bucket=output_bucket, Key=os.path.basename(outputFile))
  
    

    print("Starting cleanup")

    # Get the current script directory
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Define the paths for the Screenshots and Voiceovers folders
    screenshots_folder = os.path.join(current_dir, "Screenshots")
    voiceovers_folder = os.path.join(current_dir, "Voiceovers")

    # Clear the folders
    clear_folder(screenshots_folder)
    clear_folder(voiceovers_folder)

    backgroundVideo.close()
    # Close the raw_background_video clip
    raw_background_video.close()
    # remove the temporary file after you are done
    os.remove(tmp_bg_video_file)

    # Remove the background video file from the bucket if it's not from the used_bg_bucket
    if not from_used_bg_bucket:
        s3.delete_object(Bucket=bg_bucket, Key=selected_bg_video_key)



    #TODO - fix for S3 bucket handling
    # # after the video is uploaded
    # used_yt_dir = f"{outputDir}/used_yt"  
    # used_backgroundvideo_dir = f"{bgDir}/used"
    
    # # Call the cleanup_files function after uploading the video
    # cleanup_files(script)

    # # Move the output video to the "used_yt" folder
    # try:
    #     # shutil.move(outputFile, f"{used_yt_dir}/{safe_title}-{fileName}.mp4")
    #     unique_output_file = generate_unique_filename(used_yt_dir, f"{safe_title}-{fileName}.mp4")
    #     shutil.move(outputFile, os.path.join(used_yt_dir, unique_output_file))

    # except Exception as e:
    #     print(f"An error occurred while moving the output video: {e}")

    # # Move the background video to the "used" folder
    # try:
    #     # Move the background video to the "used" folder
    #     unique_background_file = generate_unique_filename(used_backgroundvideo_dir, f"{bgPrefix}{bgIndex}.mp4")
    #     shutil.move(f"{bgDir}/{bgPrefix}{bgIndex}.mp4", os.path.join(used_backgroundvideo_dir, unique_background_file))
    # except Exception as e:
    #     print(f"An error occurred while moving the background video: {e}")


import os
import shutil

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def generate_unique_filename(destination, filename):
    if os.path.exists(os.path.join(destination, filename)):
        base, ext = os.path.splitext(filename)
        filename = f"{base}_1{ext}"
    return filename

def validate_tags(tags):
    MAX_TAG_LENGTH = 30
    MAX_TAGS_LENGTH = 450

    valid_tags = []
    total_tags_length = 0

    for tag in tags:
        if len(tag) <= MAX_TAG_LENGTH and (total_tags_length + len(tag) + 1) <= MAX_TAGS_LENGTH:
            valid_tags.append(tag)
            total_tags_length += len(tag) + 1

    return valid_tags
