# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import itertools


from OpenSSL import crypto, SSL

#from twisted.conch.ssh import keys
#from twisted.internet.ssl import DistinguishedName
#from twisted.internet._sslverify import (Certificate, CertificateRequest,
#                                         PrivateCertificate as TwPC, PublicKey,
#                                         KeyPair)
from twisted.internet._sslverify import SSL, _sessionCounter, md5, reflect
from twisted.internet._sslverify import OpenSSLCertificateOptions as OSSLCO


#class PrivateCertificate(TwPC):
#    callable = None
#
#    def _verify(self, connection, x509, errnum, errdepth, ok):
#        print '_verify (ok=%d):' % ok
#        print '  subject:', x509.get_subject()
#        print '  issuer:', x509.get_issuer()
#        print '  errnum %s, errdepth %d' % (errnum, errdepth)
#        return ok
#
#    def _makeContext(self):
#        ctx = SSL.Context(self.method)
#
#        if self.certificate is not None and self.privateKey is not None:
#            ctx.use_certificate(self.certificate)
#            ctx.use_privatekey(self.privateKey)
#            # Sanity check
#            ctx.check_privatekey()
#
#        verifyFlags = SSL.VERIFY_NONE
#        if self.verify:
#            verifyFlags = SSL.VERIFY_PEER
#            if self.requireCertificate:
#                verifyFlags |= SSL.VERIFY_FAIL_IF_NO_PEER_CERT
#            if self.verifyOnce:
#                verifyFlags |= SSL.VERIFY_CLIENT_ONCE
##            if self.caCerts:
##                store = ctx.get_cert_store()
##                for cert in self.caCerts:
##                    store.add_cert(cert)
#            ctx.load_verify_locations(self.caCerts)
#            ctx.set_verify(verifyFlags, self._verify)
#
#
#        if self.verifyDepth is not None:
#            ctx.set_verify_depth(self.verifyDepth)
#
#        if self.enableSingleUseKeys:
#            ctx.set_options(SSL.OP_SINGLE_DH_USE)
#
#        if self.fixBrokenPeers:
#            ctx.set_options(self._OP_ALL)
#
#        if self.enableSessions:
#            sessionName = md5.md5("%s-%d" % (reflect.qual(self.__class__),
#                                             _sessionCounter())).hexdigest()
#            ctx.set_session_id(sessionName)
#
#        return ctx

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
#        import sys
#        sys.stdout = sys.__stdout__
        print '_verify (ok=%d):' % preverify_ok
        print '  subject:', x509.get_subject()
        print '  issuer:', x509.get_issuer()
        print '  errnum %s, errdepth %d' % (errnum, errdepth)
        return preverify_ok

    def _makeContext(self):
        ctx = SSL.Context(self.method)

        if self.certificate is not None and self.privateKey is not None:
            ctx.use_certificate_file(self.certificate)
            ctx.use_privatekey_file(self.privateKey)
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
                ctx.load_verify_locations(self.caCerts)
#                store = ctx.get_cert_store()
#                for cert in self.caCerts:
#                    store.add_cert(cert)

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


#
#_sessionCounter = itertools.count().next
#
#class SSLContextFactory(object):
#
#    def __init__(self, cert_path, cacert_path):
#        self.cert_path = cert_path
#        self.cacert_path = cacert_path
#
#    def _verify(self, connection, x509, errnum, errdepth, ok):
#        print '_verify (ok=%d):' % ok
#        print '  subject:', x509.get_subject()
#        print '  issuer:', x509.get_issuer()
#        print '  errnum %s, errdepth %d' % (errnum, errdepth)
#        return ok
#
#    def getContext(self):
#        """Create an SSL context."""
#        ctx = SSL.Context(SSL.TLSv1_METHOD)
#        ctx.use_certificate_file(self.cert_path)
#        ctx.use_privatekey_file(self.cert_path)
#        print 'Context additions'
#        ctx.load_client_ca(self.cacert_path)
#        ctx.load_verify_locations(self.cacert_path)
#        ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
#                       self._verify)
#        print 'verify depth:', ctx.get_verify_depth()
#        ctx.set_verify_depth(1)
#        print 'verify depth:', ctx.get_verify_depth()
#        sessionName = md5.md5("%s-%d" % (reflect.qual(self.__class__),
#                                         _sessionCounter())).hexdigest()
#        ctx.set_session_id(md5.md5("%s-%d" % (reflect.qual(self.__class__),
#                                              _sessionCounter())).hexdigest())
#        return ctx


