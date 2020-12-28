# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
system alarm log
COLUMNS:
  DATEX
  IPADDR
  USER_NICK: user nick UPPERCASE
  KEYX 
    'LOGIN'
    'USER.LOCK'
  MESSAGE: text

File:           oSYS_A_LOG.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
#from flask import request   
from datetime import datetime, timedelta
import time
from flask import request

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.oDB_USER import oDB_USER


def save_log(db_obj, args):
    '''
    save log
    :param args:
    USER_NICK
    KEYX 
    MESSAGE
    '''
    
    user_nick = args.get('USER_NICK','')
    
    if user_nick!='' and user_nick!=None:
        args['USER_NICK'] = args['USER_NICK'].upper()
        
    args['DATEX']=db_obj.Timestamp2Sql()
    ipaddr  = request.environ['REMOTE_ADDR'] # does not work with NGNIX? :request.environ.get('HTTP_X_REAL_IP', request.remote_addr)          
    args['IPADDR']=ipaddr
   
    try:
        db_obj.insert_row('SYS_A_LOG', args, 'DATEX')        
    except:
        pass  # do not handle this error
    
def del_logs(db_obj, del_args):
    '''
    delete logs
    '''
    if not len(del_args):
        raise BlinkError(1,'No keys given.')
    db_obj.del_row('SYS_A_LOG', del_args)        
     
    
def ask_lock_user(db_obj, user_nick):
    '''
    ask if the user account should be locked?
    TBD: LOCK only an IP-Address ???
    :return: int  do_lock: 0,1
    '''
    
    do_lock=0
    TIME_DIFF_MINUTES = 10 #minutes
    MAX_FAIL_ALLOW    = 5 # max 10 tries allowed
    
    time_now  = datetime.now()
    time_diff  = timedelta(minutes=TIME_DIFF_MINUTES)
    time_start = time_now- time_diff
    time_start_str = db_obj.Timestamp2Sql(time_start)
    
    user_nick = user_nick.upper()
    # <DB>
    sql_cmd = "count(*) from SYS_A_LOG where datex>="+db_obj.addQuotes(time_start_str) +' and UPPER(USER_NICK)='+db_obj.addQuotes(user_nick)
    db_obj.select_tuple(sql_cmd)
    db_obj.ReadRow()
    entry_cnt = db_obj.RowData[0]  
    
    if entry_cnt > MAX_FAIL_ALLOW:
        do_lock=1
        
    return do_lock

def ask_login_allow(db_obj, user_nick):
    '''
    allow again
    - MUST find a last LOCK entry
    '''
    
    answer = 0
    ALLOW_TIME_DIFF_MINUTES = 15 #minutes
    time_now  = datetime.now()
    time_diff_allow  = timedelta(minutes=ALLOW_TIME_DIFF_MINUTES)
    time_start_allow = time_now - time_diff_allow
    time_start_allow_str = db_obj.Timestamp2Sql(time_start_allow)    
    
    user_nick = user_nick.upper()
    sql_cmd = "max(DATEX) from SYS_A_LOG where USER_NICK="+db_obj.addQuotes(user_nick)+ \
        " and KEYX=" + db_obj.addQuotes('USER.LOCK')
    db_obj.select_tuple(sql_cmd)
    db_obj.ReadRow()
    last_date = db_obj.RowData[0]
    if last_date == None:
        return [answer, '']
    
    last_date_str='UNDEFINED'
    try:
        last_date_str = db_obj.Timestamp2Sql(last_date) 
    except:
        # undefined error ...
        return [answer, last_date_str]
    
    if last_date<time_start_allow:
        answer = 1
    
    return [answer, last_date_str]

        
def lock_user(db_obj, user_nick): 
    '''
    lock the user
    '''
    
    user_nick = user_nick.upper()
    user_id = oDB_USER.Table.get_user_by_nick(db_obj, user_nick)
    if user_id:
        
        mod_lib = oDB_USER.modify_obj(db_obj, user_id)
        flag=2
        mod_lib.set_login_denied(db_obj, flag)
        
        # wait for a new time-slot for  the log ...
        time.sleep(2.0)
        
        up_args= {
            'USER_NICK':user_nick,
            'KEYX' :'USER.LOCK',
            'MESSAGE':'User locked now by system'              
        }
        save_log(db_obj, up_args)
        
def unlock_user(db_obj, user_nick): 
    '''
    unlock the user
    '''
    user_nick = user_nick.upper()
    user_id = oDB_USER.Table.get_user_by_nick(db_obj, user_nick)
    if user_id:
        
        mod_lib = oDB_USER.modify_obj(db_obj, user_id)
        flag=0
        mod_lib.set_login_denied(db_obj, flag)
        
        # wait 10ms for the log ...
        time.sleep(0.01)
        
        # delete old logs
        del_args={'USER_NICK':user_nick}
        del_logs(db_obj, del_args)