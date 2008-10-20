# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.spread.pb import Avatar
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh import session

class ConfigServerPerspective(Avatar):
    def __init__(self, cert_fingerprint):
        self.fingerprint = cert_fingerprint

    def logout(self):
        print "ConfigServerPrespective.logout() called", self.fingerprint
        print self.factory.protocol
        print self.factory.protocol.localObjects
        print dir(self.factory.protocol)

    def perspective_getRepos(self):
        print "perspective_getRepos()"
        return {}
#        return self.factory.storage.get('repos')


class ConfigClientPerspective(Avatar):
    def __init__(self, username):
        self.username = username

    def logout(self):
        print "ConfigClientPrespective.logout() called"

    def perspective_getRepos(self):
        return self.factory.storage.get('repos')


class MercurialUser(ConchUser):
    def __init__(self, username, factory):
        ConchUser.__init__(self)
        self.username = username
        self.factory = factory
        self.channelLookup.update({'session': session.SSHSession})
