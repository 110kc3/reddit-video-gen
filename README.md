## Note: with new chages of reddit API this is now unmaintained


# Reddit Video Generator

Reddit Video Generator is a Python-based project that creates videos from top Reddit posts and their comments. The project uses Selenium WebDriver for taking screenshots of the posts, moviepy for video editing, and text-to-speech for generating audio from the post titles and comments.

It is based on https://github.com/Shifty-The-Dev/RedditVideoGenerator project, hovewer with few improvments.

Channel for the videos is https://youtube.com/@InternetStories69
Also replicated some for tiktok https://www.tiktok.com/@internetstoriesguru


## Getting Started

These instructions will help you set up the project on your local machine for development and usage purposes.*** not finished

### Prerequisites

### For local usage
(currently local usage is not working, hovewer below are still needed for cloud application to work)
1. Register with Reddit to create and Script API application [here](https://www.reddit.com/prefs/apps/) and fill your secrets in Secrets/reddit_secrets.py
2. Youtube account
3. GCP account on the same email as Youtube account with enabled [YouTube Data API](https://developers.google.com/youtube/v3)
You will need to create YouTube app on GCP and then authenticate to it... you will also need client_secrets_desktop.json in order to even connect to GCP from your account.
4. AWS account* (this is needed for the voiceover voice I used, you could swap if for something else, but I found the Joanna voice to be the best for these type of videos)

### Additional for cloud usage and complete automation
4. AWS account: 
- currently the code uses AWS buckets for all files handling, thus you will need to create couple of buckets on AWS. 
The script was tested on 1CPU-1GB Ubuntu VM, it can take up to an hour for a video to be generated.
(you could use diferent provider, but aws is free on that vm)


### AWS: Set up the buckets

1. Create buckets and update their name in config.ini

BackgroundVideosBucket: Bucket that will keep background videos that will be used in background of the created videos (duh)
Important to note that videos need to be already in vertical format. Used videos will be deleted from this bucket so this needs to be filled up after running the script few times.
ADD your background videos into it.

UsedBackgroundVideosBucket:
This is additional bucket for background videos if the ones in previous bucket will be empty, this one is not cleared after background video is used.

OutputVideosBucket:
If the video will not be uploaded to youtube it will be sent to this bucket.

YoutubeOutputVideosBucket: 
If the video will be uploaded to youtube it will be sent to this bucket. (the idea was then to implement tiktok and facebook replication, without the need to create videos again - this was not implemented)

IDsOfCreatedVideosBucket:
If the video will be uploaded to youtube this bucket will receive .txt file with tittle, id, description and tags of the uploaded video. Script first checks this bucket for already created videos and exludes it from the pool of the videos that it's able to create.

Another bucket, not in config.ini:
- Upload your secrets to SECRETS-BUCKET (yes I know this is bad practise, seemed cheaper than to use secret manager)

Bucket will need to contain 2 files, already in a folder:
Secrets/aws_secrets.py
AWS_ACCESS_KEY_ID = 
AWS_SECRET_ACCESS_KEY = 

Secrets/reddit_secrets.py
reddit_client_id=""
reddit_client_secret=""
reddit_user_agent="Windows10:Shittyapp:v0.1 by u/you"


## AWS: Create IAM user with permissions to buckets and Amazon polly

1. Sign in to the AWS Management Console and open the IAM console at https://console.aws.amazon.com/iam/.
2. In the navigation pane, choose "Users".
3. Find the user whose credentials you're using in your code and click on their name.
4. Click the "Add permissions" button.

Add below policies to this user: (one is for voiceovers, another for bucket access)

AmazonPollyFullAccess 

and create new policy and assign it to the user, 
sample policy I used is in AWS/aws-iam-user-policy.json file

Add his access key credentials to Secrets/aws_secrets.py

### GCP: Autorize application to use youtube

Next you have to 

https://developers.google.com/youtube/v3/guides/authentication

On test setup you can use authorize_youtube.py

on headless setup use authorize_youtube_headless.py

It completes the OAuth 2.0 authentication flow, with the use the flow.run_console() method to authenticate with the Google API using a code that you obtain from the Google Cloud Console.

..........

### Installation

AWS:
1. Create IAM Role that will Allow EC2 instances to call AWS services on your behalf, give it the same permissions as the user above
2. Create EC2 instance (Ubuntu 22)
I used Canonical, Ubuntu, 22.04 LTS on eu-central-1 - ami-0ec7f9846da6b0f61
- assign IAM user with required permissions to it
- add startup script to the vm (AWS/aws-startup-script.sh)

2. SSH to vm, authorize your youtube account to use this app
cd /home/ubuntu/reddit-video-gen
python 
............. add credentials from GCP 
....
TODO
# Add crontab entry for your script
(sudo crontab -u ubuntu -l; echo "20 */8 * * * cd /home/ubuntu/reddit-video-gen && ./run.sh >> /home/ubuntu/reddit-video-gen/logs/app.log 2>&1") | sudo crontab -u ubuntu -

.........

Usage
Edit the config.ini file to set the desired parameters for your video, such as the Reddit API credentials, video settings, and output directory.

Run the main.py script to be prompted for which post to choose.
python main.py

Alternatively, you can run `python main.py <reddit-post-id>` to create a video for a specific post.




######



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









AWS linux vm: (when code is in bucket - TODO change)


Install the AWS CLI tool on your Ubuntu VM. You can do this by running the following command:

sudo apt-get update && sudo apt-get install awscli -y
Once the AWS CLI tool is installed, you need to configure it with your AWS credentials. You can do this by running the following command and following the prompts:

aws configure

NOTE: (better to use IAM roles) IAM roles: You can assign an IAM role to the instance when launching it. The IAM role should have the necessary permissions to access the S3 bucket. The AWS CLI and SDKs can automatically retrieve the credentials from the instance metadata service, so you don't need to provide credentials explicitly.

After the CLI tool is configured, you can use the following command to sync all the files from the S3 bucket to a local directory on your Ubuntu VM:
aws s3 sync s3://code-temp-internetstories .


sudo apt install python3-pip


.....











#
After competing setup for youtube auto upload you can then replicate incoming videos from YT to other platforms.
I wanted to do this via code, however it looks like to much work.

I found below tool that replicates all your youtube videos to other platforms.

It has 14 day trial, after that there is billing per month.

If you wish to use it, consider using my referal link: https://repurpose.io/?aff=107387






#######






Broken
FIX:
verify if the background video file is in correct format
when video is not vertical - also handle proper screenshot scaling
 code only will work when video is in vertical format - no idea how to fix it



TODO:

FIX:
Selenium - how to block popups (screenshot taking is not working every time)

test if the background video is long
...

Proper error handling

there is an issue if the 2nd bucket fo background video is selected TODO

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


