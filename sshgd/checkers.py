# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.error import UnauthorizedLogin, UnhandledCredentials
from twisted.internet import defer
from twisted.python import failure, log

from zope.interface import implements

from sshgd import creds

class ValidCertificate(Exception):
    pass

class RevokedCertificate(Exception):
    pass

class ClientCertificateChecker(object):
    credentialInterfaces = creds.ICertificateCredentials,
    implements(ICredentialsChecker)

    def requestAvatarId(self, certificate):
        print "requestAvatarId", certificate
        d = defer.maybeDeferred(self.checkCertificate, certificate)
        d.addCallback(self._cbRequestAvatarId, certificate)
        d.addErrback(self._ebRequestAvatarId)
        return d

    def checkCertificate(self, certificate):
        print "def checkCertificate(self, certificate):"
        return True
        # Return True or False
        pass

    def _cbRequestAvatarId(self, validCert, certificate):
        print "def _cbRequestAvatarId(self, validCert, certificate):", validCert, certificate
        if not validCert:
            return failure.Failure(UnauthorizedLogin())
        try:
            print 789, certificate.original.original.digest("md5")
            return certificate.original.original.digest("md5")
        except Exception, err:
            print "Exception", err
        # Check the certificate
        return failure.Failure(UnauthorizedLogin())

    def _ebRequestAvatarId(self, f):
        if not f.check(UnauthorizedLogin, ValidCertificate):
            log.msg(f)
            return failure.Failure(UnauthorizedLogin())
        return f
