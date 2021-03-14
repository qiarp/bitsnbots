import pytest
from assertpy import assert_that
from parser.parser import Parser


@pytest.mark.parametrize("title, desc, content, tags", [
    ('my title', 'description', 'https://bnbits.ml', ['tag0', 'tag1']),
    ('second title', 'utf8 éçã', 'https://bnbits.ml', ['tag2']),
    ('Custom long title of post', 'this is the description of this post',
     'https://bnbits.ml\nhttps://bnbits.ml', []),
    ('Custom long title of post - . look at this', 'this is the description of this post\nand it now has line break',
     'https://bnbits.ml\nhttps://bnbits.ml\nhttps://duckduckgo.com', ['tag1', 'tag2', 'tag3', 'tag5']),
    ('', 'bnb desc', 'https://bnbits.ml', ['tag21']),
    ('', 'my desc', 'https://www.youtube.com/watch?v=zXTEWFb_6w4\nhttps://duckduckgo.com', ['tag31']),
])
def test_gohugo_parser(title, desc, content, tags):
    expected_template = '''
---
title: '''+title+'''
date: 2021-03-13T11:49:41-03:00
draft: true
summary: '''+desc+''' '''+content+'''
tags: '''+str(tags)+'''
isfeed: true
id: 1
---
        '''
    parser = Parser()
    template, post_id = parser.gohugo_parser(
        title,
        desc,
        content,
        tags,
        post_id=1
    )

    assert_that(template).is_length(len(expected_template)) if title != '' \
        else assert_that(len(template)).is_greater_than(len(expected_template))
    assert_that(template).is_equal_to(expected_template) if title != '' \
        else assert_that(template).is_not_equal_to(expected_template)
    assert_that(post_id).is_not_none()


@pytest.mark.parametrize("title, desc, content, tags", [
    ('my title', 'description', 'https://bnbits.ml', ['tag0', 'tag1'])
])
def test_gohugo_save_with_git(title, desc, content, tags):
    parser = Parser()
    template, post_id = parser.gohugo_parser(
        title,
        desc,
        content,
        tags
    )
    filename = parser.gohugo_save()

    assert_that(filename).is_not_none()
