# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.application import internet
from sshg.usage.base import BaseOptions
from sshg.factories import AdminServerFactory, WebServiceFactory
from sshg.config.rpc import RPCResource


class PBConfigServerOptions(BaseOptions):
    optParameters = [
        ["port", "p", 4444, "server port number", int],
    ]

    def getService(self):
        factory = AdminServerFactory.createFactory(self.parent.parent.storage)
        ctx = factory.getContext(self.parent.opts)
        return internet.SSLServer(self.opts.get('port'), factory, ctx)

class RPCConfigServerOptions(BaseOptions):
    optParameters = [
        ["port", "p", 6666, "server port number", int],
    ]

    def getService(self):
        rpc = RPCResource(self.parent.parent.storage)
        factory = WebServiceFactory(rpc)
        ctx = factory.getContext(self.parent.opts)
        return internet.SSLServer(self.opts.get('port'), factory, ctx)

class ConfigServerOptions(BaseOptions):
    longdesc = "Configuration Server(s)"
    optParameters = [
        ["certid", "c", None, "Certificate ID", int],
    ]

    subCommands = [
#        ["pb", None, PBConfigServerOptions, "PB Based config service"],
        ["rpc", None, RPCConfigServerOptions, "XML-RPC based config service"]
    ]

    defaultSubCommand = 'rpc'

    def postOptions(self):
        from axiom import errors
        from sshg.db.model import Certificate
        rootCAs = self.parent.store.query(Certificate, Certificate.rootCA==True)
        certId = self.opts.get('certid')
        try:
            cert = self.parent.store.findUnique(Certificate,
                                                Certificate.storeID==certId)
            self.opts['certificate'] = cert
            self.opts['caCerts'] = rootCAs
        except errors.ItemNotFound:
            import sys
            print "Certificate with the ID %i was not found" % certId
            sys.exit(1)

    def getService(self):
        return self.subOptions.getService()

