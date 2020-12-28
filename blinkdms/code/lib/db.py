# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
abstract layer for any database, currently use postgres
File:           db.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.db_pg_abs import pg_database

class db (pg_database):
    pass