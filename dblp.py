#coding: utf-8
import sys
import numpy as np
import argparse
import xml.etree.ElementTree as ET
import re

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--inp', type=str, help='file name', required=True)
    parser.add_argument('--st', type=int, required=False, default=None)
    parser.add_argument('--en', type=int, required=False, default=None)
    args = parser.parse_args()

    tree = ET.parse(args.inp)
    root = tree.getroot()

    venue2cnt = {}
    
    for child in root:
        if child.tag != 'r':
            continue
        for e in child:
            if e.tag != 'article' and e.tag != 'inproceedings':
                continue

            tmp = {}
            for f in e:
                if f.tag=='year':
                    tmp['year'] = int(f.text)
                if f.tag=='journal':
                    tmp['journal'] = f.text
                if f.tag=='booktitle':
                    tmp['booktitle'] = f.text

            assert('year' in tmp)
            if args.st is not None and tmp['year'] < args.st:
                continue
            if args.en is not None and tmp['year'] > args.en:
                continue


            assert(not ('booktitle' in tmp and 'journal' in tmp))
            if 'journal' in tmp:
                tmp['booktitle'] = tmp['journal']
                del(tmp['journal'])

            if tmp['booktitle'] == 'CoRR':
                continue

            tmp['booktitle'] = re.sub(r' \([0-9]+\)$', '', tmp['booktitle'])

            if tmp['booktitle'] not in venue2cnt:
                venue2cnt[tmp['booktitle']] = 0
            venue2cnt[tmp['booktitle']] += 1

    for e in sorted(venue2cnt.items(), key=lambda x:x[1], reverse=True):
        print('{}\t{}'.format(e[0], e[1]))







if __name__ == '__main__':

    main()
