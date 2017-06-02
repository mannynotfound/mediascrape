import TwitterMediaSearch
import os
import urllib.request
import argparse
from pathlib import Path

def mediascrape(user, output):
    TwitterPageIterator = TwitterMediaSearch.TwitterPager(title = user).get_iterator(user)

    all_media = []
    count = 0

    for page in TwitterPageIterator:
        for media in page['media']:
            print(count, ' ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– ')
            print(media)
            all_media.append(media)
            print('')
            print('')
            # print("{0} id: {1} text: {2}".format(count, tweet['id_str'], tweet['text']))
            count += 1

    path = os.path.dirname(os.path.realpath(__file__))
    if output:
        dump_path = output
    else:
        dump_path = path + '/media'

    dump_dir = '{0}/{1}'.format(dump_path, user)
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)

    # extract all nested media
    img_urls = []
    for m in all_media:
        media = m.get('entities', {}).get('media', [])
        imgs = [x for x in media if x.get('type') == 'photo']
        for idx, img in enumerate(imgs):
            img_urls.append({
                'url': img.get('media_url'),
                'filename': '{}_{}_{}.jpg'.format(user, m.get('id_str'), idx),
            })


    # fetch + save images
    total = len(img_urls)
    for idx, img in enumerate(img_urls):
        url = img.get('url')
        filename = img.get('filename')
        # only save the photo if it does not already exist
        photo_already_exists = Path(dump_dir + "/" + filename)
        if photo_already_exists.is_file():
            print('fetching image {} - already exists, skipping...'.format(idx + 1))
        else:
            print('fetching image {}/{} - {}'.format(idx + 1, total, url))
            try:
                urllib.request.urlretrieve(url, '{0}/{1}'.format(dump_dir, filename))
            except Exception as e:
                print(e)


if __name__ == '__main__':
    # parse cli arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', help = 'user to scrape')
    ap.add_argument('-o', '--output', help = 'directory to save media to')
    args = vars(ap.parse_args())
    user = args['user']
    output = args['output']
    mediascrape(user, output)

