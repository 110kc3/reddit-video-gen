# Reddit Video Generator

This program generates a .mp4 video automatically by querying the top post on the
r/askreddit subreddit, and grabbing several comments. To use this program:
- [ ] Install dependencies
- [ ] Register with Reddit to create and API application [here](https://www.reddit.com/prefs/apps/)
- [ ] Use the credentials from the previous step to update reddit.py line 46-51
- [ ] Make a copy of config.example.ini and rename to config.ini

Now, you can run `python main.py` to be prompted for which post to choose. Alternatively,
you can run `python main.py <reddit-post-id>` to create a video for a specific post.



YT authentication:

python authorize_youtube.py

This will open a new browser window asking you to authorize the application. Once you do that, it will create an authorized_user.json file containing the necessary fields (refresh_token, client_id, client_secret).


TODO:

change structure of the files

implement auto yt upload

check how to move to linux vm - headless setup


auto tiktok upload

