import logging
from datetime import datetime

import praw
import pymongo
from praw import Reddit
from praw.models.reddit.comment import Comment
from praw.models.reddit.submission import Submission
from praw.models.reddit.subreddit import Subreddit
from pymongo.collection import Collection


class CollectionWrapper:
    def __init__(self, collection: Collection):
        self.collection: Collection = collection

    def insert_one(self, doc, doc_id):
        if not self.has_doc(doc_id):
            self.collection.insert_one(doc).inserted_id
            logging.info(f"Inserted {doc_id} inside of collection")
        else:
            logging.warning(f"Could not insert {doc_id} as it already exists")

    def find_doc(self, doc_id):
        return self.collection.find_one({"_id": doc_id})

    def has_doc(self, doc_id):
        return self.collection.count_documents({"_id": doc_id}, limit=1) > 0


class SubmissionCollections(CollectionWrapper):
    def __init__(self, collection: Collection, reddit: Reddit):
        super().__init__(collection)
        self.reddit = reddit

    def insert_one(self, post: Submission):
        doc = self.convert_to_document(post)
        super().insert_one(doc, doc_id=doc["_id"])

    def convert_to_document(self, post: Submission):
        doc = {
            "_id": post.id,
            "title": post.title,
            "author": {"id": post.author.id, "name": post.author.name},
            "subreddit": post.subreddit.display_name,
            "text": post.selftext,
            "date": datetime.fromtimestamp(post.created),
        }
        return doc

    def get_doc(self, doc_id):
        if not super().has_doc(doc_id):
            post = Submission(self.reddit, doc_id)
            doc = self.convert_to_document(post)
            super().insert_one(doc)
        return super().find_doc(doc_id)


class CommentCollections(CollectionWrapper):
    def __init__(self, collection: Collection, reddit: Reddit):
        super().__init__(collection)
        self.reddit = reddit

    def insert_one(self, comment: Comment):
        doc = self.convert_to_document(comment)
        super().insert_one(doc, doc_id=doc["_id"])

    def convert_to_document(self, comment):
        comment_doc = {
            "_id": comment.id,
            "text": comment.body,
            "author": {"id": comment.author.id, "name": comment.author.name},
            "post": {
                "id": comment.link_id,
            },
            "parent": {
                "id": comment.parent_id,
            },
            "subreddit": {
                "id": comment.subreddit_id,
            },
            "permalink": comment.permalink,
            "created": datetime.fromtimestamp(comment.created),
        }
        return comment_doc

    def get_doc(self, doc_id):
        if not super().has_doc(doc_id):
            post = Comment(self.reddit, doc_id)
            doc = self.convert_to_document(post)
            super().insert_one(doc)
        return super().find_doc(doc_id)
