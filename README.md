# mediascrape

Download a Twitter user's media easily, no API keys needed.

<p align="center">
  <img width="80%" src="cover.png" />
</p>

mediascrape requires no API credentials and instead relies on public endpoints combined with HTML parsing from [lxml](http://lxml.de/) to extract data.

## usage

to download all media images from a user 

`python3 mediascrape.py -u [user]`

eg: `python3 mediascrape.py -u lilbthebasedgod`

this will save all files to a directory of `/media/[user]/*`

## multi\_mediascrape

to download all media images from a list of users, make a line-seperated `.txt` list of users and pass it to `multi_mediascrape` with `-f` 

`python3 multi_mediascrape.py -f [txt file of names]`

eg: `python3 multi_mediascrape.py -f /home/me/tweetscrape/models/names.txt`

this will save all files to a directory of `/media/[user]/*`

## memefinder

experimental script to find the same images posted in different tweets, possibly
suggesting the image is of meme interest

`python3 memefinder.py -d [optional directory] -x [show cross post only]`
