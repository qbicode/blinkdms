import unittest
# from flask import session

from test._test_subs.real_server import Blink_UT_Real_Cls

class TestMockServer(Blink_UT_Real_Cls):
    
    user='testX'
    
    def test_1(self):
        self.called = False
        
        argu = { 'context':'ACTIVE' }
        result = self.rpc_call("sys_set", argu) 

        argu = { 'id':1 }
        result = self.rpc_call("doc_view", argu)        
        print ("RESULT: "  + str(result) )
                

        #self.assertEqual(200, response.status_code)
        #self.assertTrue( type(result_data)==dict )


if __name__ == '__main__':
    unittest.main()

