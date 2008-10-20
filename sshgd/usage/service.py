# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
from ConfigParser import SafeConfigParser

from sshgd.usage import BaseOptions, certs, client, config, server

from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker, MultiService
from zope.interface import implements

class SSHgDOptions(BaseOptions):
    optParameters = [
        ["config", "C", None, "Configuration file"]
    ]
    subCommands = [
        ["server", None, server.MercurialServerOptions,
         "Mercurial SSH service"],
        ["config", None, config.ConfigServerOptions,
         "Configuration server service"],
        ["client", None, client.ClientOptions, "Configuration client"],
        ["certs", None, certs.CertsCreatorOptions, "Certificates creator"]
    ]

    runnedPostOption = False

    def postOptions(self):
        if self.runnedPostOption: return
        if self.opts.get('config'):
            config_file = self.opts['config'] = os.path.abspath(
                os.path.expanduser(self.opts.get('config'))
            )
        self.runnedPostOption = True

#    def getServices(self):
#        for name, sname, command, description in self.subCommands:
#            yield command.getService()

class ServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "sshgd" #__package__.lower()
    description = "foo" #__summary__
    options = SSHgDOptions

    def makeService(self, options):
        return options.subOptions.getService()
#        master_service = MultiService()
#        service = options.subOptions.getService()
#        service.setServiceParent(master_service)
#        print options.subCommand
#        print dir(self)
#
#        import sys
#        sys.stdout = sys.__stdout__
#        return master_service


if __name__ == '__main__':
    import os, sys
    from twisted.python import usage

    sys.path.insert(0, os.path.abspath('../../'))
    print sys.path

    runner = SSHgDOptions()
    try:
        runner.parseOptions() # When given no argument, parses sys.argv[1:]
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
