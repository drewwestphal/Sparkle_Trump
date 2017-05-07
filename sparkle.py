import twitter
import os
from os.path import join, dirname
from dotenv import load_dotenv
import random
import re

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


MIN_EMOJIS = 25
TWEET_LEN = 140
EMOJI_REGEX = r"/[\u263a-\U0001f645]/"
LINK_REGEX = r"/(\S+\.(com|net|org|edu|gov|co)(\/\S+)?)"




def load_emojis(filename):
    emojis = ''
    for line in open(filename):
        line = ''.join(line.split())
        if not line.startswith('#'):
            emojis += line
    return emojis


sparkles = load_emojis('./sparkles.txt')
nightcaps = load_emojis('./nightcaps.txt')

def random_sparkles(n):
    return ''.join([random.choice(sparkles) for number in range(0, n)])

def random_nightcap(n):
    return ''.join([random.choice(nightcaps) for number in range(0, n)])


def dmac_space_sparkles(text, max_sparkles_in_a_space=99, pad_ending=True, include_nightcap=False, nightcap_chars=2):
    words = text.split()
    unfree_chars = 0
    for word in words:
        unfree_chars += len(word)

    sparkly_nightcap = "\n\n"+random_nightcap(nightcap_chars)
    if include_nightcap:
        unfree_chars += len(sparkly_nightcap)

    free_chars = TWEET_LEN-unfree_chars;
    spaces_for_emojis = len(words)+1
    emoji_in_each_space = min(free_chars//spaces_for_emojis, max_sparkles_in_a_space)

    sparkled_tweet = random_sparkles(emoji_in_each_space)
    for word in words:
        sparkled_tweet += word + random_sparkles(emoji_in_each_space)

    if pad_ending:
        sparkled_tweet += random_sparkles(TWEET_LEN-len(sparkled_tweet)-(len(sparkly_nightcap) if include_nightcap else  0))

    if include_nightcap and len(sparkled_tweet) <=   TWEET_LEN-len(sparkly_nightcap):
        return sparkled_tweet+sparkly_nightcap

    return sparkled_tweet

def aki_scattershot(text):
    sparkle_idx_probability = .66
    num_sparkles = min(TWEET_LEN-len(text), sparkle_idx_probability*len(text))
    sparkle_idx_probability = num_sparkles/len(text)

    sparkled_tweet_phase_0 = ''
    for word in text.split():
        sparkled_tweet_phase_0 += word
        sparkled_tweet_phase_0 += random_sparkles(1)

    sparkled_tweet_phase_1 = ''
    sparkles_used = 0
    for i in range(0, len(sparkled_tweet_phase_0)):
        if len(sparkled_tweet_phase_1) < TWEET_LEN:
            if sparkles_used < num_sparkles and random.uniform(0, 1) <= sparkle_idx_probability:
                sparkled_tweet_phase_1 += random_sparkles(1)

            sparkled_tweet_phase_1 += sparkled_tweet_phase_0[i]


    return sparkled_tweet_phase_1

#print(random_sparkles(2))
#print(random_nightcap(2))

#print("\n\n"+dmac_space_sparkles(test_text,3)+"\n\n")
#print("\n\n"+dmac_space_sparkles(test_text,3,True,True,2)+"\n\n")
#print("\n\n"+aki_scattershot(test_text)+"\n\n")

#print(sparkles)
#print(len(sparkles))
#print(random.choice(sparkles))

def communal_fmt_choice(text):
    return dmac_space_sparkles(text, 3, True, True, 2)


def comparable_form(text):
    return re.sub(r"\W", "", re.sub(LINK_REGEX, "", re.sub(EMOJI_REGEX, "", text)))

read_api = twitter.Api(consumer_key=os.environ['READ_CONSUMER_KEY'],
                      consumer_secret=os.environ['READ_CONSUMER_SECRET'],
                      access_token_key=os.environ['READ_ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['READ_ACCESS_TOKEN_SECRET'])

write_api = twitter.Api(consumer_key=os.environ['WRITE_CONSUMER_KEY'],
                      consumer_secret=os.environ['WRITE_CONSUMER_SECRET'],
                      access_token_key=os.environ['WRITE_ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['WRITE_ACCESS_TOKEN_SECRET'])


# texts that have headroom for at least MIN_EMOJIS
texts_to_sparkle_up = [tweet.text for tweet
                       in read_api.GetUserTimeline(screen_name="realDonaldTrump", count=200)
                       if len(tweet.text) <= (TWEET_LEN - MIN_EMOJIS)]

extant_tweet_corpus_texts = [tweet.text for tweet
                       in write_api.GetUserTimeline(count=200)]

untweeted_sparkleable_texts = [text for text in texts_to_sparkle_up if
                               comparable_form(text) not in [comparable_form(ext) for ext in extant_tweet_corpus_texts]]

if len(untweeted_sparkleable_texts):
    target = untweeted_sparkleable_texts[-1]
    write_api.PostUpdate(communal_fmt_choice(target))

