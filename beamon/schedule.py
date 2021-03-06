"""
.. module:: schedule.py
   :platform: Unix
   :synopsis: Interact with information from the APS online schedule.

.. moduleauthor:: David Vine <djvine@gmail.com>

This module is largely John Hammonds work to which I'll be adding
some scripts as needed.
"""

from suds.wsse import Security, UsernameToken
from suds.client import Client
from suds.transport.https import HttpAuthenticated
import logging
import sys
import datetime
import traceback
import urllib2
import httplib
from xml.sax import SAXParseException
import ipdb
from collections import defaultdict
import ConfigParser
import socket
cf = ConfigParser.ConfigParser()

debug = False
""" You must use the APS web password. You can check it by logging into
the proposal system. Be careful because this system also accepts LDAP
account info.

The credentials are stored in a '.ini' file and read by python.
 - Create a file called 'credentials.ini',
 - Put the following text in it:
 [credentials]
 username = YOUR BADGE NUMBER
 password = YOUR APS WEB PASSWORD



 that's it.

"""
if socket.gethostname()=='dawn':
    cf.read('/home/david/python/beamon/beamon/credentials.ini')
    base = 'https://schedule.aps.anl.gov/beamschedds/springws/'
else:
    cf.read('/local/beamon/beamon/credentials.ini')
    base = 'https://schedule.aps.anl.gov:8443/beamschedds/springws/'
username = cf.get('credentials', 'username')
password = cf.get('credentials', 'password')
# Uncomment this for INTERNAL network
#base = 'https://schedule.aps.anl.gov:8443/beamschedds/springws/'
# Uncomment this for EXTERNAL network
#base = 'https://schedule.aps.anl.gov/beamschedds/springws/'

class HTTPSConnectionV3(httplib.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        try:
            print ("using connection")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, \
                                        ssl_version=ssl.PROTOCOL_SSLv3)
        except ssl.SSLError, e:
            print("Trying SSLv3.")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, \
                                        ssl_version=ssl.PROTOCOL_SSLv23)

class HTTPSHandlerV3(urllib2.HTTPSHandler):
    def https_open(self, req):
        print "using this opener"
        return self.do_open(HTTPSConnectionV3, req)

def setSoapHeader(client, username, password):
    security = Security()
    token = UsernameToken(username, password)
    token.setcreated()
    security.tokens.append(token)
    if debug:
        print security
    client.set_options(wsse=security)

def findRunName(startDate, endDate):
    """Find the official run name for the run that spans the
    given startDate and endDate

    Returns string."""
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
    try:
        result = runScheduleServiceClient.service.findAllRuns()
    except Exception:
        print "ERROR in findRunName"
        sys.exit(2)
    except soapFault:
        print "ERROR in findRunName"
        print soapFault
        sys.exit(2)
    runArray = result.run
    runName = None
    for run in runArray:

        try:
            if startDate >= run.startTime and endDate <= run.endTime:
                runName = run.runName
                break
        except Exception as ex:
            print "ERROR caught in findRunName:" + str(ex)
            print startDate
            print run.startTime
            print endDate
            print run.endTime
            raise ex
    return runName


def findBeamlineSchedule(beamlineName, runName):
    """Find beamline schedule for given beamlineName and runName"""

    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
    try:
        result  = beamlineScheduleServiceClient.service.findBeamlineSchedule(beamlineName, runName)
    except SAXParseException as ex:
        print "ERROR in findBeamlineSchedule\n"
        traceback.print_exc()
        sys.exit(2)

    return result

def findBeamtimeRequestsByBeamline(beamlineName, runName):
    """Find beamline schedule for given beamlineName and runName

    Returns schedule object."""
    try:
        result  = beamlineScheduleServiceClient.service.findBeamtimeRequestsByBeamline(beamlineName, runName)
    except SAXParseException:
        print "ERROR in findBeamtimeRequestsByBeamline"
    except Exception:
        print "ERROR in findBeamtimeRequestByBeamline\n"
        traceback.print_exc()
        sys.exit(2)
    return result

def setup_connection():
    result = urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))
    logging.raiseExceptions = 0

    beamlineScheduleServiceURL = base + \
         'beamlineScheduleService/beamlineScheduleWebService.wsdl'

    runScheduleServiceURL = base + \
         'runScheduleService/runScheduleWebService.wsdl'

    try:
        credentials = dict(username=username, password=password)
        t = HttpAuthenticated(**credentials)
        if debug:
            print t.u2handlers()
            print t.credentials()
        runScheduleServiceClient = Client(runScheduleServiceURL)
        runScheduleServiceClient.options.cache.setduration(seconds=10)
        result = setSoapHeader(runScheduleServiceClient, username, password)
        beamlineScheduleServiceClient = Client(beamlineScheduleServiceURL)
        beamlineScheduleServiceClient.options.cache.setduration(seconds=10)
        result = setSoapHeader(beamlineScheduleServiceClient, username, password)
    except Exception, ex:
        print "CANNOT OPEN SERVICES:" + str(ex)
        raise
        exit(-1)

    return runScheduleServiceClient, beamlineScheduleServiceClient

def get_users(beamline='2-ID-E', date=None):
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
    if not date:
        date = datetime.datetime.now()
    run_name = findRunName(date, date)
    schedule = findBeamlineSchedule(beamline, run_name)

    events = schedule.activities.activity
    users = defaultdict(dict)
    for event in events:
        try:
            if event.activityType.activityTypeName in ['GUP', 'PUP', 'rapid-access']:
                if date >= event.startTime and date <= event.endTime:
                        for experimenter in event.beamtimeRequest.proposal.experimenters.experimenter:
                            for key in experimenter.__keylist__:
                                users[experimenter.lastName][key] = getattr(experimenter, key)
        except:
            ipdb.set_trace()
            raise

    return users

def get_pi(beamline='2-ID-E', date=None):
    pi = 'Comm'
    users = get_users(beamline, date)
    for user in users:
    	for key in users[user].keys():
	    if key=='piFlag':
	        pi = user
		break
    return pi

if __name__ == '__main__':

    now = datetime.datetime.now()
    runScheduleServiceClient, beamlineScheduleServiceClient = setup_connection()
    print(findRunName(now, now))
    #print(get_users('2-ID-B', datetime.datetime(2014, 11, 5, 10)))
    print(get_users('2-ID-E', datetime.datetime(2014, 10, 9, 10)))
    print(get_pi('2-ID-E', datetime.datetime(2014, 10, 9, 10)))

