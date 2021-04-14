from os import listdir
from requests import get
from re import compile, UNICODE, sub
from github.git import Git

gohugo_path = '../bytesnbits/content/feed'


class Parser:
    def __init__(self):
        self.content = None
        self.pid = None
        return

    def gohugo_parser(self, title: str, desc: str, content: str, tags: list, date: str, post_id=None) -> (str, str):

        template = '''
---
title: [$title]
date: [$date]
draft: true
summary: [$desc] [$content]
tags: [$tags]
isfeed: true
id: [$id]
---
        '''
        lc = locals()
        for value in lc.keys():
            if value in ['self', 'tags', 'post_id']:
                continue
            data = self.cleanup_str(lc.get(value)) \
                if value in ['title'] \
                else lc.get(value)

            if data is None or len(data) <= 1:
                continue
            template = template.replace(f'[${value}]', data)

        template = template.replace('[$tags]', str(tags))

        total_posts = len([name for name in listdir(gohugo_path)])
        post_id = f'{total_posts + 2}' if post_id is None else '1'

        template = template.replace('[$id]', post_id)

        if title == '' and content != '':
            first_url = content.split('\n')[0]
            req = get(first_url)
            if req.status_code == 200:
                title_re = compile(r'<title>(.*?)</title>', UNICODE)
                match = title_re.search(req.text)
                if match:
                    template = template.replace('[$title]',  self.cleanup_str(str(match.group(1))))

        if desc == '':
            template = template.replace('[$desc]', '')

        self.content = template
        self.pid = post_id

        return template, post_id

    def gohugo_save(self) -> str:
        filename = f'bnb-feed-{self.pid}.md'

        file = open(f'{gohugo_path}/{filename}', 'w')
        file.write(self.content)
        file.close()

        git = Git()
        ok = git.push_changes(f'{filename}')
        if not ok:
            return None

        return filename

    def cleanup_str(self, content: str):
        n = sub('[:"\']', '', content)
        return n
