#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Call mymod in mymod1
"""

from mymod import MyClass

if __name__ == "__main__":
  """ Main Class
  """
  my = MyClass(1,2)
  print my.spam
  print my.eggs
  