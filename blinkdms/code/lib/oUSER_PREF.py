# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
manage USER_PREF

File:           oUSER_PREF.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import json
from blinkdms.code.lib.main_imports import *


class MainLib:
    """
     * sub def for table USER_PREF and session['user_glob']
    """
    
    @staticmethod
    def _val2str(val):
        '''
        manage dict or lists: transform to JSON
        '''
        if val==None:
            return val
        
        if type(val)==str:
            return val
        
        if type(val)==dict:
            val_json = json.dumps(val)
            return 'JSON:'+val_json 
        if type(val)==list:
            val_json = json.dumps(val)
            return 'JSON:'+val_json         
        
        # numbers ...
        val = str(val)
        return val
        

    @staticmethod
    def save(db_obj):
        """
	* save userGlob as user preferences
	* optimized for LOW DELETE/INSERT SQL-Methods !
	* - update USER_PREF:UPFLAG = 0
	* - insert / update user + USER_PREF:UPFLAG = 1
	* - delete where UPFLAG = 0
        TBD: check, if user is allowed to save preferences!
	* @param sql      
        
        compare DB with session['user_glob'] : iterate DATABASE
            * tmpUserGlob[KEY] = 
            *      0 : ??? ERROR
            * 		1 : value conflict
            *      2 : equal match
            *      3 : need new value
        """
        
        debug.printx(__name__, "save USER_PREF ...", 1)
        
        user_glob   = session['user_glob']
        debug.printx(__name__, "save user_glob:" + str(user_glob) )
        
        tmpUserGlob = {}
        db_user_id  = session['sesssec']['user_id']
        sqlsel = 'var_name, value FROM user_pref WHERE db_user_id = ' + db_obj.addQuotes(db_user_id) + ' ORDER BY var_name'
        db_obj.select_tuple(sqlsel)
        while db_obj.ReadRow():
            
            val = db_obj.RowData[1]
            key = db_obj.RowData[0]
            val_sess = MainLib._val2str(user_glob.get(key,None))
            
            # type of data: string or number or None
            
            if  (val_sess == None) or ( type(val_sess) == str and val_sess==''):
                tmpUserGlob[key] = 0
                continue # ignore NULL values : will lead to a DELETE

            if (val == val_sess) :
                tmpUserGlob[key]=2
            else:
                tmpUserGlob[key]=1



        """ compare DB with _SESSION['userGlob'] : iterate SESSION-variable
        * tmpUserGlob[KEY] = 1 : conflict
        * tmpUserGlob[KEY] = 2 : equal match
	"""
        for key, val in user_glob.items():

            if  (val == None) or ( type(val) == str and val==''):
                continue # ignore NULL values

            if not tmpUserGlob.get( key, None ): # not saved yet in DB
                tmpUserGlob[key] = 3 # need to insert ...



        """
	just update/insert values, where tmpUserGlob[key]= 1 or 2
	"""

        db_obj.set_auto_commit(0)

        # INIT USER_PREF : UPFLAG=0
        db_obj.execute('UPDATE USER_PREF set UPFLAG=0 WHERE db_user_id = ' + str(db_user_id) )

        # insert/update values
        for key, flag in tmpUserGlob.items():
            
            args = {}
            pk_dict = {
                'DB_USER_ID':db_user_id,
                'VAR_NAME': key,
            }
            act=''
            
            while 1:
                if flag==1: # update VALUE
                    val = MainLib._val2str(user_glob.get(key,None))
                    act='UPDATE'
                    args = {
                        'VALUE': val,
                        'UPFLAG': 1,
                    }

                    break
                if flag==2: # set only the UPDATE flag
                    act='UPDATE'
                    args = {
                        'UPFLAG': 2,
                    }                    
                    break 
                if flag==3: # insert
                    act='INSERT'
                    val = MainLib._val2str(user_glob[key])
                    args = {
                        'VALUE': val,
                        'UPFLAG': 3,
                        'DB_USER_ID':db_user_id,
                        'VAR_NAME': key,                        
                    }                    
                    break
                
                # nothing ...
                break
                    


            if len(args):
                if act=='UPDATE':
                    db_obj.update_row('USER_PREF', pk_dict, args)
                if act=='INSERT':
                    db_obj.insert_row('USER_PREF', args)




        # delete entries, where UPFLAG=0 ( never mentioned ....
        db_obj.execute('DELETE FROM USER_PREF WHERE db_user_id = ' + str(db_user_id) + ' and UPFLAG=0')

        db_obj.commit()
        db_obj.set_auto_commit(1) # switch back to auto commit


    @staticmethod
    def load(db_obj, userGlob):
        '''
        load all user_glob
        :param userGlob: {}
        '''
        db_user_id  = session['sesssec']['user_id']
        json_key='JSON:'
        json_key_len = len(json_key)
        
        db_obj.select_tuple('var_name, value FROM user_pref WHERE db_user_id = ' + db_obj.addQuotes(db_user_id) + ' ORDER BY var_name')
        cnt = 0
        while db_obj.ReadRow():
            
            val = db_obj.RowData[1]
            if val is None:
                pass
            elif type(val) == str and val=='':
                pass
            else:   
                
                if len(val)>=json_key_len:
                    if val[0:json_key_len]==json_key:
                        val = json.loads( val[json_key_len:] )
                
                userGlob[db_obj.RowData[0]] = val
                cnt=cnt+1

        return cnt

    @staticmethod
    def set_key_val(db_obj, key, val, save_in_db=0):
        '''
        save ONE key,val
        optional: save in database
        '''
        session['user_glob'][key] = val
        
        if not save_in_db:
            return
        
        db_user_id  = session['sesssec']['user_id']
        pk_dict = {'DB_USER_ID':db_user_id , 'VAR_NAME':key }
        
        val = MainLib._val2str(val)
        args= {'VALUE':val }
        db_obj.insert_update('USER_PREF', pk_dict, args)

    def save_one_key_val_cls(self, db_obj, key, val):
        '''
        save ONE key,val
        TBD: check, if user is allowed to save preferences!
        '''
        db_user_id  = session['sesssec']['user_id']
        pk_dict = {'DB_USER_ID':db_user_id , 'VAR_NAME':key }
        
        val = MainLib._val2str(val)
        args= {'VALUE':val }
        db_obj.insert_update('USER_PREF', pk_dict, args)    