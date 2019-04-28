#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests_html import HTML

from stage1st import Stage1stClient


class Reply(Stage1stClient):
    def __init__(
        self,
        pid=None,
        tid=None,
        author=None,
        authorid=None,
        dateline=None,
        message=None,
        subject=None,
    ):
        self._pid = pid
        self._tid = tid
        self._author = author
        self._authorid = authorid
        self._dateline = dateline
        self._message = "<div>" + message + "</div>"
        self._subject = subject

    @property
    def pid(self):
        return self._pid

    @property
    def tid(self):
        return self._tid

    @property
    def author(self):
        return self._author

    @property
    def authorid(self):
        return self._authorid

    @property
    def dateline(self):
        return self._dateline

    @property
    def message(self):
        html = HTML(html=self._message)
        return html.text

    @property
    def subject(self):
        return self._subject
