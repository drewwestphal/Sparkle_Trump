import random

from os.path import join, dirname

def load_emojis(filename):
    return [line.strip() for line in open(filename, encoding="utf-8") if len(line.strip())>0 and not line.strip().startswith('#')]

class SparkleTrump(object):
    SPARKLES = load_emojis(join(dirname(__file__), 'sparkles.txt'))
    NIGHTCAPS = load_emojis(join(dirname(__file__), 'nightcaps.txt'))
    TWEET_LEN = 140
    MIN_SPACE = 7
	
def interpolate_single_sparkle(sparkle_source, string, index, limit_chars=-1):
    if limit_chars > -1:
        sparkle_source = [sparkle for sparkle in sparkle_source if len(sparkle) <= limit_chars]

    # if there are no sparkles that meet our criteria, just return the original
    return string if not sparkle_source else string[:index]+random.choice(sparkle_source)+string[index:]


def interpolate_sparkles(sparkle_source, string, index, n_sparkles, limit_chars=-1):
    free_space = limit_chars if limit_chars>-1 else 100*n_sparkles
    max_len = len(string) + free_space

    for remaining_sparkles in reversed(range(0, n_sparkles)):
        char_limit_this_choice = max(0,max_len-len(string)-remaining_sparkles)
        string = interpolate_single_sparkle(sparkle_source, string, index, char_limit_this_choice)
        
    return string


def sparkles_for_spaces(sparkle_source, text, n_sparkles_per_space, maximum_returned_length):
    words = text.split()
    text = ''.join(words)
    word_spaces = [0]
    for word in words:
        word_spaces.append(word_spaces[-1] + len(word))

    for rem_spaces, space_idx in reversed(list(enumerate(word_spaces))):
        text = interpolate_sparkles(sparkle_source, text, space_idx, n_sparkles_per_space, maximum_returned_length - len(text) - rem_spaces * n_sparkles_per_space)

    return text