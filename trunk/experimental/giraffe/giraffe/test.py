#!/usr/bin/env python2.4

import doctest

def _test():
    doctest.testfile('new.txt')

if __name__=='__main__':
    _test()
