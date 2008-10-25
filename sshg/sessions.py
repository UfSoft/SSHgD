# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.conch.ssh import session
from twisted.python import components

from zope.interface import implements

from sshg.avatars import MercurialUser

class MercurialSession(object):
    implements(session.ISession)

    hg_process_pid = None

    def __init__(self, avatar):
        self.avatar = avatar
        self.factory = avatar.factory

    def getPty(self, term, windowSize, attrs):
        pass

    def windowChanged(self, newWindowSize):
        pass

    def execCommand(self, protocol, cmd):
        import os
        from twisted.internet import reactor

        self.hg_process_pid = reactor.spawnProcess(
                        processProtocol = protocol,
                        executable      = 'hg',
                        args            = cmd.split() + ['--debug'],
                        env             = os.environ,
                        path            = '/home/vampas/projects/L10nManager/')

    def eofReceived(self):
        if self.hg_process_pid:
            self.hg_process_pid.loseConnection()
            self.hg_process_pid = None

    def closed(self):
        if self.hg_process_pid:
            self.hg_process_pid.loseConnection()
            self.hg_process_pid = None

    def openShell(self, transport):
        pass

components.registerAdapter(MercurialSession, MercurialUser, session.ISession)
