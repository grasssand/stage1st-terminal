#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

import crayons

from config import FORUM_LIST_KEY, URL_FORUM_LIST, URL_THREAD_LIST
from forum import Forum
from stage1st import Stage1stClient


class Index(Stage1stClient):
    def __init__(self, url=None, page=1):
        super().__init__()
        self._child = FORUM_LIST_KEY
        self._url = url
        self._cur_page = page

    @property
    def cur_page(self):
        return self._cur_page

    @property
    def url(self):
        return self._url or URL_FORUM_LIST

    @property
    def forums(self):
        if self.content is None:
            self._get_content()
        forums_list = self.content[self._child]
        for i, forum in enumerate(forums_list):
            f = Forum(
                forum["fid"],
                URL_THREAD_LIST.format(forum["fid"], 1),
                forum["name"],
                forum.get("description", ""),
                forum["threads"],
                forum["posts"],
                forum["todayposts"],
            )
            print(self._info(i, f))

    def forum(self, fid):
        return Forum(fid)

    def terminal(self):
        self.forums
        while True:
            ipt = input(f"Index $ ")
            if ipt:
                opt, args = re.match(r"\s*([a-z]*)\s*(\d*)", ipt).groups()
                if opt == "q":
                    break
                elif opt == "f":
                    self.refresh()
                    self.forums
                elif opt == "e":
                    sys.exit(0)
                elif opt == "h" or opt == "help":
                    self.help()
                elif args and not opt:
                    f = self.forum(args)
                    f.termianl()
                else:
                    pass

    def help(self):
        print(
            """
                <operate> [args]
                [Forum ID]          进入相应论坛板块
                <f>                 刷新
                <q>                 离开返回上一级
                <e>                 退出
                <h>                 显示帮助信息
            """
        )

    def _info(self, idx, forum_cls):
        return (
            f"[{crayons.cyan(forum_cls.fid)}]\t"
            f"{forum_cls.name}({crayons.green(forum_cls.todayposts)})\t"
            f"{crayons.yellow(forum_cls.description)}"
        )


if __name__ == "__main__":
    s = Index()
    s.terminal()
