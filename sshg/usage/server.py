# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import sys

from twisted.application import internet
from sshg.checkers import MercurialPublicKeysDB
from sshg.factories import MercurialReposFactory
from sshg.portals import MercurialRepositoriesPortal
from sshg.realms import MercurialRepositoriesRealm
from sshg.usage.base import BaseOptions

from sshg.db.model import errors, Certificate

class MercurialServerOptions(BaseOptions):
    longdesc = "Mercurial repositories SSH server"

    optParameters = [
        ["port", "p", 2222, "server port number", int],
        ["certid", "c", None, "Server certificate id", int],
    ]

    def getService(self):
        certid = self.opts.get('certid')
        try:
            certificate = self.parent.storage.findUnique(
                Certificate,
                Certificate.storeID==certid,
                Certificate.rootCA==False
            )
        except errors.ItemNotFound:
            print "Certificate with the ID %i was not found" % certid
            sys.exit(1)
        realm = MercurialRepositoriesRealm()
        portal = MercurialRepositoriesPortal(realm)
        portal.registerChecker(MercurialPublicKeysDB(self.parent.storage))
        factory = MercurialReposFactory(realm,
                                        portal,
                                        self.parent.storage,
                                        certificate.privateKey)
        return internet.TCPServer(self.opts.get('port'), factory)
