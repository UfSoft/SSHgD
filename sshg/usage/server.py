# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.application import internet
from sshg.checkers import MercurialPublicKeysDB
from sshg.factories import MercurialReposFactory
from sshg.portals import MercurialRepositoriesPortal
from sshg.realms import MercurialRepositoriesRealm
from sshg.usage.base import BaseOptions

class MercurialServerOptions(BaseOptions):
    longdesc = "Mercurial repositories SSH server"

    optParameters = [
        ["port", "p", 2222, "server port number", int],
        ["certificate", "f", ".ssh/server.pem", "private key file path"],
    ]

    def getService(self):
        realm = MercurialRepositoriesRealm()
        portal = MercurialRepositoriesPortal(realm)
        portal.registerChecker(MercurialPublicKeysDB(self.parent.storage))
        factory = MercurialReposFactory(realm,
                                        portal,
                                        self.parent.storage,
                                        self.opts.get('certificate'))
        return internet.TCPServer(self.opts.get('port'), factory)
