# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from OpenSSL import crypto, SSL
from twisted.python import log

from twisted.internet._sslverify import SSL, _sessionCounter, md5, reflect
from twisted.internet._sslverify import OpenSSLCertificateOptions as OSSLCO


class OpenSSLCertificateOptions(OSSLCO):
#    def __init__(self,
#                 privateKey=None,
#                 certificate=None,
#                 method=None,
#                 verify=False,
#                 caCerts=None,
#                 verifyDepth=9,
#                 requireCertificate=True,
#                 verifyOnce=True,
#                 enableSingleUseKeys=True,
#                 enableSessions=True,
#                 fixBrokenPeers=False):
#        pass

    def _verify(self, connection, x509, errnum, errdepth, preverify_ok):
        if preverify_ok:
            log.msg("Verified Certificate with Common-Name: "
                    '"%s"; Issuer: "%s"' % (x509.get_subject().CN,
                                            x509.get_issuer().CN))
        else:
            log.msg("Did NOT Verified  Certificate with Common-Name: "
                    '"%s"; Issuer: "%s"; Errnum: %s; Errdepth: %d' % (
                    x509.get_subject().CN, x509.get_issuer().CN,
                    errnum, errdepth))
        return preverify_ok

    def _makeContext(self):
        ctx = SSL.Context(self.method)

        if self.certificate is not None and self.privateKey is not None:
            if isinstance(self.certificate, basestring):
                ctx.use_certificate(crypto.load_certificate(
                    crypto.FILETYPE_PEM, self.certificate))
            else:
                ctx.use_certificate(crypto.load_certificate(
                    crypto.FILETYPE_PEM, self.certificate.content))

            if isinstance(self.privateKey, basestring):
                ctx.use_privatekey(crypto.load_privatekey(
                    crypto.FILETYPE_PEM, self.privateKey))
            else:
                ctx.use_privatekey(crypto.load_privatekey(
                    crypto.FILETYPE_PEM, self.privateKey.privateKey))
            # Sanity check
            ctx.check_privatekey()

        verifyFlags = SSL.VERIFY_NONE
        if self.verify:
            verifyFlags = SSL.VERIFY_PEER
            if self.requireCertificate:
                verifyFlags |= SSL.VERIFY_FAIL_IF_NO_PEER_CERT
            if self.verifyOnce:
                verifyFlags |= SSL.VERIFY_CLIENT_ONCE
            if self.caCerts:
                store = ctx.get_cert_store()
                if isinstance(self.caCerts, basestring):
                    store.add_cert(crypto.load_certificate(
                        crypto.FILETYPE_PEM, self.caCerts))
                else:
                    for cert in self.caCerts:
                        content = None
                        if isinstance(cert, basestring):
                            content = cert
                        else:
                            content = cert.content
                        store.add_cert(crypto.load_certificate(
                            crypto.FILETYPE_PEM, content))


        ctx.set_verify(verifyFlags, self._verify)

        if self.verifyDepth is not None:
            ctx.set_verify_depth(self.verifyDepth)

        if self.enableSingleUseKeys:
            ctx.set_options(SSL.OP_SINGLE_DH_USE)

        if self.fixBrokenPeers:
            ctx.set_options(self._OP_ALL)

        if self.enableSessions:
            sessionName = md5.md5("%s-%d" % (reflect.qual(self.__class__),
                                             _sessionCounter())).hexdigest()
            ctx.set_session_id(sessionName)

        return ctx

