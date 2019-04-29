#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools


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
