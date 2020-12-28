# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
date functions
File:           f_date.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

def f_datetime2YMD(date_obj):
    return date_obj.strftime("%Y-%m-%d")