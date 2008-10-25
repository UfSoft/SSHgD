# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.application import internet
from sshg.factories import WebServiceFactory
from sshg.usage.base import BaseOptions
from sshg.web.rpc import RPCResource

class RPCOptions(BaseOptions):
    optParameters = [
        ["port", "p", 6666, "server port number", int],
    ]

    def getService(self):
        rpc = RPCResource(self.parent.parent.storage)
        factory = WebServiceFactory(rpc)
        ctx = factory.getContext(self.parent.opts)
        return internet.SSLServer(self.opts.get('port'), factory, ctx)


class WebServiceOptions(BaseOptions):
    longdesc = """Web-based configuration services"""

    optParameters = [
        ["cacert", "c", ".ssh/cacert.pem", "Root CA certificate file path"],
        ["certificate", "f", ".ssh/server.pem", "private key file path"],
    ]

    subCommands = [
        ["rpc", None, RPCOptions, "Run the XML-RPC web service"]
    ]

    def getService(self):
        return self.subOptions.getService()
