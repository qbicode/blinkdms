# debug class
from flask import session

class debug:
    
    def printx(funcname, text, min_debug_lev=0):
        '''
        static method
        '''
        debug_level = 0
        if 'user_glob' in session:
            tmp = session['user_glob'].get('debug.level', '0')
            try:
                debug_level = int(tmp)
            except:
                debug_level = 0  # ignore this error ...

        if debug_level >= min_debug_lev:
            print('DEBUG_OUT: ' + funcname + ': ' + text)
