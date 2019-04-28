#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import URL_FORUM_LIST, URL_THREAD_LIST, FORUM_LIST_KEY
from stage1st import Stage1stClient
from forum import Forum


class Index(Stage1stClient):
    def __init__(self, url=None, page=None):
        super().__init__()
        self._child = FORUM_LIST_KEY
        self._url = url
        self._cur_page = page or 1

    @property
    def cur_page(self):
        return self._cur_page

    @property
    def url(self):
        return URL_FORUM_LIST

    @property
    def forums(self):
        if self.content is None:
            self._get_content()
        forums_list = self.content[self._child]
        for forum in forums_list:
            yield Forum(
                forum["fid"],
                URL_THREAD_LIST.format(forum["fid"], 1),
                forum.get("name"),
                forum.get("description", ""),
                forum.get("threads"),
                forum.get("posts"),
                forum.get("todayposts"),
            )
