# 
# gfwlist2shadowrocket
# g2s
# 
# Created by wuwenhan on 18/10/2017.
# 03:24
# Copyright (c) 2017 wuwenhan. All rights reserved.
#

import argparse
from gfwlist_parser import GFWListParser


def build_args():
    parser = argparse.ArgumentParser(description='Convert GFWList to '
                                                 'Shadowrocket config')
    parser.add_argument('-g',
                        '--gfwlist',
                        type=argparse.FileType('w'),
                        default=None,
                        help='`gfwlist.txt` file path, this script will '
                             'download `gfwlist.txt` from GitHub if you '
                             'didn\'t specific this argument.')
    parser.add_argument('-o',
                        '--output',
                        type=argparse.FileType('w'),
                        default='./shadowrocket.conf',
                        help='write documents to FILE, default '
                             '`shadowrocket.conf`')

    return parser.parse_args()


def main():
    args = build_args()
    parser = GFWListParser(output=args.output.name,
                           gfwlist_path=args.gfwlist.name
                           if args.gfwlist else None)
    parser.generate_conf()


if __name__ == '__main__':
    main()
