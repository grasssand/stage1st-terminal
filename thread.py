#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import REPLY_LIST_KEY, THREAD_KEY, URL_REPLY_LIST
from reply import Reply
from stage1st import Stage1stClient
from util import check_attr


class Thread(Stage1stClient):
    def __init__(
        self,
        tid,
        url=None,
        fid=None,
        author=None,
        authorid=None,
        subject=None,
        dateline=None,
        lastpost=None,
        lastposter=None,
        views=None,
        replies_count=None,
        page=None,
    ):
        super().__init__()
        self._key = THREAD_KEY
        self._child = REPLY_LIST_KEY
        self._tid = tid
        self._url = url
        self._fid = fid
        self._author = author
        self._authorid = authorid
        self._subject = subject
        self._dateline = dateline
        self._lastpost = lastpost
        self._lastposter = lastposter
        self._views = views
        self._replies_count = replies_count
        self._cur_page = page or 1

    @property
    def tid(self):
        return self._tid

    @property
    def cur_page(self):
        return self._cur_page

    @property
    def url(self):
        return URL_REPLY_LIST.format(self._tid, self._cur_page)

    @property
    @check_attr("_fid")
    def fid(self):
        return self.content[self._key]["fid"]

    @property
    @check_attr("_author")
    def author(self):
        return self.content[self._key]["author"]

    @property
    @check_attr("_authorid")
    def authorid(self):
        return self.content[self._key]["authorid"]

    @property
    @check_attr("_subject")
    def subject(self):
        return self.content[self._key]["subject"]

    @property
    @check_attr("_dateline")
    def dateline(self):
        return self.content[self._key]["dateline"]

    @property
    @check_attr("_lastpost")
    def lastpost(self):
        return self.content[self._key]["lastpost"]

    @property
    @check_attr("_lastposter")
    def lastposter(self):
        return self.content[self._key]["lastposter"]

    @property
    @check_attr("_views")
    def views(self):
        return self.content[self._key]["views"]

    @property
    @check_attr("_replies_count")
    def replies_count(self):
        return int(self.content[self._key]["replies"])

    @property
    def replies(self):
        if self.content is None:
            self._get_content()
        replies_list = self.content[self._child]
        for reply in replies_list:
            yield Reply(
                reply["pid"],
                reply["tid"],
                reply["author"],
                reply["authorid"],
                reply["dateline"],
                reply["message"],
                self.subject,
            )

    @property
    def all_replies(self):
        max_page = self.replies_count // 50 + 1
        for p in range(1, max_page + 1):
            if p == self._cur_page:
                content = self.content
            else:
                url = URL_REPLY_LIST.format(self._tid, p)
                resp = self._session.get(url)
                resp = resp.json()
                content = resp["Variables"]
            replies_list = content[self._child]
            for reply in replies_list:
                yield Reply(
                    reply["pid"],
                    reply["tid"],
                    reply["author"],
                    reply["authorid"],
                    reply["dateline"],
                    reply["message"],
                    self.subject,
                )

    def next_page(self):
        max_page = self.replies_count // 50 + 1
        if self._cur_page < max_page:
            self._cur_page += 1
            self.refresh()

    def prev_page(self):
        if self._cur_page > 1:
            self._cur_page -= 1
            self.refresh()

    def refresh(self):
        super().refresh()
        self._fid = None
        self._subject = None
        self._dateline = None
        self._lastpost = None
        self._lastposter = None
        self._views = None
        self._replies_count = None
