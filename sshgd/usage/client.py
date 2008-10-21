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
    def getCommand(self, prespective):
        return prespective.callRemote("getRepos").addCallback(self.showReturned)

    def showReturned(self, result):
        if result:
            print result
        else:
            print "No repositories available"

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

        factory = AdminClientFactory()
        ctx = factory.getContext(self.opts)
        deferred = factory.login(self.opts.get("certificate"))
        deferred.addCallback(self.subOptions.getCommand)
        deferred.addCallback(self.stop).addErrback(self.stop)
        reactor.connectSSL(self.opts.get('host'),
                           self.opts.get('port'),
                           factory,
                           ctx)

    def stop(self, traceback):
        if traceback:
            print "Something went wrong"
            print traceback.getTraceback()
        try:
            reactor.stop()
        except:
            # Reactor might not yet be running
            pass

if __name__ == '__main__':
    parser = ClientOptions()
    try:
        parser.parseOptions() # When given no argument, parses sys.argv[1:]
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)

    reactor.run()

