# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.conch.ssh import factory, keys
from twisted.internet.ssl import PrivateCertificate
from twisted.web.server import Site
from twisted.spread import pb

from OpenSSL.crypto import FILETYPE_PEM

from sshg import creds, realms, portals, checkers
from sshg.utils.certs import OpenSSLCertificateOptions

class AdminServerPortalWrapper(pb._PortalWrapper):
    def remote_login(self, certificate, mind=None):
        credentials = creds.ClientCertificate(certificate)
        defer = self.portal.login(credentials, mind, pb.IPerspective)
        defer.addCallback(self._loggedIn)
        return defer

    def _loggedIn(self, (interface, perspective, logout)):
        if not pb.IJellyable.providedBy(perspective):
            perspective = pb.AsReferenceable(perspective, "perspective")
#        self.broker.notifyOnDisconnect(logout)
        return perspective

class AdminServerPortalRoot(pb._PortalRoot):
    def rootObject(self, broker):
        return AdminServerPortalWrapper(self.portal, broker)

class SSLContextFactory(object):
    def getContext(self, opts):
        return OpenSSLCertificateOptions(opts.get('certificate'),
                                         opts.get('certificate'),
                                         verify=True,
                                         caCerts=opts.get('cacert'))

class AdminServerFactory(pb.PBServerFactory, SSLContextFactory):
    """Configuration factory"""

    @classmethod
    def createFactory(Class, store):
        realm = realms.AdminConfigRealm()
        portal = portals.AdminPortal(realm)
        portal.registerChecker(checkers.ClientCertificateChecker())
        factory = Class(AdminServerPortalRoot(portal))
        factory.store = store
        realm.factory = portal.factory = factory
        return factory
#
#    def remote_login(self, certificate):
#        print "def remote_login(self, certificate):"
#        print certificate

    def verifyCertificate(self, certificate):
        print "on verifyCertificate", certificate

class AdminClientFactory(pb.PBClientFactory, SSLContextFactory):
    """Configuration client factory"""

    @classmethod
    def createFactory(Class):
        return Class(portals.AdminPortal(realms.AdminConfigRealm()))


    def clientConnectionMade(self, broker):
#        print 333, dir(self)
#        print dir(self.protocol)
#        print self.protocol.transport
#        print 333, dir(broker)
        return pb.PBClientFactory.clientConnectionMade(self, broker)


    def login(self, credentials, client=None):
        d = self.getRootObject()
        d.addCallback(self._sendCertificate, credentials, client)
        return d


    def _sendCertificate(self, root, creds, mind):
        return root.callRemote("login", creds, mind)

class WebServiceFactory(Site, SSLContextFactory):
    pass

class MercurialReposFactory(factory.SSHFactory):

    _publicKey = None
    _privateKey = None

    def __init__(self, realm, portal, store, privateCertificate):
        realm.factory = portal.factory = self
        self.realm = realm
        self.portal = portal
        self.store = store

        self._privateKey = keys.Key.fromString(
            PrivateCertificate.loadPEM(
                open(privateCertificate).read()
            ).privateKey.dump(FILETYPE_PEM)
        )
        self._publicKey = self._privateKey.public()

    def getPublicKeys(self):
        return {'ssh-rsa': self._publicKey}

    def getPrivateKeys(self):
        return {'ssh-rsa': self._privateKey}

