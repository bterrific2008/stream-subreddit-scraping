import os
from datetime import datetime

import praw
import pymongo
import pytz
from praw.models.reddit.comment import Comment
from praw.models.reddit.submission import Submission
from praw.models.reddit.subreddit import Subreddit

from wrappers.wrappers import SubmissionCollections, CommentCollections

CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
USER_AGENT = os.environ["REDDIT_USER_AGENT"]

TARGET_SUBREDDIT = os.environ["REDDIT_TARGET_SUBREDDIT"]
SCRAPE_POST_COUNT = int(os.environ["REDDIT_SCRAPE_POST_COUNT"])
SCRAPE_COMMENT_COUNT = int(os.environ["REDDIT_SCRAPE_COMMENT_COUNT"])

MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = int(os.environ["MONGO_PORT"])
DATABASE_NAME = os.environ["MONGO_DB_NAME"]
POST_COLLECTION_NAME = os.environ["POST_COLLECTION_NAME"]
COMMENT_COLLECTION_NAME = os.environ["COMMENT_COLLECTION_NAME"]


def convert_post_to_document(post: Submission):
    post_doc = {
        "_id": post.id,
        "title": post.title,
        "author": {"id": post.author.id, "name": post.author.name},
        "subreddit": post.subreddit.display_name,
        "text": post.selftext,
        "date": datetime.datetime.fromtimestamp(post.created),
    }

    return post_doc


def main():

    mongodb = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    collection = mongodb[DATABASE_NAME][POST_COLLECTION_NAME]
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    subreddit: Subreddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
    ).subreddit(TARGET_SUBREDDIT)

    post_collection = SubmissionCollections(collection=collection, reddit=reddit)
    comment_collection = CommentCollections(collection=collection, reddit=reddit)

    new_posts = subreddit.new(limit=SCRAPE_POST_COUNT)
    post: Submission
    for post in new_posts:
        post_collection.insert_one(post)

    new_comments = subreddit.comments(limit=SCRAPE_COMMENT_COUNT)
    comment: Comment
    for comment in new_comments:
        comment_collection.insert_one(comment)


if __name__ == "__main__":
    main()
