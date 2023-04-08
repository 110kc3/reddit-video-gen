from createVideo import createVideo

def main():
    num_videos = 1  # Change this value to the number of videos you want to create

    for i in range(num_videos):
        try:
            createVideo()
            print(f"Video {i + 1} created successfully.")
        except Exception as e:
            print(f"An error occurred while creating video {i + 1}: {e}")

if __name__ == "__main__":
    main()

