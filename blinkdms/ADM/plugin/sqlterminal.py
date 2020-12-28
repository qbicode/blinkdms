'''
SQL terminal plugin
'''
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.gui.form import form

import sys

class plug_XPL(gPlugin) :  
    '''
     * SQL terminal plugin
     * @package sqlterminal.py
     * @author  Steffen Kube (steffen@blink-dx.com)
    '''

    def register(self) :

        self.infoarr['title']	= 'SQL Terminal'
       
        self.infoarr['layout']	= 'ADM/sqlterminal'
        self.infoarr['admin.only'] = True
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]         


    format =''# 'html' or 'csv'
    
    def _init1(self,sqls, outmode, parx) :
    
        
        sqls = sqls.strip()
        if ( outmode=="" ): outmode="html"
    
        formatDef = {'html':'html', 'csv':'csv', 'csvTmp':'csv', 'hex':'hex' }
        self.format = formatDef[outmode]
    
        self.sqls = sqls
        self.outmode = outmode
        self.parx = parx
    

    def _checkSelect(self, sqls):
        answer = 0
        pos1 = sqls.find(' ')
        start_pattern = sqls[0:pos1]
        cmd_head = start_pattern
        rest = sqls[pos1:]

        return {'cmd_head': cmd_head.upper(), 'rest': rest}

    def _getCount(self, sqlo, sqls):

        pos = sqls.lower().find('from'.lower())
        if pos < 0:
            return 0
 
        pos_new = pos + 4
        fromAfter = sqls[pos_new:] 
        
        pos_ord = fromAfter.find('order by')
        if pos_ord>0:
            fromAfter = fromAfter[0:pos_ord]
 
        debug.printx(__name__, "FROM_AFTER: "+ fromAfter + "| pos_ord:"+str(pos_ord) )	 
 
        sqlsel = 'count (1) from ' + fromAfter
        answer = sqlo.select_tuple(sqlsel)
    
        sqlo.ReadRow()
        cnt = sqlo.RowData[0]
        return (cnt)
    
    
    """
     * the main export loop
     * @return 
     * @param object sqlO
     * @global string outmode
     * @global array parx
     """
    def doit(self, sqlo ) :
        global  error
    
        parx    = self.parx
        outmode = self.outmode
        format  = self.format
        sqls    = self.sqls.strip()
        
        debug.printx(__name__, "SQLS: "+ sqls )
    
        self.lineFeedsRep = 0
        isSelect = 0
        answer = self._checkSelect( sqls )
    
        allow_all_sql = 1
        if ( allow_all_sql ) :     
            # other user tests
            # only "select is allowed !!! 
           
            if  answer['cmd_head']!='SELECT' and not self.is_admin() :
                raise ValueError ("only 'select' command allowed for NON-Admins.")
        
            if answer['rest']=='' :
                raise ValueError("expecting at least one WHITE_SPACE in the SQL-command")
        
        sqls_without_select = answer['rest']
    
        if answer['cmd_head']=='SELECT' :
            isSelect=1
        
        cnt = 0
        objcnt = 0 # default
        # get number of results ...
        docnt  = 0
        	
        debug.printx(__name__, "SQLS2: "+ sqls )	
        if isSelect==1 and self.parx['count']>0  :
            docnt  = 1
            objcnt = self._getCount(sqlo, sqls)
    
    
    
        if (docnt>0 and outmode!="csv" ) :
            self.text_array.append('Expected number of rows:' + str(objcnt))
  
        if not isSelect:
            self.text_array.append("Execute a NON-Select command.")
            sqlo.execute(sqls)
            return
    
    
        sqlo.select_tuple(sqls_without_select)
        colName_list = sqlo.column_names()

        self.data = []

        self.data.append(colName_list)

        while(sqlo.ReadRow()) :
            self.data.append(sqlo.RowData)
            cnt = cnt + 1







    def startMain(self) :

        self.text_array = []
        self.data = []
        db_obj = self._db_obj1
        
        parx   =  {}
        if "parx" in self._req_data:
            parx   = self._req_data["parx"]
        
        if "sql" in parx:
            sqls   = parx["sql"]
        else: sqls=''
        
        #outmode = self._req_data["outmode"]
        outmode='html'
        parx = {'count':1}
       
        self._init1(sqls, outmode, parx)
        
        if ( outmode!="csv" ) :
            self.form1()
        
 
        
        if self.sqls != ''  :    
            self.doit( db_obj )
        
               
    
    def form1(self):
        
        parx = {}
        if 'parx' in self._req_data:
            parx = self._req_data['parx']
        
        if "sql" not in parx:
            parx["sql"]=''  
        
        initarr   = {}
        
        initarr["title"]       = "Execute SQL command"
        initarr["startform"]   = 1 
        initarr["submittitle"] = "Submit"
    
        hiddenarr = {}
        hiddenarr["mod"]      = self._mod      
        self.formobj = form(initarr, hiddenarr, 0)

        fields = []
        fieldx = {
            "title" : "sql COMMAND", 
            "name"  : "sql",
            "object": "textarea",
            "val"   : parx['sql'], 
            "inits" : {'cols':120, 'rows':4},
            "notes" : "SQL command"
            }
        fields.append(fieldx)
        self.formobj.set_form_defs(fields)
        

        
    def mainframe(self):
        
        db_obj = self._db_obj1
        
        debug.printx(__name__, "REQUEST:"+ str(self._req_data) )

        massdata = {}
        
        formdata = self.formobj.get_template_data()
        massdata['form'] = formdata
        massdata['data'] = self.data
        massdata['text_array'] = self.text_array
        self.sh_main_layout(massdata = massdata )          

        

        
        
             
