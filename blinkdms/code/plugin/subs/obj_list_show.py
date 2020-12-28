# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
search
File:           obj_list_show.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.main_imports import *

from blinkdms.code.lib.tab_abs_sql import Table_sql
from blinkdms.code.lib.gui.obj_list_sub import Obj_list_sub

from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.oDB_USER import oDB_USER

class ShowList:
    
    def __init__(self, massdata, req_data):
        self.massdata = massdata
        self._req_data = req_data

    def get_table_header(self, tab_order_list):
        '''
        :param tab_order_list: [ {'col':column, 'ord': 'ASC|DESC'} ]
        '''
        header = self.listExtLib.get_head_cols()

        # produce temporary DICT for order by info
        order_dict={}
        for row in tab_order_list:
            order_dict[row['col']] = row['ord']        

        # rescan columns ...
        ind = 0
        for row in header:
            col_name = row['name']
            if col_name in order_dict:
                header[ind]['sort'] = order_dict[col_name]
            ind = ind + 1
        
        return header
    
    def sort_set(self, order_dict):
        
        order_list=[]
        for key,val in order_dict.items():
            order_list.append({'col':key, 'ord':val})
            
        return order_list         
    
    def start(self, db_obj, db_obj2):

        context = session['sesssec']['my.context']

        if context=='EDIT':
            from blinkdms.code.plugin.subs.obj_list_x_EDIT import Main as ListExtender
        if context == 'ACTIVE':
            from blinkdms.code.plugin.subs.obj_list_x_ACTIVE import Main as ListExtender

        self.listExtLib = ListExtender()
        
        doc_lib1 = oDOC_VERS.Table(context)
        usetable = doc_lib1.table
        self.table = usetable
        
        sql_build_lib = Table_sql(usetable)
        sql_from = sql_build_lib.get_sql_from(db_obj)
    
        sql_cmd = "count(x.VERSION_ID) from " + sql_from
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        objcnt_sel = db_obj.RowData[0]
        
        if objcnt_sel:
    
            new_sort_list = None
            if 'qs' in self._req_data:
                new_sort_list = self.sort_set(self._req_data['qs'])
    
            self.list_helper = Obj_list_sub(self.table)
            if new_sort_list != None:
                self.list_helper.set_sort_prefs(new_sort_list)
                self.list_helper.save_user_prefs_DB(db_obj)            
    
            tab_order_list = self.list_helper.get_sort_prefs()
            sql_from_order = sql_build_lib.get_sql_from_order_list(db_obj, tab_order_list)
    
            self.massdata['header'] = self.get_table_header(tab_order_list)
            cols = []
            ind = 0
            col_id_DB_USER = -1
            for row in self.massdata['header']:
                colname = row['name']
                cols.append(colname)
                if colname == 'x.DB_USER_ID':
                    col_id_DB_USER = ind
                ind = ind + 1
    
            cols_text = ','.join(cols)
            sql_cmd = cols_text + " from " + sql_from_order
            debug.printx(__name__, "(52) sql_cmd:" + str(sql_cmd))
    
            self.massdata['data'] = []
            db_obj.select_tuple(sql_cmd)
            while db_obj.ReadRow():
                row_data = list(db_obj.RowData)

                if col_id_DB_USER >= 0:
                    if (row_data[col_id_DB_USER]):
                        user_name = oDB_USER.Table.get_fullname(db_obj2, row_data[col_id_DB_USER])
                        row_data[col_id_DB_USER] = user_name
                self.massdata['data'].append(row_data)
    
            #debug.printx(__name__, "(72) self.massdata[data]:" + str(self.massdata['data']))
    
    

