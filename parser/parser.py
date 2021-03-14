from os import listdir
from requests import get

gohugo_path = '../bytesnbits/content/feed'


class Parser:
    def __init__(self):
        self.content = None
        self.pid = None
        return

    def gohugo_parser(self, title, desc, content, tags, post_id=None) -> (str, str):

        template = '''
---
title: [$title]
date: 2021-03-13T11:49:41-03:00
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
            data = lc.get(value)
            template = template.replace(f'[${value}]', data)

        template = template.replace('[$tags]', str(tags))

        total_posts = len([name for name in listdir(gohugo_path)])
        post_id = f'{total_posts + 1}' if post_id is None else '1'

        template = template.replace('[$id]', post_id)

        # if title is None, get title of url

        self.content = template
        self.pid = post_id

        return template, post_id

    def gohugo_save(self) -> str:
        filename = f'bnb-feed-{self.pid}.md'

        file = open(f'{gohugo_path}/{filename}', 'w')
        file.write(self.content)
        file.close()

        return filename
