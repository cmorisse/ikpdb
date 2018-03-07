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
DEBUGGED_PROGRAM = "ikpdb/tests/debugged_programs/test03_suspend.py"

class TestCase03Suspend(unittest.TestCase):
    
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
        self.dp = subprocess.Popen(cmd_line, stdout=subprocess.PIPE)
        time.sleep(0.4)  # allows debugger to start
        self.ikpdb = IKPdbClient(TESTED_IKPDB_HOST, TESTED_IKPDB_PORT)

    def tearDown(self):
        if self.dp:
            self.dp.kill()
            time.sleep(1)

    def test_01_suspend(self):
        """Launch a debugged program and suspend."""
        time.sleep(0.2)  # allows debugger to start
        self.ikpdb.run_script()

        #time.sleep(0.2)  # allow running program to enter loop
        msg_id = self.ikpdb.send('suspend')
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to 'suspend'.")

        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], 'programBreak', "Unexpected reply to 'suspend'.")
        a_var_dump = filter(lambda e:e['name']=='loop', i_msg['frames'][0]['f_locals'])
        print("suspended while loop=%s" % a_var_dump[0]['value'])

    def test_02_set_trace(self):
        """Launch a debugged program and wait for it break on set_trace()"""
        time.sleep(0.2)  # allows debugger to start
        self.ikpdb.run_script()

        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], 'programBreak', "Unexpected message received.")
        self.assertEqual(i_msg['result']['executionStatus'], 'stopped', "Unexpected break.")
        self.assertEqual(i_msg['frames'][0]['line_number'], 14, "broke on unexpected line number.")

    def test_03_Exception(self):
        """Launch a debugged program and wait for it to raise an Exception"""
        time.sleep(0.2)  # allows debugger to start
        self.ikpdb.run_script()

        # first break on set_trace()
        i_msg = self.ikpdb.receive()
        self.ikpdb.resume()

        # final break on exception
        i_msg = self.ikpdb.receive()
        self.assertEqual(i_msg['command'], 'programBreak', "Unexpected message received.")
        self.assertIsNotNone(i_msg['exception'], "Expected exception not received.")

