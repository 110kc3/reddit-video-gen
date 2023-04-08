# script that renames all files in a given directory to "ShortTemplate_N", where N is a sequential number starting from 0:

import os

# Directory containing the videos to be renamed
directory = "C:/repos/reddit-video-gen/BackgroundVideos/"

# Get all the video files in the directory
video_files = [f for f in os.listdir(directory) if f.endswith(".mp4")]

# Sort the video files in alphabetical order
video_files.sort()

# Rename each video file to ShortTemplate_N.mp4
for i, filename in enumerate(video_files):
    new_filename = "ShortTemplate_{:d}.mp4".format(i)
    os.rename(directory + filename, directory + new_filename)
