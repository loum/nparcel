PY=/usr/bin/env python
NOSE=/usr/bin/nosetests -s -v
GIT=/usr/bin/git
PYTHONPATH=.

# The TEST variable can be set to allow you to control which tests
# to run.  For example, if the current project has a test set defined at
# "tests/test_<name>.py", to run the "Test<class_name>" class:
#
# $ make test TEST=tests:Test<class_name>
#
# To run individual test cases within each test class:
#
# $ make test TEST=tests:Test<class_name>.test_<test_name>
#
# Note: for this to work you will need to import the test class into
# the current namespace via "tests/__init__.py"
TEST=nparcel.tests:TestLoader \
	 nparcel.tests:TestLoaderIpec \
	 nparcel.tests:TestParser \
	 nparcel.tests:TestStopParser \
	 nparcel.tests:TestDbSession \
	 nparcel.tests:TestReporter \
	 nparcel.tests:TestEmailer \
	 nparcel.tests:TestRest \
	 nparcel.tests:TestRestEmailer \
	 nparcel.tests:TestRestSmser \
	 nparcel.tests:TestDaemonService \
	 nparcel.tests:TestLoaderDaemon \
	 nparcel.tests:TestPrimaryElectDaemon \
	 nparcel.tests:TestCommsDaemon \
	 nparcel.tests:TestReminderDaemon \
	 nparcel.tests:TestMapperDaemon \
	 nparcel.tests:TestExporter \
	 nparcel.tests:TestExporterIpec \
	 nparcel.tests:TestConfig \
	 nparcel.tests:TestB2CConfig \
	 nparcel.tests:TestFtp \
	 nparcel.tests:TestService \
	 nparcel.tests:TestReminder \
	 nparcel.tests:TestPrimaryElect \
	 nparcel.tests:TestInit \
	 nparcel.tests:TestComms \
	 nparcel.tests:TestMapper \
	 nparcel.tests:TestMts \
	 nparcel.table.tests:TestAgent \
	 nparcel.table.tests:TestJob \
	 nparcel.table.tests:TestJobItem \
	 nparcel.table.tests:TestTable \
	 nparcel.table.tests:TestIdentityType \
	 nparcel.utils.tests:TestFiles

sdist:
	$(PY) setup.py sdist

rpm:
	$(PY) setup.py bdist_rpm

docs:
	PYTHONPATH=$(PYTHONPATH) sphinx-build -b html doc/source doc/build

build: docs rpm

test:
	$(NOSE) $(TEST)

clean:
	$(GIT) clean -xdf

.PHONY: docs rpm test