#def generate_key_pair():
#    return KeyPair.generate()
#
#def get_next_serial(serial_file):
#    if not os.path.exists(serial_file):
#        counter = itertools.count(0).next
#    else:
#        counter = itertools.count(int(open(serial_file, 'r').read())).next
#
#    serial = counter()
#    open(serial_file, 'w').write(str(counter()))
#    return serial
#
#def build_certs(basepath='./.ssh'):
#    opa = os.path.abspath
#    ope = os.path.expanduser
#    opj = os.path.join
#
#    basepath = opa(ope(basepath))
#    if not os.path.isdir(basepath):
#        os.mkdir(basepath)
#
#    serial_file = opj(basepath, 'serial')
#
##
##    # Generate Private/Public Keypair
##    pkey = generate_key_pair()
##
##    # Save Private Key
###    pkeytxt = pkey.dump(format=crypto.FILETYPE_PEM)
##    pkeytxt = pkey.dump()
##    open(opa(ope(opj(basepath, 'private.key'))), 'wb').write(pkeytxt)
##
###    cacert = pkey.newCertificate(pkeytxt, format=crypto.FILETYPE_PEM)
##    cacert = pkey.newCertificate(pkeytxt)
#
#    rootDn = DistinguishedName(commonName='SSHgD RootCA')
#    rootPk = KeyPair.generate()
#    rootCaReq = rootPk.certificateRequest(rootDn)
#    cert_opts = {'secondsToExpiry': 60 * 60 * 24 * 365 * 5 } # Five years
#    rootCaCertData = rootPk.signCertificateRequest(
#        rootDn, # issuerDistinguishedName
#        rootCaReq, # request data
#        lambda dn: True, # verifyDNCallback
#        get_next_serial(serial_file), # serial number
#        **cert_opts
#    )
#    rootCert = rootPk.newCertificate(rootCaCertData)
#    print 123, rootCert
#    open(opa(ope(opj(basepath, 'ca.cert'))), 'wb').write(rootCert.dump(crypto.FILETYPE_PEM))
#    open(opa(ope(opj(basepath, 'ca.pkey'))), 'wb').write(rootPk.dump(crypto.FILETYPE_PEM))
##    open(opa(ope(opj(basepath, 'ca.cert'))), 'wb').write(rootCert.dumpPEM())
#
#    serverDn = DistinguishedName(commonName='SSHgD Server')
#    serverPk = KeyPair.generate()
#
#
#
#    serverCaReq = serverPk.certificateRequest(serverDn)
#
#    serverCaCertData = rootPk.signCertificateRequest(
#        serverDn, # issuerDistinguishedName
#        serverCaReq, # request data
#        lambda dn: True, # verifyDNCallback
#        get_next_serial(serial_file), # serial number
#        **cert_opts
#    )
#
#    serverCert = serverPk.newCertificate(serverCaCertData)
#    open(opa(ope(opj(basepath, 'server.cert'))),
#         'wb').write(serverCert.dumpPEM())
#
#
#
#    open(opa(ope(opj(basepath, 'server.pkey'))),
#         'wb').write(serverPk.dump(crypto.FILETYPE_PEM))
##    open(opa(ope(opj(basepath, 'server_pub.pkey'))),
##         'wb').write(rootPk.get_publickey().dump(crypto.FILETYPE_PEM))
#
##    print serverPk.original.public()
##    print crypto.dump_privatekey(crypto.FILETYPE_PEM, serverCert.getPublicKey().original)
#
#    for client in range(3):
#        new_client_cert(basepath, serial_file, rootPk)
#
#    del opa, ope, opj
#
#def new_client_cert(basepath, serial_file, rootPk):
#    opa = os.path.abspath
#    ope = os.path.expanduser
#    opj = os.path.join
#
#    serial = get_next_serial(serial_file)
#    admins_public_keys_file = opa(ope(opj(basepath, 'admins_pub_keys.key')))
#    if not os.path.isfile(admins_public_keys_file):
#        admins_file_write_mode = 'w+b'
#    else:
#        admins_file_write_mode = 'a+b'
#
#
#    clientDn = DistinguishedName(commonName='SSHgD Client - %i' % (serial-1))
#    clientPk = KeyPair.generate()
#    clientCaReq = clientPk.certificateRequest(clientDn)
#
#    clientCaCertData = rootPk.signCertificateRequest(
#        clientDn, # issuerDistinguishedName
#        clientCaReq, # request data
#        lambda dn: True, # verifyDNCallback
#        serial, # serial number
#        secondsToExpiry = 60 * 60 * 24 * 365 * 5  # Five years
#    )
#
#    clientCert = clientPk.newCertificate(clientCaCertData)
#    open(opa(ope(opj(basepath, 'client-%i.cert' % (serial-1)))),
#         'w+b').write(clientCert.dumpPEM())
#
#    clientPubKey = keys.Key.fromString(data=clientPk.dump(crypto.FILETYPE_PEM))
#    admins_public_keys_file = open(admins_public_keys_file,
#                                   admins_file_write_mode)
#    admins_public_keys_file.write(clientPubKey.public().toString("openssh")+'\n')
#    del opa, ope, opj
#
#def load_pk_n_cert(path):
#    return PrivateCertificate.loadPEM(open(path).read())
#
#def load_privatekey(path):
#    pkNcert = load_pk_n_cert(path)
#    return keys.Key.fromString(pkNcert.privateKey.dump(crypto.FILETYPE_PEM))
#
#if __name__ == '__main__':
#    build_certs()

