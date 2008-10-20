# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os

from twisted.cred.credentials import ICredentials
from twisted.internet.ssl import Certificate
from twisted.spread import pb
from zope.interface import implements

class ICertificateCredentials(ICredentials):
    def checkCertificate():
        """Pass the certificate to be checked and do the checking"""

class ClientCertificate(pb.Referenceable):
    implements(ICertificateCredentials)

    def __init__(self, certificate):
        if not isinstance(certificate, Certificate):
            if os.path.isfile(certificate):
                certificate = Certificate.loadPEM(open(certificate).read())
            else:
                certificate = Certificate.loadPEM(certificate)
        self.original = certificate
        self.certificate = certificate.dumpPEM()

    def checkCertificate(self):
        print "checkCertificate() called"
