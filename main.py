from moviepy.editor import *

import reddit, screenshot, time, subprocess, random, configparser, sys, math
from youtube_upload import upload_video

def createVideo():
    config = configparser.ConfigParser()
    config.read('config.ini')
    outputDir = config["General"]["OutputDirectory"]

    startTime = time.time()

    # Get script from reddit
    # If a post id is listed, use that. Otherwise query top posts
    if (len(sys.argv) == 2):
        script = reddit.getContentFromId(outputDir, sys.argv[1])
    else:
        postOptionCount = int(config["Reddit"]["NumberOfPostsToSelectFrom"])
        script = reddit.getContent(outputDir, postOptionCount)
    fileName = script.getFileName()

    # Create screenshots
    screenshot.getPostScreenshots(fileName, script)

    # Setup background clip
    bgDir = config["General"]["BackgroundDirectory"]
    bgPrefix = config["General"]["BackgroundFilePrefix"]
    bgCount = int(config["General"]["BackgroundVideos"])
    bgIndex = random.randint(0, bgCount-1)
    # bgIndex = 1
    # backgroundVideo = VideoFileClip(
    #     filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4", 
    #     audio=False).subclip(0, script.getDuration())
    # w, h = backgroundVideo.size

    # Setup background clip and loop the video if it's too short
    voiceover_duration = script.getDuration()
    raw_background_video = VideoFileClip(
        filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4",
        audio=False)
    bg_duration = raw_background_video.duration
    num_loops = math.ceil(voiceover_duration / bg_duration)
    backgroundVideo = raw_background_video.fx(vfx.loop, duration=voiceover_duration)
    w, h = backgroundVideo.size

    def __createClip(screenShotFile, audioClip, marginSize):
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
        clips.append(__createClip(comment.screenShotFile, comment.audioClip, marginSize))

    # Merge clips into single track
    contentOverlay = concatenate_videoclips(clips).set_position(("center", "center"))

    # Compose background/foreground
    # final = CompositeVideoClip(
    #     clips=[backgroundVideo, contentOverlay], 
    #     size=backgroundVideo.size).set_audio(contentOverlay.audio)
    final = CompositeVideoClip(
        clips=[backgroundVideo, contentOverlay], 
        size=backgroundVideo.size).set_audio(contentOverlay.audio.set_duration(voiceover_duration))

    final.duration = script.getDuration()
    final.set_fps(backgroundVideo.fps)

    # Write output to file
    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"{outputDir}/{fileName}.mp4" #FILENAME###############
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
    video_description = "We dive into some of the funniest and most outrageous questions and answers from the popular AskReddit forum. Join us as we explore the weird and wonderful world of Reddit, with entertaining and meme-worthy moments guaranteed"
    video_tags = ["Reddit", "AskReddit", "AMA", "Entertainment", "Comedy", "Humor", "Memes", "Funny", "Laugh", "Viral"]
    video_category_id = "22"  # Entertainment category

    upload_video(outputFile, video_title, video_description, video_tags, video_category_id)

if __name__ == "__main__":
    createVideo()