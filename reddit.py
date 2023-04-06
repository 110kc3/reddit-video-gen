import os, re, praw, markdown_to_text, time
from videoscript import VideoScript
import random

redditUrl = "https://www.reddit.com/"

def getContent(outputDir, postOptionCount) -> VideoScript:
    reddit = __getReddit()
    existingPostIds = __getExistingPostIds(outputDir)

    now = int( time.time() )
    autoSelect = postOptionCount == 0
    posts = []

    for submission in reddit.subreddit("askreddit").top(time_filter="month", limit=postOptionCount*3):
        if (f"{submission.id}.mp4" in existingPostIds or submission.over_18):
            continue
        hoursAgoPosted = (now - submission.created_utc) / 3600
        print(f"[{len(posts)}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
        posts.append(submission)
        if (autoSelect or len(posts) >= postOptionCount):
            break

    if (autoSelect):
        return __getContentFromPost(posts[0])
    else:
        postSelection = int(input("Input :"))
        selectedPost = posts[postSelection]
        return __getContentFromPost(selectedPost)


def getContentFromId(outputDir, submissionId) -> VideoScript:
    reddit = __getReddit()
    existingPostIds = __getExistingPostIds(outputDir)
    print(existingPostIds)
    
    if (submissionId in existingPostIds):
        print("Video already exists!")
        exit()
    try:
        submission = reddit.submission(submissionId)
    except:
        print(f"Submission with id '{submissionId}' not found!")
        exit()
    return __getContentFromPost(submission)

def __getReddit():
    return praw.Reddit(
        client_id="3392eYFbN73bpfEDZ-1ATA",
        client_secret="XVXfwp52AksHp1PfvvWeUpQ-MeaCxQ",
        # user_agent sounds scary, but it's just a string to identify what your using it for
        # It's common courtesy to use something like <platform>:<name>:<version> by <your name>
        # ex. "Window11:TestApp:v0.1 by u/Shifty-The-Dev"
        user_agent="Window10:CommentFetcher:v0.1 by u/Speedi1103"
    )


def __getContentFromPost(submission) -> VideoScript:
    content = VideoScript(submission.url, submission.title, submission.id)
    print(f"Creating video for post: {submission.title}")
    print(f"Url: {submission.url}")

    failedAttempts = 0
    for comment in submission.comments:
        if(content.addCommentScene(markdown_to_text.markdown_to_text(comment.body), comment.id)):
            failedAttempts += 1
        if (content.canQuickFinish() or (failedAttempts > 2 and content.canBeFinished())):
            break
    return content

# function retrieves a list of existing post IDs from the outputDir (output directory) where the videos are stored
def __getExistingPostIds(outputDir):
    files = os.listdir(outputDir)
    # I'm sure anyone knowledgable on python hates this. I had some weird 
    # issues and frankly didn't care to troubleshoot. It works though...
    files = [f for f in files if os.path.isfile(outputDir+'/'+f)]
    return [re.sub(r'.*?-', '', file) for file in files]
