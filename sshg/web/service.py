# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.python import usage

class XMLRPCService(usage.Options):
    optParameters = [
        ["port", "p", 6666, "server port number", int],
        ["cacert", "c", ".ssh/cacert.pem", "Root CA certificate file path"],
        ["certificate", "f", ".ssh/server.pem", "private key file path"],
    ]
    
    