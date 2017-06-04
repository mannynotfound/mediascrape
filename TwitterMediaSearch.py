# appropriated from
# https://github.com/dtuit/TwitterWebsiteSearch/blob/master/TwitterWebsiteSearch.py
import requests
from requests import Request, Session
from datetime import datetime, timezone
from time import sleep, time
import lxml
import lxml.html as lh
from urllib.parse import quote, urlsplit
import re
from operator import itemgetter

base_url = 'https://twitter.com/i/profiles/show/'

def search(user, max_position=None, session=None):
    media_url = base_url + user + '/media_timeline'
    params = {
            'include_available_features': '1',
            'include_entities': '1',
            'reset_error_state': 'false',
            }

    if max_position is not None:
        params['max_position'] = max_position
        params['last_note_ts'] = int(time())

    # Create Request
    request = prepare_request(media_url, params)

    # Execute Request
    result = execute_request(request, session)
    result_json = result.json()

    # Extract Results
    media = []
    if result_json is not None and result_json['items_html'] is not None:
        media = parse_media(result_json['items_html'])

    # Return Result
    return {
        '_request': request,
        '_result': result,
        '_result_json': result_json,
        'media': media
        }

def prepare_request(url, params):
    payload_str = "&".join("%s=%s" % (k,v) for k,v in params.items())
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/29.0.1547.65 Chrome/29.0.1547.65 Safari/537.36',
        'Accept-Encoding' : 'gzip, deflate, sdch, br'
        }
    cookie = {}
    req = Request('GET', url, params=payload_str, headers=headers, cookies=cookie)
    return req.prepare()

def execute_request(prepared_request, session=None):
    try:
        if session is None:
            session = Session()
        result = session.send(prepared_request)
        return result
    except requests.exceptions.Timeout as e:
        raise

def _parse_tweet(tweetElement):
    li = tweetElement
    tweet = {
        'created_at' : None,
        'id_str' : li.get('data-item-id'),
        'text' : None,
        'lang' : None,
        'entities': {
            'hashtags': [],
            'symbols':[],
            'user_mentions':[],
            'urls':[],
        },
        'user' : {
            'id_str' : None,
            'name' : None,
            'screen_name': None,
            'profile_image_url': None,
            'verified': False
            },
        'retweet_count' : 0,
        'favorite_count' : 0,
        'is_quote_status' : False,
        'in_reply_to_user_id': None,
        'in_reply_to_screen_name' : None,
        'contains_photo': False,
        'contains_video': False,
        'contains_card': False

    }

    content_div = li.cssselect('div.tweet')

    if len(content_div) > 0:
        content_div = content_div[0]
        tweet['user']['id_str'] = content_div.get('data-user-id')
        tweet['user']['name'] = content_div.get('data-name')
        tweet['user']['screen_name'] = content_div.get('data-screen-name')
    else:
        return None

    reply_a = content_div.cssselect('div.tweet-context a.js-user-profile-link')
    if len(reply_a) > 0:
        tweet['in_reply_to_user_id'] = reply_a[0].get('data-user-id')
        tweet['in_reply_to_screen_name'] = reply_a[0].get('href') # remove /

    user_img = content_div.cssselect('img.avatar')
    if len(user_img) > 0:
        tweet['user']['profile_image_url'] = user_img[0].get('src')

    text_p = content_div.cssselect('p.tweet-text')
    if len(text_p) > 0:
        text_p = text_p[0]
        tweet['text'] = text_p.text_content()
        tweet['lang'] = text_p.get('lang')

    verified_span = content_div.cssselect('span.Icon--verified')
    if len(verified_span) > 0:
        tweet['user']['verified'] = True

    date_span = content_div.cssselect('span._timestamp')
    if len(date_span) > 0:
        tweet['created_at'] = datetime.utcfromtimestamp(int(date_span[0].get('data-time-ms'))/1000).strftime('%Y-%m-%d %H:%M:%S')

    counts = li.cssselect('span.ProfileTweet-action--retweet, span.ProfileTweet-action--favorite')
    if len(counts) > 0:
        for c in counts:
            classes = c.get('class').split(' ')
            if 'ProfileTweet-action--retweet' in classes:
                tweet['retweet_count'] = c[0].get('data-tweet-stat-count')
            elif 'ProfileTweet-action--favorite' in classes:
                tweet['favorite_count'] = c[0].get('data-tweet-stat-count')

    entities = tweet['entities']
    _parse_tweet_entites(text_p, entities)

    tweet_media_context = content_div.cssselect('div.AdaptiveMedia-container')
    if len(tweet_media_context) > 0:
        tweet_media_context = tweet_media_context[0]
        tweet['entities']['media'] = []
        photo_found = False
        tweet_media_photos = tweet_media_context.cssselect('div.AdaptiveMedia-photoContainer')
        for elm in tweet_media_photos:
            tweet['contains_photo'] = photo_found = True
            photo = {
               'media_url' : elm.get('data-image-url'),
               'type' : 'photo'
            }
            tweet['entities']['media'].append(photo)
        if not photo_found:
            tweet_media_video = tweet_media_context.cssselect('div.AdaptiveMedia-videoContainer')
            if len(tweet_media_video) > 0:
                tweet['contains_video'] = True
                video = {
                    'type' : 'video',
                    'video_type' : re.search(re.compile(r"PlayableMedia--([a-zA-Z]*)"), tweet_media_video[0].cssselect('div[class*="PlayableMedia--"]')[0].get('class')).group(1),
                    'media_url' : 'https://twitter.com/i/videos/tweet/' + tweet['id_str'],
                    'video_thumbnail' : re.search(re.compile(r"background-image:url\(\'(.*)\'"),tweet_media_video[0].cssselect('div.PlayableMedia-player')[0].get('style')).group(1)
                }
                tweet['entities']['media'].append(video)

    else:
        tweet_media_context = content_div.cssselect('div.card2')
        if len(tweet_media_context) > 0:
            pass

    return tweet

