#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Callback:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.data = self.kwargs.get('data', None)
        self.retry = None
        self.timeout = None




def callback_si():
    pass


def main():
    callback_si()


if __name__ == "__main__":
    main()
