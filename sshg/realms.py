# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from zope.interface import implements

from twisted.conch.interfaces import IConchUser
from twisted.cred.portal import IRealm
from twisted.spread import pb
from sshg.avatars import ConfigServerPerspective, MercurialUser


class AdminConfigRealm(object):
    implements(IRealm)
    def requestAvatar(self, avatarId, mind, *interfaces):
        if pb.IPerspective in interfaces:
            avatar = ConfigServerPerspective(avatarId)
            avatar.factory = self.factory
            return pb.IPerspective, avatar, avatar.logout
        raise Exception, "No supported interfaces found."


class MercurialRepositoriesRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            avatar = MercurialUser(avatarId)
            avatar.factory = self.factory
            return interfaces[0], avatar, avatar.logout
        raise Exception, "No supported interfaces found."