def _parse_tweet_entites(element, entities):
    try:
        tags = element.cssselect('a.twitter-hashtag, a.twitter-cashtag, a.twitter-atreply, a.twitter-timeline-link')
    except Exception as e:
        tags = []
        pass
    if len(tags) > 0:
        for tag in tags:
            classes = tag.get('class').split(' ')
            if 'twitter-hashtag'in classes:
                entities['hashtags'].append(tag.text_content()) #remove # symbol
            elif 'twitter-cashtag' in classes:
                entities['symbols'].append(tag.text_content()) #remove $ symbol
            elif 'twitter-atreply' in classes:
                mentioned_user = {
                    'id_str' : tag.get('data-mentioned-user-id'),
                    'screen_name' : tag.text_content() #remove @ symbol
                }
                entities['user_mentions'].append(mentioned_user)
            elif 'twitter-timeline-link' in classes: # and 'u-hidden' not in classes
                url = {
                    'url': tag.get('href'),
                    'expanded_url' : tag.get('data-expanded-url'),
                    'display_url' : None
                }
                display_url = tag.cssselect('span.js-display-url')
                if len(display_url) > 0:
                    url['display_url'] = display_url[0].text_content()
                entities['urls'].append(url)

def _parse_tweet_media(element, media):
    pass


def parse_media(items_html):
    try:
        markup = lh.fromstring(items_html.replace('\n', '').encode('unicode-escape'))
    except lxml.etree.ParserError as e:
        return []

    media = []
    for li in markup.cssselect('li.js-stream-item'):

        # Check if is a tweet type element
        if 'data-item-id' not in li.attrib:
            continue
        tweet = _parse_tweet(li)
        if tweet:
            media.append(tweet)

    return media

class TwitterPager():
    def __init__(self,
                rate_delay=0,
                error_delay=5,
                timeout=5,
                retry_limit=4,
                title='',
                continue_on_empty_result=False,
                session=Session()):

        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.timeout = timeout
        self.retry_limit = retry_limit
        self.continue_on_empty_result = continue_on_empty_result
        self.session = session

    def execute_request(prepared_request, session=None):
        try:
            return execute_request(prepared_request, session)
        except requests.exceptions.Timeout as e:
            print(e.message)
            print("Sleeping for {:d}".format(self.error_delay))
            sleep(self.error_delay)
            return self.execute_request(prepared_request)

    def get_iterator(self, user, max_position=None):
        result = search(user, max_position)
        yield result

        while True:

            if len(result['media']) == 0:
                if not self.continue_on_empty_result:
                    print('No more media found!')
                    break

            max_position = result['media'][-1]['id_str']
            result = search(user, max_position, self.session)

            yield result

def inorder(media):
    media_sorted = sorted(media, key=itemgetter('id_str'))

if __name__ == '__main__':
    print('lol')
