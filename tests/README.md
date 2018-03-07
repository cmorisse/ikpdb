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
* Automate tests with a Makefile
* Make it an independent repo so that it can test ikpdb and ikp3db
* 
