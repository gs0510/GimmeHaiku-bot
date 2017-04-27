import praw

r = praw.Reddit('Comment Scraper 1.0 by u/_Daimon_ see '
                'https://praw.readthedocs.org/en/latest/'
                'pages/comment_parsing.html')
r.login('lumos510', '051095gs')
submission = r.get_submission(submission_id='11v36o')
flat_comments = praw.helpers.flatten_tree(submission.comments)
already_done = set()
for comment in flat_comments:
    if comment.body == "Hello" and comment.id not in already_done:
        #comment.reply(' world!')
        already_done.add(comment.id)