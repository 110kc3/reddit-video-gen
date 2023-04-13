from datetime import datetime
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
import tempfile

import Scripts.reddit as reddit

import  Scripts.screenshot as screenshot, time, subprocess, random, configparser, sys, math
from Scripts.youtube_upload import upload_video
from Scripts.aws_bucket_handler import download_file_from_s3, upload_file_to_s3, upload_video_id_to_s3

from moviepy.video.fx.crop import crop
from moviepy.video.fx import resize
from PIL import Image
def createVideo():
    
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        outputDir = config["General"]["OutputDirectory"]
        
        # Get the background videos bucket
        bg_bucket = config['S3']['BackgroundVideosBucket']
        used_bg_bucket = config["S3"]["UsedBackgroundVideosBucket"]
        # Flag to check if the video is from the used_bg_bucket
        from_used_bg_bucket = False

        # Get the background videos bucket
        output_bucket = config['S3']['OutputVideosBucket'] #not uploaded to YT
        uploaded_youtube_output_bucket = config["S3"]["YoutubeOutputVideosBucket"]
        uploaded_youtube_IDs_output_bucket = config["S3"]["IDsOfCreatedVideosBucket"]

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

        # Create screenshots, there is an issue with google popup, not sure how to fix it - trying couple times works eventually
        max_attempts = 5
        success = False

        for attempt in range(max_attempts):
            try:
                screenshot.getPostScreenshots(fileName, script)
                success = True
                break
            except Exception as e:
                print(f"screenshot Attempt {attempt + 1} failed with error: {e}")
                if attempt == max_attempts - 1:
                    print("All screenshot attempts failed. Exiting.")
                    exit()
                else:
                    print("Retrying screenshot...")

        if success:
            print("Screenshots created successfully.")
        print("starting background bucket reading")
        response = ""
        # List objects in the background videos bucket
        response = s3.list_objects_v2(Bucket=bg_bucket)

        # Check if there are no videos in the bucket
        if 'Contents' not in response:
            # List objects in the used background videos bucket
            response = s3.list_objects_v2(Bucket=used_bg_bucket)
            # print(response)
            print("NO MORE BACKGROUND IMAGES") #TODO create an alert
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
        # download_file_from_s3()

        s3.download_file(bg_bucket, selected_bg_video_key, tmp_bg_video_file)
        # there is an issue if the 2nd bucket is selected TODO
        # try:
        #     with tempfile.NamedTemporaryFile(delete=False) as tmp_bg_video_file:
        #         download_file_from_s3(s3, bg_bucket, selected_bg_video_key, tmp_bg_video_file.name)
        #         raw_background_video = moviepy.editor.VideoFileClip(tmp_bg_video_file.name, audio=False)
        # except Exception as e:
        #     print(f"An error occurred while creating video  {e}")
        #     exit()

        # Setup background clip and loop the video if it's too short
        voiceover_duration = script.getDuration()
        raw_background_video = VideoFileClip(filename=tmp_bg_video_file, audio=False)
        bg_duration = raw_background_video.duration
        #not tested
        if bg_duration > voiceover_duration:
            print("The background video is longer than the voiceover. Cutting to fit the duration.")
            raw_background_video = raw_background_video.subclip(0, voiceover_duration+1)
            bg_duration = raw_background_video.duration

        num_loops = math.ceil(voiceover_duration / bg_duration)

        # Get the size of the raw background video
        w, h = raw_background_video.size
        print("raw_background_video.size is " + str(raw_background_video.size))

        # Check if the video is in vertical format
        aspect_ratio = w / h
        print("aspect_ratio is " + str(aspect_ratio))
        if aspect_ratio < 1:
            print("The background video is in vertical format.")
        else:
            print("The background video is NOT in vertical format. Converting to vertical format.")

            # Calculate the new width while maintaining the aspect ratio
            new_width = int(h * (9 / 16))

            # Crop the video to fit the vertical format while keeping its center
            raw_background_video = crop(raw_background_video, width=new_width, height=h, x_center=raw_background_video.w / 2, y_center=raw_background_video.h / 2)

        # Loop the video after cropping (if necessary)
        backgroundVideo = raw_background_video.fx(vfx.loop, duration=voiceover_duration)

        def __createClip(screenShotFile, audioClip, marginSize):
            print(f"Creating clip for: {screenShotFile}")

            # Calculate the new size for the screenshot while maintaining its aspect ratio
            screenshot_image = Image.open(screenShotFile)
            image_w, image_h = screenshot_image.size
            scale_w = (w - 2 * marginSize) / image_w
            scale_h = (h - 2 * marginSize) / image_h

            scale_factor = min(scale_w, scale_h)

            new_w = int(image_w * scale_factor)
            new_h = int(image_h * scale_factor)

            # Create the image clip
            imageClip = ImageClip(
                screenShotFile,
                duration=audioClip.duration
            ).set_position(("center", "center"))

            # Resize the image
            imageClip = imageClip.resize(width=new_w, height=new_h)

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

        outputFile = f"{outputDir}/{safe_title}-{fileName}.mp4"  # Use the title as the filename

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
        upload_successful = upload_video(outputFile, video_title, video_description, video_tags, video_category_id)
        #upload_successful = True

        # Choose the appropriate S3 bucket based on the upload success
        if upload_successful:
            output_bucket = uploaded_youtube_output_bucket

        # Upload the video to the appropriate S3 bucket
        upload_file_to_s3(s3, outputFile, output_bucket, os.path.basename(outputFile))
    
        # Add this line after the video is created and uploaded
        print("starting to upload created video ID")
        upload_video_id_to_s3(s3, outputFile, uploaded_youtube_IDs_output_bucket, video_description, video_tags)


        print("Starting cleanup")
        # current_dir variable to the parent directory,
        current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


        try:
            # Define the paths for the Screenshots and Voiceovers folders
            screenshots_folder = os.path.join(current_dir, "Screenshots")
            voiceovers_folder = os.path.join(current_dir, "Voiceovers")
            outputvideos_folder = os.path.join(current_dir, "OutputVideos")

            # Clear the folders
            clear_folder(screenshots_folder)
            clear_folder(outputvideos_folder)
            clear_folder(voiceovers_folder)

        except:
            print("failed to remove screenshot and voiceover contents")
        
        try:
            print("trying to delete background file")
            backgroundVideo.close()
            # Close the raw_background_video clip
            raw_background_video.close()
            # remove the temporary file after you are done
            os.remove(tmp_bg_video_file)

        except:
            print("failed to remove screenshot and voiceover contents")
        
        #todo delete outpud video local 

        # Remove the background video file from the bucket if it's not from the used_bg_bucket
        if not from_used_bg_bucket:
            s3.delete_object(Bucket=bg_bucket, Key=selected_bg_video_key)
    except Exception as e:
   
        print(f" EXCEPT  issue with create video function - calling cleanup Reason: {e}")
        current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        try:
            # Define the paths for the Screenshots and Voiceovers folders
            screenshots_folder = os.path.join(current_dir, "Screenshots")
            voiceovers_folder = os.path.join(current_dir, "Voiceovers")
            outputvideos_folder = os.path.join(current_dir, "OutputVideos")

            # Clear the folders
            clear_folder(screenshots_folder)
            clear_folder(outputvideos_folder)
            clear_folder(voiceovers_folder)

        except:
            print("EXCEPTEXCEPT failed to remove screenshot and voiceover contents")
        
        try:
            #This may not be created yet
            print("EXCEPTEXCEPTEXCEPT trying to delete background file")
            backgroundVideo.close()
            # Close the raw_background_video clip
            raw_background_video.close()
            # remove the temporary file after you are done
            os.remove(tmp_bg_video_file)

        except:
            print("EXCEPTEXCEPTEXCEPT failed to remove screenshot and voiceover contents")




import os
import shutil

def clear_folder(folder_path):
    print(f"Clearing folder: {folder_path}")  # Add this line
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        print(f"Deleting file: {file_path}")  # Add this line
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
