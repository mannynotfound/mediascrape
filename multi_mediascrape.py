import argparse
import os
import io
import json
import sys
from mediascrape import mediascrape

# set base path
path = os.path.dirname(os.path.realpath(__file__))
dump_path = path + '/media'

# parse cli arguments
ap = argparse.ArgumentParser()
ap.add_argument('-f', '--file', help = 'file of names to grab')
ap.add_argument('-o', '--output', help = 'directory to save media to')
args = vars(ap.parse_args())
filename = args['file']
output = args['output']

with io.open(filename, encoding='utf-8') as f:
    name_list = f.read().splitlines()

for name in name_list:
    mediascrape(name, output)
