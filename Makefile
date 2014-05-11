PY=/usr/bin/env python
NOSE=/usr/bin/nosetests -s -v --with-xunit
GIT=/usr/bin/git
RPM=/bin/rpm
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
TEST=top.tests:TestLoader \
	 top.tests:TestLoaderIpec \
	 top.tests:TestParser \
	 top.tests:TestStopParser \
	 top.tests:TestAdpParser \
	 top.tests:TestReporter \
	 top.tests:TestEmailerBase \
	 top.tests:TestEmailer \
	 top.tests:TestRest \
	 top.tests:TestRestEmailer \
	 top.tests:TestRestSmser \
	 top.tests:TestDaemonService \
	 top.tests:TestLoaderDaemon \
	 top.tests:TestOnDeliveryDaemon \
	 top.tests:TestCommsDaemon \
	 top.tests:TestReminderDaemon \
	 top.tests:TestMapperDaemon \
	 top.tests:TestFilterDaemon \
	 top.tests:TestAdpDaemon \
	 top.tests:TestPodTranslatorDaemon \
	 top.tests:TestReporterDaemonUncollected \
	 top.tests:TestReporterDaemonCompliance \
	 top.tests:TestReporterDaemonNonCompliance \
	 top.tests:TestReporterDaemonException \
	 top.tests:TestReporterDaemonTotals \
	 top.tests:TestReporterDaemonCollected \
	 top.tests:TestExporter \
	 top.tests:TestExporterIpec \
	 top.tests:TestExporterFast \
	 top.tests:TestConfig \
	 top.b2cconfig.tests:TestB2CConfig \
	 top.b2cconfig.tests:TestCommsB2CConfig \
	 top.b2cconfig.tests:TestExporterB2CConfig \
	 top.b2cconfig.tests:TestReporterB2CConfig \
	 top.b2cconfig.tests:TestHealthB2CConfig \
	 top.b2cconfig.tests:TestReminderB2CConfig \
	 top.b2cconfig.tests:TestMapperB2CConfig \
	 top.b2cconfig.tests:TestPodB2CConfig \
	 top.b2cconfig.tests:TestOnDeliveryB2CConfig \
	 top.b2cconfig.tests:TestFilterB2CConfig \
	 top.b2cconfig.tests:TestAdpB2CConfig \
	 top.tests:TestFtp \
	 top.tests:TestService \
	 top.tests:TestReminder \
	 top.tests:TestOnDelivery \
	 top.tests:TestAdp \
	 top.tests:TestInit \
	 top.tests:TestComms \
	 top.tests:TestMapper \
	 top.tests:TestFilter \
	 top.tests:TestAuditer \
	 top.report.tests:TestUncollected \
	 top.report.tests:TestCompliance \
	 top.report.tests:TestNonCompliance \
	 top.report.tests:TestException \
	 top.report.tests:TestTotals \
	 top.report.tests:TestCollected \
	 top.tests:TestWriter \
	 top.tests:TestXlwriter \
	 top.table.tests:TestAgent \
	 top.table.tests:TestJob \
	 top.table.tests:TestJobItem \
	 top.table.tests:TestTable \
	 top.table.tests:TestIdentityType \
	 top.table.tests:TestTransSend \
	 top.table.tests:TestAgentStocktake \
	 top.table.tests:TestParcelSize \
	 top.table.tests:TestDeliveryPartner \
	 top.table.tests:TestLoginAccount \
	 top.table.tests:TestSystemLevelAccess \
	 top.table.tests:TestLoginAccess \
	 top.table.tests:TestReturnsReference \
	 top.table.tests:TestReturns \
	 top.tests:TestDbSession \
	 top.tests:TestOraDbSession \
	 top.utils.tests:TestFiles \
	 top.utils.tests:TestUtils \
	 top.utils.tests:TestSetter \
	 top.tests:TestPostcode \
	 top.tests:TestTimezone \
	 top.tests:TestPodTranslator

sdist:
	$(PY) setup.py sdist

rpm:
	$(PY) setup.py bdist_rpm

docs:
	PYTHONPATH=$(PYTHONPATH) sphinx-build -b html doc/source doc/build

build: docs rpm

test:
	$(NOSE) $(TEST)

uninstall:
	$(RPM) -e python-top


install:
	$(RPM) -ivh dist/python-top-?.??-?.noarch.rpm

upgrade:
	$(RPM) -Uvh dist/python-top-?.??-?.noarch.rpm

clean:
	$(GIT) clean -xdf
	\rm -fr /tmp/tmp*
	\rm -fr /tmp/v*

.PHONY: docs rpm test
