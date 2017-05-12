import twitter
import os
from os.path import join, dirname
from dotenv import load_dotenv
import random
import re
import html
from sparkle_func import *


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


EMOJI_REGEX = r'[^\x00-\x7F]'
LINK_REGEX = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'




def dmac_space_sparkles(text, max_sparkles_in_a_space=99, pad_ending=True, include_nightcap=False, nightcap_chars=2):
    nightcap = ''
    if include_nightcap: 
        nightcap = "\n\n"
        nightcap = interpolate_sparkles(SparkleTrump.NIGHTCAPS, nightcap, len(nightcap), 2, SparkleTrump.TWEET_LEN-len(text)-len(nightcap))

    emoji_in_each_space = min((SparkleTrump.TWEET_LEN-sum([len(word) for word in text.split()])-len(nightcap))//len(text.split()), max_sparkles_in_a_space)

    text = sparkles_for_spaces(SparkleTrump.SPARKLES, text, emoji_in_each_space, SparkleTrump.TWEET_LEN - len(nightcap))+nightcap

    if pad_ending:
        text = interpolate_sparkles(SparkleTrump.SPARKLES, text, len(text)-len(nightcap), SparkleTrump.TWEET_LEN, SparkleTrump.TWEET_LEN-len(text))

    return text

def aki_scattershot(text):
    text = sparkles_for_spaces(SparkleTrump.SPARKLES, text, 1, SparkleTrump.TWEET_LEN)

    sparkle_idx_probability = .66
    num_sparkles = int(min(SparkleTrump.TWEET_LEN-len(text), sparkle_idx_probability*len(text)))
    sparkle_idx_probability = num_sparkles/len(text)

    for index in reversed(range(0, len(text))):
        if random.uniform(0, 1) <= sparkle_idx_probability:
            print(index)
            text = interpolate_single_sparkle(SparkleTrump.SPARKLES, text, index, SparkleTrump.TWEET_LEN - len(text))

    return text

#print(random_sparkles(2))
#print(random_nightcap(2))

#test_text = "We finally agree on something Rosie."

#print("\n\n"+dmac_space_sparkles(test_text,3)+"\n\n")
#print("\n\n"+dmac_space_sparkles(test_text,3,True,True,2)+"\n\n")
#print("\n\n"+aki_scattershot(test_text)+"\n\n")
#print(communal_fmt_choice(test_text))

#print(sparkles)
#print(len(sparkles))
#print(random.choice(sparkles))

def communal_fmt_choice(text):
    return dmac_space_sparkles(text, 3, True, True, 2)


def comparable_form(text, debug_pfx=False, debug=False):
    replace_emoji = re.sub(EMOJI_REGEX, " ", text.lower())
    replace_links = re.sub(LINK_REGEX, "", replace_emoji)
    replace_nonws = re.sub(r"\W", "", replace_links)

    if debug_pfx and debug:
        print('['+debug_pfx+'a]'+text)
        print('['+debug_pfx+'0]'+replace_emoji)
        print('[' + debug_pfx + '1]' + replace_links)
        print('[' + debug_pfx + '2]' + replace_nonws)
    return replace_nonws

read_api = twitter.Api(consumer_key=os.environ['READ_CONSUMER_KEY'],
                      consumer_secret=os.environ['READ_CONSUMER_SECRET'],
                      access_token_key=os.environ['READ_ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['READ_ACCESS_TOKEN_SECRET'])

write_api = twitter.Api(consumer_key=os.environ['WRITE_CONSUMER_KEY'],
                      consumer_secret=os.environ['WRITE_CONSUMER_SECRET'],
                      access_token_key=os.environ['WRITE_ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['WRITE_ACCESS_TOKEN_SECRET'])


# texts that have headroom for at least MIN_EMOJIS
texts_to_sparkle_up = [html.unescape(tweet.text) for tweet
                       in read_api.GetUserTimeline(screen_name="realDonaldTrump", count=200)
                       if len(tweet.text) <= (SparkleTrump.TWEET_LEN - SparkleTrump.MIN_SPACE)]

extant_tweet_corpus_texts = [html.unescape(tweet.text) for tweet
                             in write_api.GetUserTimeline(count=200)]

comparable_corpus = [comparable_form(ext,"corp") for ext in extant_tweet_corpus_texts]
untweeted_sparkleable_texts = [text for text in texts_to_sparkle_up if
                               comparable_form(text, "orig") not in comparable_corpus]

if len(untweeted_sparkleable_texts):
    target = untweeted_sparkleable_texts[-1]
    write_api.PostUpdate(communal_fmt_choice(target))

