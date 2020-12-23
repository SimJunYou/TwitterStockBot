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
        for eachTweet in self.api.GetStreamFilter(follow=self.users):
            if 'user' not in eachTweet:
                continue
            if ("@" + eachTweet['user']['screen_name']) not in USERS:  # Added the @ to fit USERS format
                continue
            logger.info(f"Got a new tweet from: {'@' + eachTweet['user']['screen_name']}")
            if eachTweet['text'][0] == '@':  # If it's a reply, don't proceed
                logger.warn(f"Ignoring reply tweets. Text:\n{eachTweet['text']}")
                continue
            tweet_str = format_tweet(eachTweet)
            tele_queue.put([tweet_str])

    def get_latest_tweets(self):
        for eachId in self.users:
            # first, get a list of tweets from each user's timeline (only 1 tweet in this list)
            tweet = self.api.GetUserTimeline(user_id=int(eachId), count=1, include_rts=False, exclude_replies=True)
            if not tweet:
                continue
            tweet = tweet[0].AsDict()  # there should only be one tweet anyways, and convert it to a dict
            tweet_str = format_tweet(tweet)
            tweet_items = [tweet_str]
            if tweet.get('media'):
                for eachMedia in tweet['media']:
                    tweet_img = eachMedia['media_url']
                    tweet_items.append(tweet_img)
            print(tweet)
            tele_queue.put(tweet_items)


def format_tweet(tweet: dict):
    return f"@{tweet['user']['screen_name']} says...\n\n{tweet['text']}"


if __name__ == "__main__":
    tw = TwitterBot()
    tw.get_latest_tweets()
