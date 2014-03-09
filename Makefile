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
	 nparcel.tests:TestAdpParser \
	 nparcel.tests:TestReporter \
	 nparcel.tests:TestEmailerBase \
	 nparcel.tests:TestEmailer \
	 nparcel.tests:TestRest \
	 nparcel.tests:TestRestEmailer \
	 nparcel.tests:TestRestSmser \
	 nparcel.tests:TestDaemonService \
	 nparcel.tests:TestLoaderDaemon \
	 nparcel.tests:TestOnDeliveryDaemon \
	 nparcel.tests:TestCommsDaemon \
	 nparcel.tests:TestReminderDaemon \
	 nparcel.tests:TestMapperDaemon \
	 nparcel.tests:TestFilterDaemon \
	 nparcel.tests:TestAdpDaemon \
	 nparcel.tests:TestReporterDaemonUncollected \
	 nparcel.tests:TestReporterDaemonCompliance \
	 nparcel.tests:TestReporterDaemonNonCompliance \
	 nparcel.tests:TestReporterDaemonException \
	 nparcel.tests:TestReporterDaemonTotals \
	 nparcel.tests:TestReporterDaemonCollected \
	 nparcel.tests:TestExporter \
	 nparcel.tests:TestExporterIpec \
	 nparcel.tests:TestExporterFast \
	 nparcel.tests:TestConfig \
	 nparcel.tests:TestB2CConfig \
	 nparcel.tests:TestCommsB2CConfig \
	 nparcel.tests:TestFtp \
	 nparcel.tests:TestService \
	 nparcel.tests:TestReminder \
	 nparcel.tests:TestOnDelivery \
	 nparcel.tests:TestAdp \
	 nparcel.tests:TestInit \
	 nparcel.tests:TestComms \
	 nparcel.tests:TestMapper \
	 nparcel.tests:TestFilter \
	 nparcel.tests:TestAuditer \
	 nparcel.report.tests:TestUncollected \
	 nparcel.report.tests:TestCompliance \
	 nparcel.report.tests:TestNonCompliance \
	 nparcel.report.tests:TestException \
	 nparcel.report.tests:TestTotals \
	 nparcel.report.tests:TestCollected \
	 nparcel.tests:TestWriter \
	 nparcel.tests:TestXlwriter \
	 nparcel.table.tests:TestAgent \
	 nparcel.table.tests:TestJob \
	 nparcel.table.tests:TestJobItem \
	 nparcel.table.tests:TestTable \
	 nparcel.table.tests:TestIdentityType \
	 nparcel.table.tests:TestTransSend \
	 nparcel.table.tests:TestAgentStocktake \
	 nparcel.table.tests:TestParcelSize \
	 nparcel.table.tests:TestDeliveryPartner \
	 nparcel.table.tests:TestLoginAccount \
	 nparcel.table.tests:TestSystemLevelAccess \
	 nparcel.table.tests:TestLoginAccess \
	 nparcel.table.tests:TestReturnsReference \
	 nparcel.table.tests:TestReturns \
	 nparcel.tests:TestDbSession \
	 nparcel.tests:TestOraDbSession \
	 nparcel.utils.tests:TestFiles \
	 nparcel.utils.tests:TestUtils \
	 nparcel.tests:TestPostcode \
	 nparcel.tests:TestTimezone

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
	\rm -fr /tmp/tmp*
	\rm -fr /tmp/v*

.PHONY: docs rpm test
