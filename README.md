# Reddit Video Generator

This program generates a .mp4 video automatically by querying the top post on the
r/askreddit subreddit, and grabbing several comments. To use this program:
- [ ] Install dependencies
- [ ] Register with Reddit to create and API application [here](https://www.reddit.com/prefs/apps/)
- [ ] Use the credentials from the previous step to update reddit.py line 46-51
- [ ] Make a copy of config.example.ini and rename to config.ini

Now, you can run `python main.py` to be prompted for which post to choose. Alternatively,
you can run `python main.py <reddit-post-id>` to create a video for a specific post.




There are some issues with libraries:

fix:

python -m pip install -r requirements2.txt



YT authentication:

python authorize_youtube.py

This will open a new browser window asking you to authorize the application. Once you do that, it will create an authorized_user.json file containing the necessary fields (refresh_token, client_id, client_secret).




AWS user creation with user policy:
+ need to add AmazonPollyFullAccess policy

Sign in to the AWS Management Console and open the IAM console at https://console.aws.amazon.com/iam/.
In the navigation pane, click on "Policies" and then click the "Create policy" button.
In the "Create policy" page, click the "JSON" tab and replace the existing content with the sample policy provided above.
Click the "Review policy" button, give your policy a name (e.g., "S3VideoBucketAccess"), and click "Create policy".
In the navigation pane, click on "Users" and find your polly-script-bot user.
Click on the user name to open the user details page. In the "Permissions" tab, click on the "Add permissions" button and then click on "Attach existing policies directly".
In the search box, type the name of the policy you just created (e.g., "S3VideoBucketAccess") and select the checkbox next to it. Click on the "Attach policy" button to attach the policy to your polly-script-bot user.



IAM policy should look like this:


{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arm bucket name"
        }
    ]
}







TODO:


verify if the background video file is in correct format

auto facebook upload


check how to move to linux vm - headless setup

Finish opacity of screenshots

Create some process to choose/download background videos - maybe have ai choose specific video based on video title 

FUTURE TODO:

auto tiktok upload - kinda difficult - would need separate page deployed for authentication


DONE:

Fix check for created videos in bucket,
issues with the filenames creation 


Change storage of the files:
- move finished files to specific folder
- have all video files on S3 bucket

Fix videos from ID

Checking if the same video already exists


change structure of the files

implement automatic video chosing

add tags to video tittle, 

randomize video description and tags


