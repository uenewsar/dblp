#coding: utf-8
import sys
import argparse
import subprocess
import re
import random
import string
import os
import numpy as np
import xml.etree.ElementTree as ET



def make_randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def download_xml(url):

    # change .html to .xml
    url = re.sub(r'\.html$', '.xml', url)
    assert(re.search(r'\.xml$', url))

    # make file name
    fn = make_randomname(8) + '.xml'

    # download
    cmd = 'wget {} -O {}'.format(url, fn)
    #print(cmd)    
    subprocess.run(cmd, shell=True)

    assert(os.path.isfile(fn))

    fr = open(fn, 'r', encoding='utf-8')
    ret = fr.readlines()
    fr.close()

    if os.path.isfile(fn):
        os.remove(fn)

    ret = ''.join(ret)

    return ret


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--inp_file', type=str, help='XML file dump downlaoded from DBLP.', required=False, default=None)
    parser.add_argument('--inp_url', type=str, help='URL of DBLP.', required=False, default=None)
    parser.add_argument('--st', type=int, help='Start year.', required=False, default=None)
    parser.add_argument('--en', type=int, help='End year.', required=False, default=None)
    args = parser.parse_args()

    if args.inp_file is None and args.inp_url is None:
        print(' Either --inp_file or --inp_url must be specified.')
        raise Exception()

    tree = None
    if args.inp_url is not None:
        # download from URL
        print(' Downloading from URL {}'.format(args.inp_url))
        data = download_xml(args.inp_url)
        # parse
        tree = ET.ElementTree(ET.fromstring(data))
    else:
        # parse local XML file
        tree = ET.parse(args.inp_file)


    root = tree.getroot()

    # get person name
    person_name = root.attrib['name']


    # parse article
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


    buf = []
    output_title = '{} ({}-{})'.format(person_name, args.st, args.en)
    buf.append(output_title)
    buf.append('VENUE\tCOUNT')
    for e in sorted(venue2cnt.items(), key=lambda x:x[1], reverse=True):
        buf.append('{}\t{}'.format(e[0], e[1]))

    fw = open(output_title + '.txt', 'w', encoding='utf-8')
    for e in buf:
        print(e)
        fw.write(e + '\n')
    fw.close()
    







if __name__ == '__main__':

    main()
