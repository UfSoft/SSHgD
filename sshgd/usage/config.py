# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os

from twisted.application import internet
from sshgd.usage.base import BaseOptions
from sshgd.factories import AdminServerFactory

class ConfigServerOptions(BaseOptions):
    longdesc = "fooo bar"
    optParameters = [
        ["port", "p", 4444, "configuration server port number", int],
        ["cacert", "c", ".ssh/cacert.pem", "Root CA certificate file path"],
        ["certificate", "f", ".ssh/server.pem", "private key file path"],
    ]

    def postOptions(self):
        for key, val in self.opts.iteritems():
            if isinstance(val, basestring):
                self.opts[key] = os.path.abspath(val)

    def getService(self):
        factory = AdminServerFactory.createFactory()
        factory.storage = self.parent.storage
        ctx = factory.getContext(self.opts)
        return internet.SSLServer(self.opts.get('port'), factory, ctx)

