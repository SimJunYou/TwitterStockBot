from config import TW_KEY_SET, USERS, tele_queue, job_queue
import twitter
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class TwitterBot:
    def __init__(self):
        self.api = twitter.Api(consumer_key=TW_KEY_SET[0],
                               consumer_secret=TW_KEY_SET[1],
                               access_token_key=TW_KEY_SET[2],
                               access_token_secret=TW_KEY_SET[3])
        self.users = self.convert_name_to_id(USERS)  # users to follow
        logger.info("Twitter Bot initialised")

    def convert_name_to_id(self, names):
        id_list = []
        for each in names:
            user_obj = self.api.GetUser(screen_name=each)
            id_list.append(str(user_obj.id))
        return id_list

    def start_track_stream(self):
        for each_tweet in self.api.GetStreamFilter(follow=self.users):
            if 'user' not in each_tweet:
                continue
            if ("@" + each_tweet['user']['screen_name']) not in USERS:  # Added the @ to fit USERS format
                continue
            logger.info(f"Got a new tweet from: {'@' + each_tweet['user']['screen_name']}")
            if each_tweet['text'][0] == '@':  # If it's a reply, don't proceed
                logger.warn(f"Ignoring reply tweets. Text:\n{each_tweet['text']}")
                continue
            enqueue_tweet(each_tweet)

    def get_latest_tweets(self):
        logger.info("Scraping latest tweets from user list...")
        for eachId in self.users:
            # first, get a tweet from each user's timeline (it will be in a list)
            tweet = self.api.GetUserTimeline(user_id=int(eachId), count=1, include_rts=False, exclude_replies=True)
            if not tweet:
                continue
            enqueue_tweet(tweet[0].AsDict())

    def get_recommendations(self):
        logger.info("Scraping recommendations from user list...")
        for eachId in self.users:
            # first, get a list of 100 tweets from each user's timeline
            tweets = self.api.GetUserTimeline(user_id=int(eachId), count=100, include_rts=False, exclude_replies=True)
            if not tweets:
                continue
            for each_tweet in tweets:
                each_tweet = each_tweet.AsDict()
                if 'text' not in each_tweet:
                    continue
                # if the tweet says 'portfolio' or 'position' and contains >= 5 '$' indicating stock symbols,
                if 'portfolio' in each_tweet['text'] or 'position' in each_tweet['text']:
                    if each_tweet['text'].count('$') >= 5:
                        enqueue_tweet(each_tweet)


def enqueue_tweet(tweet: dict):
    logger.info(f"Queueing tweet from {tweet['user']['screen_name']}")
    print(tweet)
    tweet_str = format_tweet(tweet)
    tweet_items = [tweet_str]
    if tweet.get('media'):  # if there are pictures, add the URL to tweet_items behind the main text
        for eachMedia in tweet['media']:
            tweet_img = eachMedia['media_url']
            tweet_items.append(tweet_img)
    print(tweet)
    tele_queue.put(tweet_items)


def format_tweet(tweet: dict):
    screen_name = tweet['user']['screen_name']
    text = tweet['text']

    # the date format is 'Tue Dec 22 15:51:07 +0000 2020'
    created_at = tweet['created_at'].split(' ')  # split by spaces - third space is end of date
    created_at = ' '.join(created_at[:3])  # rejoin at 3 so that there's only the date i.e. 'Tue Dec 22'

    return f"@{screen_name} on {created_at}\n\n{text}"


# for debug only
if __name__ == "__main__":
    tw = TwitterBot()
    tw.get_recommendations()