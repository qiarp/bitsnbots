import pytest
from assertpy import assert_that
from parser.parser import Parser


@pytest.mark.parametrize("title, desc, content, tags, date, clean", [
    ('my title', 'description', 'https://bnbits.ml', ['tag0', 'tag1'], '2021-03-14', True),
    ('second title', 'utf8 éçã', 'https://bnbits.ml', ['tag2'], '2021-03-14', True),
    ('Custom long title of post', 'this is the description of this post',
     'https://bnbits.ml\nhttps://bnbits.ml', [], '2021-03-14', True),
    ('Custom long title of post - . look at this::', 'this is the description of this post\nand it now has line break',
     'https://bnbits.ml\nhttps://bnbits.ml\nhttps://duckduckgo.com',
     ['tag1', 'tag2', 'tag3', 'tag5'], '2021-03-14', False),
    ('', 'bnb desc', 'https://bnbits.ml', ['tag21'], '2021-03-14', True),
    ('', 'my desc', 'https://www.youtube.com/watch?v=zXTEWFb_6w4\nhttps://duckduckgo.com',
     ['tag31'], '2021-03-14', True),
    ('', '', 'https://bnbits.ml', [], '2021-03-14', True),
    (':qq;!"\'', '', 'https://bnbits.ml', [], '2021-03-14', False)
])
def test_gohugo_parser(title, desc, content, tags, date, clean):
    expected_template = '''
---
title: '''+title+'''
date: '''+date+'''
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
        date,
        post_id=1
    )

    if clean:
        assert_that(template).is_equal_to(expected_template) if title != '' \
            else assert_that(len(template)).is_greater_than(len(expected_template))
        assert_that(len(template)).is_equal_to(len(expected_template)) if title != '' \
            else assert_that(template).is_not_equal_to(expected_template)
    else:
        assert_that(template).is_not_equal_to(expected_template)
        assert_that(len(template)).is_less_than(len(expected_template)) if title != '' else True

    assert_that(post_id).is_not_none()


@pytest.mark.skip()
@pytest.mark.parametrize("title, desc, content, tags, date", [
    ('my title', 'description', 'https://bnbits.ml', ['tag0', 'tag1'], '2021-03-11')
])
def test_gohugo_save_with_git(title, desc, content, tags, date):
    parser = Parser()
    template, post_id = parser.gohugo_parser(
        title,
        desc,
        content,
        tags,
        date
    )
    filename = parser.gohugo_save()

    assert_that(filename).is_not_none()

