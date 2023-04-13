# Reddit Video Generator

Reddit Video Generator is a Python-based project that creates videos from top Reddit posts and their comments. 
The project uses Selenium WebDriver for taking screenshots of the posts, 
moviepy for video editing, and text-to-speech for generating audio from the post titles and comments.

## Getting Started

These instructions will help you set up the project on your local machine for development and usage purposes.

### Prerequisites

1. Python 3.x
2. pip

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/reddit-video-generator.git
cd reddit-video-generator
```

bash
Copy code
# Reddit Video Generator

Reddit Video Generator is a Python-based project that creates videos from top Reddit posts and their comments. The project uses Selenium WebDriver for taking screenshots of the posts, moviepy for video editing, and text-to-speech for generating audio from the post titles and comments.

## Getting Started

These instructions will help you set up the project on your local machine for development and usage purposes.

### Prerequisites

1. Python 3.x
2. pip

### Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/reddit-video-generator.git
cd reddit-video-generator
```
Create a virtual environment and activate it:

python3 -m venv venv
source venv/bin/activate
Install the required dependencies:

pip install -r requirements.txt
Install the required browser and WebDriver. In this example, we will use Firefox and geckodriver:

sudo apt-get install firefox
wget https://github.com/mozilla/geckodriver/releases/download/vX.Y.Z/geckodriver-vX.Y.Z-linux64.tar.gz
tar -xvzf geckodriver-vX.Y.Z-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
Make sure to replace vX.Y.Z with the appropriate version number for geckodriver.

Usage
Edit the config.ini file to set the desired parameters for your video, such as the Reddit API credentials, video settings, and output directory.

Run the main.py script to be prompted for which post to choose.
python main.py

Alternatively, you can run `python main.py <reddit-post-id>` to create a video for a specific post.


## Hosting

If you will be using aws free tier vm for hosting you will need to create swapfile for better memory management as program can fail on only 1gb of ram.

This script will create the swap file, make it persistent, and add the crontab entry (entry can be modificated) for the run.sh script. Make sure to replace the ubuntu user with the appropriate user if needed.


```
#!/bin/bash
# Create a 3GB swap file (change the count to adjust the size)
sudo dd if=/dev/zero of=/swapfile bs=1M count=3072
# Set the appropriate permissions for the swap file
sudo chmod 600 /swapfile
# Set up the swap area
sudo mkswap /swapfile
# Enable the swap file
sudo swapon /swapfile

# Add the swap file to /etc/fstab for persistence
echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab

# Add crontab entry for your script
(sudo crontab -u ubuntu -l; echo "20 */8 * * * cd /home/ubuntu && ./run.sh >> /home/ubuntu/logs/app.log 2>&1") | sudo crontab -u ubuntu -

```




######
Secrets:

Register with Reddit to create and API application [here](https://www.reddit.com/prefs/apps/)





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


Next you have to authorize your youtube account

On test setup you can use authorize_youtube.py

on headless setup use authorize_youtube_headless.py

It completes the OAuth 2.0 authentication flow, with the use the flow.run_console() method to authenticate with the Google API using a code that you obtain from the Google Cloud Console.





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


