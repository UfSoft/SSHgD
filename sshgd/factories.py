# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.spread import pb
from sshgd import creds, realms, portals, checkers
from sshgd.utils.certs import OpenSSLCertificateOptions

class AdminServerPortalWrapper(pb._PortalWrapper):
    def remote_login(self, certificate, mind=None):
        credentials = creds.ClientCertificate(certificate)
        defer = self.portal.login(credentials, mind, pb.IPerspective)
        defer.addCallback(self._loggedIn)
        return defer

    def _loggedIn(self, (interface, perspective, logout)):
        if not pb.IJellyable.providedBy(perspective):
            perspective = pb.AsReferenceable(perspective, "perspective")
        self.broker.notifyOnDisconnect(logout)
        return perspective

class AdminServerPortalRoot(pb._PortalRoot):
    def rootObject(self, broker):
        return AdminServerPortalWrapper(self.portal, broker)

class AdminServerFactory(pb.PBServerFactory):
    """Configuration factory"""

    @classmethod
    def createFactory(Class):
        realm = realms.AdminConfigRealm()
        portal = portals.AdminPortal(realm)
        portal.registerChecker(checkers.ClientCertificateChecker())
        factory = Class(AdminServerPortalRoot(portal))
        realm.factory = portal.factory = factory
        return factory

    def getContext(self, opts):
        return OpenSSLCertificateOptions(opts.get('certificate'),
                                         opts.get('certificate'),
                                         verify=True,
                                         caCerts=opts.get('cacert'))
#
#    def remote_login(self, certificate):
#        print "def remote_login(self, certificate):"
#        print certificate

    def verifyCertificate(self, certificate):
        print "on verifyCertificate", certificate

class AdminClientFactory(pb.PBClientFactory):
    """Configuration client factory"""

    @classmethod
    def createFactory(Class):
        return Class(portals.AdminPortal(realms.AdminConfigRealm()))

    def getContext(self, opts):
        return OpenSSLCertificateOptions(opts.get('certificate'),
                                         opts.get('certificate'),
                                         verify=True,
                                         caCerts=opts.get('cacert'))

    def clientConnectionMade(self, broker):
#        print 333, dir(self)
#        print dir(self.protocol)
#        print self.protocol.transport
#        print 333, dir(broker)
        return pb.PBClientFactory.clientConnectionMade(self, broker)

    def sendCommand(self, cmd, *args, **kwargs):
        root = self.getRootObject()
        root.addCallback(self._sendCommand, cmd, *args, **kwargs)

    def _sendCommand(self, root, cmd, *args, **kwargs):
        return root.callRemote(cmd, *args, **kwargs)

    def login(self, credentials, client=None):
        d = self.getRootObject()
        d.addCallback(self._sendCertificate, credentials, client)
        return d

#    def login(self, credentials):
#        d = self.getRootObject()
#        d.addCallback(self._sendCertificate, credentials)
#        return d

    def _sendCertificate(self, root, creds, mind):
        return root.callRemote("login", creds, mind)
#        d = root.callRemote("loginAnonymous", None)
#        return d.addCallback(root.callRemote, "verifyCertificate", creds)
#        print "On login()"
##        from twisted.internet.ssl import Certificate
##        cert = Certificate.loadPEM(open(opts.get('certificate')).read())
#
#        return pb.PBClientFactory.clientConnectionMade(self, credentials, client)
