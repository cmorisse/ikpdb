# coding: utf-8

import unittest
import os
import subprocess
import time
import socket
import logging
import json
from ikpdb_client import IKPdbClient

_logger = logging.getLogger(__file__)
_logger.addHandler(logging.StreamHandler())
_logger.setLevel(logging.INFO)


PYTHON_EXEC = "ikpdb/tests/py27tests/bin/python"
TESTED_IKPDB_HOST = '127.0.0.1'
TESTED_IKPDB_PORT = 15999
DEBUGGED_PROGRAM = "ikpdb/tests/debugged_programs/test02_breakpoints.py"

class TestCase02Breakpoints(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass    

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        cmd_line = [
            PYTHON_EXEC, 
            "-m", "ikpdb", 
            #"--ikpdb-log=9NB",
            #"--ikpdb-log=9",
            "--ikpdb-port=%s" % TESTED_IKPDB_PORT,
            #"--ikpdb-welcome",
            DEBUGGED_PROGRAM,
            "t02" 
        ]
        self.dp = subprocess.Popen(cmd_line,
                                   stdout=subprocess.PIPE)
        time.sleep(0.4)  # allows debugger to start
        self.ikpdb = IKPdbClient(TESTED_IKPDB_HOST, TESTED_IKPDB_PORT)

    def tearDown(self):
        if self.dp:
            self.dp.kill()
            time.sleep(1)

    def test_01_setBreakpoint(self):
        """Launch a debugged program and connect to debugger."""
        
        # set a breakpoint and launch
        msg_id = self.ikpdb.send('setBreakpoint',
                                 file_name='ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=5,
                                 enabled=True)
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to setBreakpoint.")
        self.assertEqual(i_msg['commandExecStatus'], 'ok', "Failed to setBreakpoint.")
        
        time.sleep(0.2)  # allows debugger to start
        reply_msg = self.ikpdb.run_script()

        # Wait for breakpoint
        # Note that when debugging this file you must run straight from runScript to next receive()
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], "programBreak", "programBreak message not received.")
        self.assertEqual(i_msg['exception'], None, "Unexpected exception raised.")
        top_frame = i_msg['frames'][0]
        self.assertEqual(top_frame['file_path'], 
                         'ikpdb/tests/debugged_programs/test02_breakpoints.py', 
                         "programBreak on unexpected file.")
        self.assertEqual(top_frame['line_number'], 5, "programBreak on unexpected line number.")


    def test_02_getBreakpoints(self):
        """Launch debugger, run program and wait termination"""

        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=5)

        msg_id = self.ikpdb.send('getBreakpoints')
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to getBreakpoints.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "getBreakpoints failed.")
        self.assertEqual(len(i_msg['result']), 1, "Wrong number of breakpoints returned.")
        self.assertEqual(i_msg['result'][0]['line_number'], 5, "Wrong breakpoint returned.")

    def test_03_changeBreakpointState(self):
        """Test disable a breakpoint and set a condition"""
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=5)

        msg_id = self.ikpdb.send('changeBreakpointState',
                                 breakpoint_number=0,
                                 enabled=False,
                                 condition='')
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'changeBreakpointState' enabled.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "'changeBreakpointState' command failed.")

        bp_list = self.ikpdb.get_breakpoints()
        self.assertEqual(len(bp_list), 1, "Wrong number of breakpoints returned.")
        self.assertEqual(bp_list[0]['line_number'], 5, "Wrong breakpoint returned.")
        self.assertFalse(bp_list[0]['enabled'], "'changeBreakpointState' failed.")

        msg_id = self.ikpdb.send('changeBreakpointState',
                                 breakpoint_number=0,
                                 enabled=True,
                                 condition='a_var==1')
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'changeBreakpointState' condition.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "'changeBreakpointState' command failed.")

        bp_list = self.ikpdb.get_breakpoints()
        self.assertEqual(len(bp_list), 1, "Wrong number of breakpoints returned.")
        self.assertEqual(bp_list[0]['line_number'], 5, "Wrong breakpoint returned.")
        self.assertEqual(bp_list[0]['condition'], 'a_var==1', "'changeBreakpointState' failed to set condition.")


    def test_04_conditionalBreakpoint(self):
        """Test that conditional breakpoints and enabled flag are correctly managed."""
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=5,
                                 enabled=False)
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=6,
                                 condition='a_var==50',
                                 enabled=False)
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=8,
                                 condition='a_var==50',
                                 enabled=True)

        self.ikpdb.run_script()
        
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], "programBreak", "programBreak message not received.")
        self.assertEqual(i_msg['exception'], None, "Unexpected exception raised.")
        top_frame = i_msg['frames'][0]
        self.assertEqual(top_frame['file_path'], 
                         'ikpdb/tests/debugged_programs/test02_breakpoints.py', 
                         "programBreak on unexpected file.")
        self.assertEqual(top_frame['line_number'], 8, "programBreak on unexpected line number.")
        a_var_dump = filter(lambda e:e['name']=='a_var', top_frame['f_locals'])
                
        self.assertEqual(len(a_var_dump), 1, "local a_var not found.")
        self.assertEqual(a_var_dump[0]['value'], '50', "wrong value for a_var. expecting '50' got '%s'" % a_var_dump[0]['value'])
        

    def test_05_clearBreakpoint(self):
        """Test breakpoints deletion."""
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=5,
                                 enabled=False)
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=6,
                                 condition='a_var==1',
                                 enabled=True)
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=7,
                                 condition='a_var==50',
                                 enabled=True)


        msg_id = self.ikpdb.send('clearBreakpoint', breakpoint_number=0)
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'clearBreakpoint'.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "'clearBreakpoint' command failed.")

        msg_id = self.ikpdb.send('clearBreakpoint', breakpoint_number=2)
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'clearBreakpoint'.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "'clearBreakpoint' command failed.")
        
        bp_list = self.ikpdb.get_breakpoints()
        self.assertEqual(len(bp_list), 1, "Wrong number of breakpoints returned.")
        self.assertEqual(bp_list[0]['line_number'], 6, "Wrong breakpoint returned.")

        self.ikpdb.run_script()

        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], "programBreak", "programBreak message not received.")
        self.assertEqual(i_msg['exception'], None, "Unexpected exception raised.")
        top_frame = i_msg['frames'][0]
        self.assertEqual(top_frame['file_path'], 
                         'ikpdb/tests/debugged_programs/test02_breakpoints.py', 
                         "programBreak on unexpected file.")
        self.assertEqual(top_frame['line_number'], 6, "programBreak on unexpected line number.")

        a_var_dump = filter(lambda e:e['name']=='a_var', top_frame['f_locals'])
        self.assertEqual(len(a_var_dump), 1, "local a_var not found.")
        self.assertEqual(a_var_dump[0]['value'], '1', "wrong value for a_var. expecting '1' got '%s'" % a_var_dump[0]['value'])
        
    def test_06_changeBreakpointState(self):
        """Test breakpoints modification.
        
        set 3 breakpoints at line 5,6,8. Last one with a condition preventing break
        runScript
        break at line 5
        disable breakpoint at line 6 (second)
        modify condition on last breakpoint so that it will trigger
        resume
        check that last breakpoint triggers
        """
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=5,
                                 enabled=True)
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=6,
                                 condition='a_var==1',
                                 enabled=True)
        self.ikpdb.set_breakpoint('ikpdb/tests/debugged_programs/test02_breakpoints.py',
                                 line_number=8,
                                 condition='a_var==60',
                                 enabled=True)

        self.ikpdb.run_script()

        # break at line 5
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], "programBreak", "programBreak message not received.")
        self.assertEqual(i_msg['exception'], None, "Unexpected exception raised.")
        top_frame = i_msg['frames'][0]
        self.assertEqual(top_frame['file_path'], 
                         'ikpdb/tests/debugged_programs/test02_breakpoints.py', 
                         "programBreak on unexpected file.")
        self.assertEqual(top_frame['line_number'], 5, "programBreak on unexpected line number.")
        
        # disable breakpoint at line 6 (second)
        msg_id = self.ikpdb.send('changeBreakpointState', 
                                 breakpoint_number=1,
                                 enabled=False)
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'clearBreakpoint'.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "'changeBreakpoint' command failed.")
                
        # modify condition on last breakpoint so that it will trigger
        msg_id = self.ikpdb.send('changeBreakpointState', 
                                 breakpoint_number=2,
                                 enabled=True,
                                 condition="a_var==50")
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'clearBreakpoint'.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "'changeBreakpoint' command failed.")

        bp_list = self.ikpdb.get_breakpoints()

        # resume()
        msg_id = self.ikpdb.send('resume')
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'clearBreakpoint'.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "'resume' command failed.")
        self.assertEqual(i_msg['result'].get('executionStatus'), 'running', "'resume' command failed.")

        # check that last breakpoint triggers
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], "programBreak", "programBreak message not received.")
        self.assertEqual(i_msg['exception'], None, "Unexpected exception raised.")
        top_frame = i_msg['frames'][0]
        self.assertEqual(top_frame['file_path'], 
                         'ikpdb/tests/debugged_programs/test02_breakpoints.py', 
                         "programBreak on unexpected file.")
        self.assertEqual(top_frame['line_number'], 8, "programBreak on unexpected line number.")



        
        


