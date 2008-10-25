# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from zope.interface import implements

from twisted.cred.portal import IRealm
from twisted.spread import pb
from sshg.avatars import ConfigServerPerspective


class AdminConfigRealm(object):
    implements(IRealm)
    def requestAvatar(self, avatarId, mind, *interfaces):
        if pb.IPerspective in interfaces:
            avatar = ConfigServerPerspective(avatarId)
            avatar.factory = self.factory
            return pb.IPerspective, avatar, avatar.logout
        else:
            raise NotImplementedError("no interface")
