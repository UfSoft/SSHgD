# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
from twisted.conch.ssh import session
from twisted.internet import reactor
from twisted.python import log

from zope.interface import implements

class MercurialSession(object):
    implements(session.ISession)

    hg_process_pid = None

    def __init__(self, avatar):
        log.msg("Initiated Mercurial Session: %s" % avatar.username)
        self.avatar = avatar
        self.factory = avatar.factory

    def getPty(self, term, windowSize, attrs):
        print "getPTY"
        pass

    def windowChanged(self, newWindowSize):
        print "windowChanged"
        pass

    def execCommand(self, protocol, cmd):
        print "execCommand"
#        self.hg_process_pid = reactor.spawnProcess(
#                        processProtocol = protocol,
#                        executable      = 'hg',
#                        args            = cmd.split() + ['--debug'],
#                        env             = os.environ,
#                        path            = '/home/vampas/projects/L10nManager/')

    def eofReceived(self):
        if self.hg_process_pid:
            self.hg_process_pid.loseConnection()
            self.hg_process_pid = None

    def closed(self):
        if self.hg_process_pid:
            self.hg_process_pid.loseConnection()
            self.hg_process_pid = None

    def openShell(self, transport):
        # log.msg("openShell")
        # No shells available here!
        transport.session.conn.transport.transport.loseConnection()

    def getPtyOwnership(self):
        print "getPtyOwnership"

    def setModes(self):
        print "setModes"

