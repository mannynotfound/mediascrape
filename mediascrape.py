import TwitterMediaSearch
import os
import urllib.request
import argparse
from pathlib import Path

def mediascrape(user, output):
    print('Fetching user media...')

    TwitterPageIterator = TwitterMediaSearch.TwitterPager(title = user).get_iterator(user)

    twitter_media = []
    for page in TwitterPageIterator:
        for media in page['media']:
            twitter_media.append(media)
        print('Fetched {} media tweets..'.format(len(twitter_media)))

    path = os.path.dirname(os.path.realpath(__file__))
    default_output = path + '/media'

    dump_dir = '{0}/{1}'.format(output or default_output, user)
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)

    # extract all nested media
    img_urls = []
    for m in twitter_media:
        media = m.get('entities', {}).get('media', [])
        imgs = [x for x in media if x.get('type') == 'photo']
        for idx, img in enumerate(imgs):
            img_urls.append({
                'url': img.get('media_url'),
                'filename': '{}_{}_{}.jpg'.format(user, m.get('id_str'), idx),
            })

    # fetch + save images
    total = len(img_urls)
    print('')
    print('Found {} images!'.format(total))
    print('')
    for idx, img in enumerate(img_urls):
        url = img.get('url')
        filename = img.get('filename')
        # only save the photo if it does not already exist
        photo_already_exists = Path(dump_dir + "/" + filename).is_file()
        if photo_already_exists:
            print('Skipping image {} - already exists!'.format(idx + 1))
        else:
            print('Fetching image {}/{} - {}'.format(idx + 1, total, url))
            try:
                urllib.request.urlretrieve(url, '{0}/{1}'.format(dump_dir, filename))
            except Exception as e:
                print(e)

    print('')
    print('Done scraping media!')


if __name__ == '__main__':
    # parse cli arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', help = 'user to scrape')
    ap.add_argument('-o', '--output', help = 'directory to save media to')
    args = vars(ap.parse_args())
    user = args['user']
    output = args['output']
    mediascrape(user, output)
