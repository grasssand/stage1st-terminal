#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import sys

from colorama import init

init()

ATTRIBUTES = {"bold": 1, "dim": 2}

COLORS = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
}

HIGHLIGHTS = {
    "on_black": 40,
    "on_red": 41,
    "on_green": 42,
    "on_yellow": 43,
    "on_blue": 44,
    "on_magenta": 45,
    "on_cyan": 46,
    "on_white": 47,
}


RESET = "\033[0m"


def colored(text, color=None, on_color=None, attrs=None):
    fmt_str = "\033[{}m{}".format
    if COLORS.get(color):
        text = fmt_str(COLORS[color], text)
    if HIGHLIGHTS.get(on_color):
        text = fmt_str(HIGHLIGHTS[on_color], text)
    if attrs:
        for attr in (x for x in attrs if ATTRIBUTES.get(x)):
            text = fmt_str(ATTRIBUTES[attr], text)
    text += RESET

    return text


def cprint(text, color=None, on_color=None, attrs=None, **kw):
    print(colored(text, color, on_color, attrs), **kw)


def check_attr(attr):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            value = getattr(self, attr, None)
            if value is None:
                if self.content is None:
                    self._get_content()
                value = func(self)
                setattr(self, attr, value)
            return value

        return wrapper

    return decorator
