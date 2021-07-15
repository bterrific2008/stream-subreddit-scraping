import praw
from praw.models.reddit.submission import Submission
from praw.models.reddit.comment import Comment
from praw.models.reddit.subreddit import Subreddit

import os
from datetime import datetime
import pytz

CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
USER_AGENT = os.environ['REDDIT_USER_AGENT']

TARGET_SUBREDDIT = os.environ['REDDIT_TARGET_SUBREDDIT']
SCRAPE_POST_COUNT = int(os.environ['REDDIT_SCRAPE_POST_COUNT'])
SCRAPE_COMMENT_COUNT = int(os.environ['REDDIT_SCRAPE_COMMENT_COUNT'])

def main():


    subreddit: Subreddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
    ).subreddit(TARGET_SUBREDDIT)

    new_posts = subreddit.new(limit=SCRAPE_POST_COUNT)
    post: Submission
    for post in new_posts:
        print(post.title, post.created_utc)

    new_comments = subreddit.comments(limit=SCRAPE_COMMENT_COUNT)
    comment: Comment
    for comment in new_comments:
        print(comment.author, comment.body[:50], comment.created_utc)

if __name__ == '__main__':
    main()