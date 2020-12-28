
"""
main TASK method
File:           oTASK.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *


class UserTask:
    
    __id = None

    def __init__(self, user_id):
        self.user_id = user_id

    def getNumOpenTasks(self, db_obj):
        num = db_obj.count_elem('AUD_PLAN', {'DB_USER_ID': self.user_id, 'DONE': 1})
        return num
