#
# gfwlist2shadowrocket
# gfwlist_parser
#
# Created by wuwenhan on 18/10/2017.
# 03:26
# Copyright (c) 2017 wuwenhan. All rights reserved.
#

import base64
from os import path

from urllib.parse import urlparse
from urllib.request import urlopen


def get_hostname(something):
    try:
        # quite enough for GFW
        if not something.startswith('http:'):
            something = 'http://' + something
        r = urlparse(something)
        return r.hostname
    except Exception as e:
        print(e)
        return None


def add_domain_to_set(s, something):
    hostname = get_hostname(something)
    if hostname is not None:
        if hostname.startswith('.'):
            hostname = hostname.lstrip('.')
        if hostname.endswith('/'):
            hostname = hostname.rstrip('/')
        if hostname:
            s.add(hostname)


class GFWListParser(object):
    def __init__(self, output, gfwlist_path=None):
        super().__init__()
        self.output = output
        self.gfwlist_path = gfwlist_path
        self.base_conf = './base.conf'
        self.user_rule = './user_rule.txt'
        self.gfwlist_url = 'https://raw.githubusercontent.com/gfwlist' \
                           '/gfwlist/master/gfwlist.txt '

    def generate_conf(self):
        gfwlist = self.parse_gfwlist()
        user_rule = self.parse_user_rule()

        gfwlist = ['DOMAIN-SUFFIX,' + d + ',Proxy' for d in gfwlist]
        user_rule = ['DOMAIN-SUFFIX,' + d + ',Proxy' for d in user_rule]

        base_conf = self.load_base_config()
        conf = base_conf.format(gfwlist='\n'.join(gfwlist),
                                user_rule='\n'.join(user_rule))

        self.save_conf(conf)

    def load_user_rule(self):
        if path.exists(self.user_rule) and path.isfile(self.user_rule):
            with open(self.user_rule) as f:
                user_rule = f.read()
                user_rule = user_rule.splitlines()
            return user_rule
        else:
            raise Exception('File `user_rule.txt` does not exist.')

    def load_gfwlist(self):
        if self.gfwlist_path:
            if path.exists(self.gfwlist_path) \
                    and path.isfile(self.gfwlist_path):
                with open(self.gfwlist_path, 'rb') as f:
                    gfwlist = f.read()
                    gfwlist = base64.decodebytes(gfwlist)
            else:
                raise Exception(
                    'File {} does not exist.'.format(self.gfwlist_path))
        else:
            res = urlopen(self.gfwlist_url)
            if res.code == 200:
                gfwlist = base64.b64decode(res.read())
            else:
                raise Exception(
                    'Get GFWList from GitHub failed, check you network.')
        gfwlist = str(gfwlist, encoding='utf-8')
        gfwlist = gfwlist.splitlines()
        return gfwlist

    def load_base_config(self):
        if path.exists(self.base_conf) and path.isfile(self.base_conf):
            with open(self.base_conf) as f:
                base_config = f.read()
            return base_config
        else:
            raise Exception('File `base.conf` does not exist.')

    def save_conf(self, conf):
        if path.exists(path.abspath(self.output)):
            print('File {} already exists, do you want to replace it?'.format(
                path.basename(self.output)))
            print('-' * 80)
            print('(Y)es/(N)o: ', end='')
            input_ = input()
            if input_ not in ['Y', 'y']:
                return
        with open(self.output, 'w') as f:
            f.write(conf)
        print('{} saved.'.format(path.basename(self.output)))

    def parse_gfwlist(self):
        gfwlist = self.load_gfwlist()
        domains = set()
        for rule in gfwlist:
            if rule.find('.*') >= 0:
                continue
            elif rule.find('*') >= 0:
                rule = rule.replace('*', '/')
            if rule.startswith('!'):
                continue
            elif rule.startswith('['):
                continue
            elif rule.startswith('@'):
                # ignore white list
                continue
            elif rule.startswith('||'):
                add_domain_to_set(domains, rule.lstrip('||'))
            elif rule.startswith('|'):
                add_domain_to_set(domains, rule.lstrip('|'))
            elif rule.startswith('.'):
                add_domain_to_set(domains, rule.lstrip('.'))
            else:
                add_domain_to_set(domains, rule)
        return domains

    def parse_user_rule(self):
        user_rule = self.load_user_rule()
        domains = set()
        for rule in user_rule:
            if rule.startswith('!'):
                continue
            elif rule == '':
                continue
            else:
                domains.add(rule)
        return domains
