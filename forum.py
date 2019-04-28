#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import URL_THREAD_LIST, URL_REPLY_LIST, FORUM_KEY, THREAD_LIST_KEY
from stage1st import Stage1stClient
from thread import Thread
from util import check_attr


class Forum(Stage1stClient):
    def __init__(
        self,
        fid,
        url=None,
        name=None,
        description=None,
        threads_count=None,
        posts=None,
        todayposts=None,
        page=None,
    ):
        super().__init__()
        self._key = FORUM_KEY
        self._child = THREAD_LIST_KEY
        self._fid = fid
        self._url = url
        self._name = name
        self._description = description
        self._threads_count = threads_count
        self._posts = posts
        self._todayposts = todayposts
        self._cur_page = page or 1

    @property
    def fid(self):
        return self._fid

    @property
    def cur_page(self):
        return self._cur_page

    @property
    def url(self):
        return URL_THREAD_LIST.format(self._fid, self._cur_page)

    @property
    @check_attr("_name")
    def name(self):
        return self.content[self._key]["name"]

    @property
    @check_attr("_description")
    def description(self):
        return self.content[self._key].get("description", "")

    @property
    @check_attr("_threads_count")
    def threads_count(self):
        return self.content[self._key]["threads"]

    @property
    @check_attr("_posts")
    def posts(self):
        return self.content[self._key]["posts"]

    @property
    def todayposts(self):
        return self._todayposts

    @property
    def threads(self):
        if self.content is None:
            self._get_content()
        threads_list = self.content[self._child]
        for thread in threads_list:
            yield Thread(
                thread["tid"],
                URL_REPLY_LIST.format(thread["tid"], 1),
                self._fid,
                thread["author"],
                thread["authorid"],
                thread["subject"],
                thread["dateline"],
                thread["lastpost"],
                thread["lastposter"],
                thread["views"],
                thread["replies"],
            )

    def next_page(self):
        max_page = self.threads_count // 30 + 1
        if self._cur_page < max_page:
            self._cur_page += 1
            self.refresh()

    def prev_page(self):
        if self._cur_page > 1:
            self._cur_page -= 1
            self.refresh()

    def refresh(self):
        super().refresh()
        self._name = None
        self._description = None
        self._threads = None
        self._posts = None
