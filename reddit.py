import os, re, praw, markdown_to_text, time
from videoscript import VideoScript
import random

redditUrl = "https://www.reddit.com/"

# def getContent(outputDir, postOptionCount) -> VideoScript:
#     reddit = __getReddit()
#     existingPostIds = __getExistingPostIds(outputDir)

#     now = int( time.time() )
#     autoSelect = postOptionCount == 0
#     posts = []

#     for submission in reddit.subreddit("askreddit").top(time_filter="week", limit=postOptionCount*3):
#         if (f"{submission.id}.mp4" in existingPostIds or submission.over_18):
#             continue
#         hoursAgoPosted = (now - submission.created_utc) / 3600
#         print(f"[{len(posts)}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
#         posts.append(submission)
#         if (autoSelect or len(posts) >= postOptionCount):
#             break

#     if (autoSelect):
#         return __getContentFromPost(posts[0])
#     else:
#         postSelection = int(input("Input :"))
#         selectedPost = posts[postSelection]
#         return __getContentFromPost(selectedPost)


#  old for getting posts
# def getContent(outputDir, postOptionCount, auto_select, subreddit_name, time_filter) -> VideoScript:
#     reddit = __getReddit()
#     existingPostIds = __getExistingPostIds(outputDir)

#     now = int(time.time())
#     autoSelect = auto_select or postOptionCount == 0

#     posts = []

#     for submission in reddit.subreddit(subreddit_name).top(time_filter=time_filter, limit=postOptionCount * 3):
#         if (f"{submission.id}.mp4" in existingPostIds or submission.over_18):
#             continue
#         hoursAgoPosted = (now - submission.created_utc) / 3600
#         print(f"[{len(posts)}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
#         posts.append(submission)


def getContent(outputDir, postOptionCount, auto_select, subreddit_name, time_filter) -> VideoScript:
    reddit = __getReddit()
    existingPostIds = __getExistingPostIds(outputDir)

    now = int(time.time())
    autoSelect = auto_select or postOptionCount == 0

    posts = []
    fetched_posts = []
    while len(posts) < postOptionCount:
        for submission in reddit.subreddit(subreddit_name).top(time_filter=time_filter, limit=postOptionCount * 3, params={"after": fetched_posts[-1].fullname if fetched_posts else None}):
            fetched_posts.append(submission)
            if (f"{submission.id}.mp4" in existingPostIds or submission.over_18):
                continue
            hoursAgoPosted = (now - submission.created_utc) / 3600
            print(f"[{len(posts)}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
            posts.append(submission)
            if len(posts) >= postOptionCount:
                break

    available_posts = [post for post in posts if post.id not in existingPostIds]

    if not available_posts:
        print("No available posts found!")
        exit()

    if autoSelect:
        selectedPost = available_posts[0]
    else:
        while True:
            postSelection = int(input("Input :"))
            if postSelection < len(posts) and posts[postSelection].id not in existingPostIds:
                selectedPost = posts[postSelection]
                break
            else:
                print("Invalid selection or video already exists. Please try again.")

    return __getContentFromPost(selectedPost)







def getContentFromId(outputDir, submissionId) -> VideoScript:
    reddit = __getReddit()
    # print("getting existing posts ids:")
    existingPostIds = __getExistingPostIds(outputDir)
    # print(existingPostIds)

    # print("printing submissions IDs")
    # print(submissionId)
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

    files = [f for f in files if os.path.isfile(os.path.join(outputDir, f))]
    post_ids = [re.sub(r'.*?-', '', file) for file in files]
    post_ids_without_ext = [os.path.splitext(post_id)[0] for post_id in post_ids] # returning the post IDs with the '.mp4' extension
    return post_ids_without_ext

