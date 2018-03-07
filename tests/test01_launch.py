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
DEBUGGED_PROGRAM = "ikpdb/tests/debugged_programs/test01_launch.py"

class TestCase01Launch(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        #print("CWD")
        #print(os.getcwd())
        #p = subprocess.Popen(["python", "-m", "ikpdb", "tests/debugged_programs/test01_connect.py" ])
        #print(p)
        pass
    
    
    def setUp(self):
        pass
        #print("setUp")

    def tearDown(self):
        pass
        #print("tearDown")

    def test_01_launch_file_not_exists(self):
        """ Launch a non existent debugged program and get an error"""
        # launch the debugger
        # connects to it
        # get the welcome message
        cmd_line = [
            PYTHON_EXEC, 
            "-m", 
            "ikpdb", 
            "ikpdb/tests/debugged_programs/wwwwwwwwwwwwwww.py"
        ]
        res = subprocess.Popen(cmd_line,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        output, _ = res.communicate()
        self.assertEqual(res.returncode, 1, "Wrong exit code. Expected 1, got '%s'" % res.returncode)
        self.assertTrue(output.endswith("Error: 'ikpdb/tests/debugged_programs/wwwwwwwwwwwwwww.py' does not exist.\n"),
                        "Unexpected message.")

    def test_02_connect(self):
        """Launch a debugged program and connect to debugger."""
        cmd_line = [
            PYTHON_EXEC, 
            "-m", "ikpdb", 
            #"--ikpdb-log=9N",
            "--ikpdb-port=%s" % TESTED_IKPDB_PORT,
            #"--ikpdb-welcome",
            DEBUGGED_PROGRAM,
            "t02"
        ]
        dp = subprocess.Popen(cmd_line,
                              stdout=subprocess.PIPE)
        time.sleep(0.2)
        
        # connect to debugger
        ikpdb = IKPdbClient(TESTED_IKPDB_HOST, TESTED_IKPDB_PORT)

        # end debugged program
        # TODO: Why do we need to kill in tests while behaviour is ok when running
        dp.kill()
        time.sleep(1) 

    def test_03_runScript(self):
        """Launch debugger, run program and wait termination"""
        # We need to change port to avoid addr et port used errors
        TESTED_IKPDB_PORT = 16000  
        cmd_line = [
            PYTHON_EXEC, 
            "-m", "ikpdb", 
            #"--ikpdb-log=9N",
            "--ikpdb-port=%s" % TESTED_IKPDB_PORT,
            #"--ikpdb-welcome",
            DEBUGGED_PROGRAM,
            "t03"
        ]
        
        # Allow PORT to be recycled
        dp = subprocess.Popen(cmd_line,
                              stdout=subprocess.PIPE)
        time.sleep(0.2)  # Give Ikpdb enough time to boot
        # connect to debugger
        ikpdb = IKPdbClient(TESTED_IKPDB_HOST, TESTED_IKPDB_PORT)
        time.sleep(0.4)  # Give Ikpdb enough time to boot

        msg_id = ikpdb.send('runScript')
        
        i_msg = ikpdb.receive()
        self.assertEqual(i_msg['_id'], msg_id, "Unexpected reply to runScript command.")
        self.assertEqual(i_msg['commandExecStatus'], "ok", "IKPdb failed to run debugged program.")

        i_msg = ikpdb.receive()
        self.assertEqual(i_msg['command'], "programEnd", "programEnd message not received.")
        self.assertEqual(i_msg['result']['exit_code'], None, "Unexpected exit code.")

        # TODO: Why do we need to kill in tests while behaviour is ok when running
        dp.kill()  
        # Allow PORT to be recycled
        time.sleep(1) 


