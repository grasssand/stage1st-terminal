#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

from config import FORUM_LIST_KEY, URL_FORUM_LIST, URL_THREAD_LIST
from forum import Forum
from stage1st import Stage1stClient
from util import colored


class Index(Stage1stClient):
    def __init__(self, url=None, page=1):
        super().__init__()
        self._child = FORUM_LIST_KEY
        self._url = url
        self._cur_page = page
        self._index = {}

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
        forums_list = sorted(forums_list, key=lambda x: -int(x["todayposts"]))
        for i, forum in enumerate(forums_list):
            self._index[str(i)] = forum["fid"]
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
            ipt = input(f"论坛 $ ")
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
                elif opt == "" and args:
                    fid = self._index.get(args)
                    if fid is not None:
                        f = self.forum(fid)
                        f.termianl()
                else:
                    pass

    def help(self):
        print(
            """
                <operate> [args]
                [Forum Index]       进入相应论坛板块
                <f>                 刷新
                <q>                 离开返回上一级
                <e>                 退出
                <h>                 显示帮助信息
            """
        )

    def _info(self, idx, forum_cls):
        return (
            f"「{colored(idx, 'red', attrs=['bold'])}」\t"
            f"{forum_cls.name} ({colored(forum_cls.todayposts, 'green')})\t"
            f"{colored(forum_cls.description, 'yellow')}\r"
        )


if __name__ == "__main__":
    s = Index()
    s.terminal()
