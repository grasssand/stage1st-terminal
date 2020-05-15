#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests_html import HTML

from stage1st import Stage1stClient
from util import colored


class Reply(Stage1stClient):
    def __init__(
        self,
        sid=0,
        page=1,
        author=None,
        dateline=None,
        message=None,
        pid=None,
        tid=None,
        subject=None,
        fid=None,
    ):
        super().__init__(sid=sid, page=page)
        self.author = author
        self.dateline = dateline
        self.message = message
        self.pid = pid
        self.tid = tid
        self.subject = subject
        self.fid = fid

    def __str__(self):
        return (
            f"{colored(self.dateline, 'green')}\t"
            f"{colored(self.author, 'cyan')}\n"
            f"{self.message}"
        )

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        message = message.replace('<div class="quote"><blockquote>', "“").replace(
            "</blockquote></div>", "<br/>”"
        )
        html = HTML(html=f"<div>{message}</div>")
        self._message = html.text
