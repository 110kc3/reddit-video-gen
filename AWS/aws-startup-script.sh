#!/bin/bash

# Install git, pip, and awscli
sudo apt-get update
sudo apt-get install -y git python3-pip
sudo pip3 install awscli

# Create a 3GB swap file
sudo dd if=/dev/zero of=/swapfile bs=1M count=3072
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add the swap file to /etc/fstab for persistence
echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab

# Clone the repository into the /home/ubuntu directory
sudo git clone https://github.com/110kc3/reddit-video-gen /home/ubuntu/reddit-video-gen

# Change ownership to the ubuntu user
sudo chown -R ubuntu:ubuntu /home/ubuntu/reddit-video-gen

# Install Python requirements
sudo pip3 install -r /home/ubuntu/reddit-video-gen/requirements.txt

# Configure AWS CLI
aws configure

# Sync files from S3 bucket to /home/ubuntu directory
aws s3 sync s3://code-temp-internetstories /home/ubuntu/reddit-video-gen

# create the logs directory and the app.log file
mkdir -p /home/ubuntu/reddit-video-gen/logs
touch /home/ubuntu/logs/reddit-video-gen/app.log
touch /home/ubuntu/logs/reddit-video-gen/env.log


# Add crontab entry for your script
(sudo crontab -u ubuntu -l; echo "20 */8 * * * cd /home/ubuntu/reddit-video-gen && ./run.sh >> /home/ubuntu/reddit-video-gen/logs/app.log 2>&1") | sudo crontab -u ubuntu -
