Tests running instructions (Temporary)
======================================

Create a virtualenv named py27tests in ikpdb/tests
* cd /home/ubuntu/workspace
* cd tests
* virtualenv --python=python2 py27tests
* source py27tests/bin/activate
* cd /home/ubuntu/workspace
* python ikpdb/tests/run_tests.py 


Notes:

* ikpdb_client.py is a WIP for a python (remote) client for IKPdb and IKP3db
* tests can be debugged using IKPdb on cloud9


TODO:
=====

* Increase test coverage - WIP
* Add Test for bug on evaluate() called before runscript()
* Add Test to reproduce gc object if already tracked (step out from line 4 in debugged_programs/flask01.py)
* Automate tests with a Makefile
* Make it an independent repo so that it can test ikpdb and ikp3db
* 
