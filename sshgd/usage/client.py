# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os

from twisted.python import usage, log

from twisted.plugin import IPlugin
from twisted.application import internet
from twisted.application.service import IServiceMaker, MultiService
from twisted.internet import reactor

from zope.interface import implements
try:
    from sshgd.usage.base import BaseOptions
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath("."))
    from sshgd.usage.base import BaseOptions

from sshgd.factories import AdminClientFactory
from sshgd.creds import ClientCertificate

class GetReposOpts(BaseOptions):
    def run(self, prespective):
        print "foo", prespective
        prespective.callRemote("getRepos").addCallback(self.showReturned)

    def showReturned(self, result):
        print result
        reactor.stop()

class ClientOptions(BaseOptions):

    optParameters = [
        ["port", "P", 4444,
         "The port to run the configuration server", int],
        ["host", "H", "localhost", "The configuration server host address"],
        ["certificate", "f", ".ssh/client.pem", "private key file path"],
        ["cacert", "c", ".ssh/cacert.pem", "Root CA certificate file path"],
    ]

    subCommands = [
        ["repos", None, GetReposOpts , "repos comdands"]
    ]

    def postOptions(self):
        # Convert the parsed options to their respective types and
        # paths to absolute paths
        super(ClientOptions, self).postOptions()
        self.opts['certificate'] = os.path.abspath(
                            os.path.expanduser(self.opts.get('certificate')))
        self.opts['cacert'] = os.path.abspath(
                            os.path.expanduser(self.opts.get('cacert')))
        import sys
        print repr(self.opts)
#        print repr(self.parent.opts)
        print "foo 1"
        self.realstdout = sys.stdout

    def getService(self):
        import sys
        print "foo 2"
        sys.stdout = sys.__stdout__
        factory = AdminClientFactory()
        ctx = factory.getContext(self.opts)
#        return internet.SSLClient(self.opts.get('host'),
#                                   self.opts.get('port'),
#                                   factory,
#                                   ctx) #.addErrback(stop)
        reactor.connectSSL(self.opts.get('host'),
                           self.opts.get('port'),
                           factory,
                           ctx)
        credentials = ClientCertificate(self.opts.get("certificate"))
        d = factory.login(self.opts.get("certificate"))
#        d = factory.sendCommand("getRepos")
        d.addCallback(get_repos).addErrback(stop)


def get_repos(perspective):
    print "got perspective ref:", perspective
    print "asking it to getRepos()"
    back = perspective.callRemote("getRepos")
    def foo(b):
        import sys
        print >> sys.stderr, b
    print "Got:", back.addCallback(foo).addCallback(stop)

def stop(failure):
    if failure:
        print 111, failure.getTraceback()
    reactor.stop()

if __name__ == '__main__':
    parser = ClientOptions()
    try:
        parser.parseOptions() # When given no argument, parses sys.argv[1:]
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)

    parser.getService()

    reactor.run()

#    parser.run()
