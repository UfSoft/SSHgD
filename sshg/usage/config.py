# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os

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
        ["cacert", "c", ".ssh/cacert.pem", "Root CA certificate file path"],
        ["certificate", "f", ".ssh/server.pem", "private key file path"],
    ]

    subCommands = [
        ["pb", None, PBConfigServerOptions, "PB Based config service"],
        ["rpc", None, RPCConfigServerOptions, "XML-RPC based config service"]
    ]

    def postOptions(self):
        for key in ("cacert", "certificate"):
            self.opts[key] = os.path.abspath(
                os.path.expanduser(self.opts.get(key))
            )

    def getService(self):
        return self.subOptions.getService()

