import TwitterMediaSearch
import os
import urllib.request
import argparse

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

    download_count = 0
    path = os.path.dirname(os.path.realpath(__file__))
    if output:
        dump_path = output
    else:
        dump_path = path + '/media'

    dump_dir = '{0}/{1}'.format(dump_path, user)
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)

    for m in all_media:
        current_media = m.get('entities', {}).get('media', [])

        for idx, cm in enumerate(current_media):
            if cm.get('type') == 'photo':
                download_count += 1
                url = cm.get('media_url')
                filename = '{0}_{1}.jpg'.format(user, m.get('id_str'))
                print('fetching image {0} - {1}'.format(download_count, url))
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

