# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import sys
import stat
import getpass
import itertools

from twisted.python import usage

from OpenSSL import crypto

try:
    from sshgd.usage.base import BaseOptions as RootBaseOptions
except ImportError:
    sys.path.insert(0, '.')
    from sshgd.usage.base import BaseOptions as RootBaseOptions

def ask_password(calledback=None):
    try:
        if calledback is not None:
            return getpass.getpass("Please enter the signing certificate "
                                   "password:")

        # It's not a password being requested, it's a password to define
        passwd = getpass.getpass("Define a password for the new private key "
                                 "(leave empty for none):")
        if not passwd:
            return None
        verify_password = getpass.getpass("Verify Password:")
        if passwd != verify_password:
            print "Passwords do not match. Exiting..."
            sys.exit(1)
        return passwd
    except KeyboardInterrupt:
        sys.exit(1)

class BaseOptions(RootBaseOptions):
    x509names = {
              "common-name": "commonName",
             "organization": "organizationName",
        "organization-unit": "organizationalUnitName",
                 "locality": "localityName",
        "state-or-province": "stateOrProvinceName",
                  "country": "countryName",
                    "email": "emailAddress"
    }

#    def opt_version(self):
#        """Show version"""
#        print os.path.basename(sys.argv[0]), '- 0.1'
#
#    opt_v = opt_version
#
#    def opt_help(self):
#        """Show this help message"""
#        usage.Options.opt_help(self)
#
#    opt_h = opt_help

#    def parseOptions(self, options=None):
#        if self.parent:
#            # Make sure the parent postOptions is ran before the
#            # subCommands are to expand paths, etc
#            self.parent.postOptions()
#        usage.Options.parseOptions(self, options)

class BaseCertOptions(BaseOptions):
    optParameters = [
        ["cert-name", None, "newcert.pem", "Certificate Name"],
        ["common-name", None, "NewCert", "The Certificate common name"],
        ["organization", None, None, "Organization Name"],
        ["organization-unit", None, None, "Organisation Unit Name"],
        ["locality", None, None, "Locality Name"],
        ["state-or-province", None, None, "State or Province Name"],
        ["country", None, None, "Two(2) Letter Country Name"],
        ["email", None, None, "Email Address"],
        ["years", None, 5, "Years to expire", int]
    ]

    def getNextSerial(self):
        serialfile = os.path.join(self.parent.get('output-dir'), 'serial')
        if not os.path.exists(serialfile):
            open(serialfile, 'w').write("0")
        counter = itertools.count(int(open(serialfile, 'r').read())).next
        serial = counter()
        open(serialfile, 'w').write(str(counter()))
        return serial

    def updateDestinguishedName(self, subject):
        DN = {}
        for key, val in self.opts.iteritems():
            if val and key in self.x509names:
                try:
                    setattr(subject, self.x509names.get(key), val.strip())
                except crypto.Error, err:
                    print "Setting value of '%s' failed" % key, err[0][0][2]
                    sys.exit(1)
                DN[self.x509names.get(key)] = val.strip()

        if not subject.commonName:
            print "Common Name for certificate not defined."
            print "You must pass at least a non empty --common-name"
            sys.exit(1)
        return subject

    def generatePrivateKey(self, output_path, write=True):
        privateKey = crypto.PKey()
        privateKey.generate_key(crypto.TYPE_RSA, 1024)
        if output_path:
            password = ask_password()
            encryption_args = []
            if password:
                encryption_args.extend(["DES-EDE3-CBC", password])
            privateKeyData = crypto.dump_privatekey(crypto.FILETYPE_PEM,
                                                    privateKey,
                                                    *encryption_args)
            open(output_path, 'w').write(privateKeyData)
        return privateKey

    def generateCertificateRequest(self, privateKey):
        certReq = crypto.X509Req()
        subject = self.updateDestinguishedName(certReq.get_subject())
        certReq.set_pubkey(privateKey)
        certReq.sign(privateKey, "md5")
        return certReq

    def generateCertificate(self, privateKey, output_path, write=True, mode='w',
                            issuer=None, issuerPrivateKey=None):
        assert mode in ["a", "w"], "'mode' must be one of 'w' or 'a'"

        cert = crypto.X509()
        cert.set_subject(self.updateDestinguishedName(cert.get_subject()))
        cert.set_pubkey(privateKey)
        cert.set_serial_number(self.getNextSerial())
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(self.opts.get('years'))
        if not issuer and not issuerPrivateKey:
            cert.set_issuer(self.updateDestinguishedName(cert.get_subject()))
            cert.add_extensions([
                crypto.X509Extension('basicConstraints', True, 'CA:TRUE')
            ])
            cert.sign(privateKey, "md5")
        elif issuer and issuerPrivateKey:
            cert.set_issuer(issuer)
            cert.sign(issuerPrivateKey, "md5")
        if write:
            certData = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
            open(output_path, mode).write(certData)
        return cert

class NewCA(BaseCertOptions):
    longdesc = """Create a new root certificate which will be used to issue both
    server and client certificates which are then use in authentication."""

    optParameters = [
        ["cert-name", None, "cacert.pem", "Certificate Name"],
        ["common-name", None, "CaCert", "The Root CA common name"],
    ]

    def postOptions(self):
        super(NewCA, self).postOptions()
        if self.opts.get('years') < 1:
            print "Certificate will need to be valid for at least one year"
            sys.exit(1)
        self.opts['years'] = 60 * 60 * 24 * 365 * self.opts.get('years')

        privateKey = self.generatePrivateKey(
            os.path.join(self.parent.get('output-dir'), 'private', 'cakey.pem')
        )
        self.generateCertificate(
            privateKey, os.path.join(self.parent.get('output-dir'),
                                     self.opts.get('cert-name'))
        )
        sys.exit(0)

class NewCert(BaseCertOptions):
    longdesc = "Create a new certificate which will be signed by the root CA."

    optParameters = [
        ["cert-name", None, "newcert.pem", "Certificate Name"],
        ["rootca-pk-file", None, "./.ssh/private/cakey.pem",
         "The Root CA private key file"],
        ["rootca-cert-file", None, "./.ssh/cacert.pem",
         "The Root CA certificate file"]
    ]

    def parseOptions(self, options):
        print 123
        super(NewCert, self).parseOptions(options)

    def postOptions(self):
        print 2
        super(NewCert, self).postOptions()
        if self.opts.get('years') < 1:
            print "Certificate will need to be valid for at least one year"
            sys.exit(1)
        self.opts['years'] = 60 * 60 * 24 * 365 * self.opts.get('years')

        rootCaCert = crypto.load_certificate(crypto.FILETYPE_PEM,
            open(os.path.abspath(
                os.path.expanduser(self.opts.get("rootca-cert-file"))
            )).read()
        )

        rootPrivateKey = crypto.load_privatekey(
            crypto.FILETYPE_PEM,
            open(os.path.abspath(
                os.path.expanduser(self.opts.get("rootca-pk-file")))).read(),
            ask_password
        )

        certFilename = os.path.join(self.parent.get('output-dir'),
                                    self.opts.get('cert-name'))
        print "Generating new private key"
        privateKey = self.generatePrivateKey(certFilename)
        self.generateCertificate(privateKey,
                                 certFilename,
                                 write=True,
                                 mode="a",
                                 issuer=rootCaCert.get_issuer(),
                                 issuerPrivateKey=rootPrivateKey)
        sys.exit(0)


class SignCert(BaseOptions):
    longdesc = """Sign an already created certificate pair with the root CA."""

    optParameters = [
        ["cert-name", None, "newcert.pem", "Certificate Name"],
        ["rootca-pk-file", None, "./.ssh/private/cakey.pem",
         "The Root CA private key file"],
        ["cacert", None, "./.ssh/cacert.pem",
         "The Root CA certificate file path"]
    ]

    def postOptions(self):
        print "This command does not currently do anything"
        sys.exit(0)


class CertsCreatorOptions(BaseOptions):
    runnedPostOption = False
    optParameters = [
        ["output-dir", "O", "./.ssh", "Output directory"]
    ]
    subCommands = [
        ["newca", None, NewCA, "Create new Root CA"],
        ["newcert", None, NewCert, "Create new certificate"],
        ["sign", None, SignCert, "Sign an already created certificate"]
    ]


    def postOptions(self):
        if self.runnedPostOption: return
        super(CertsCreatorOptions, self).postOptions()

        self.opts['output-dir'] = os.path.abspath(
            os.path.expanduser(self.opts.get('output-dir'))
        )

        basepath = self.opts.get("output-dir")

        if not os.path.exists(basepath):
            os.makedirs(os.path.join(basepath, 'private'),
                        stat.S_IREAD + stat.S_IWRITE + stat.S_IEXEC)

        self.runnedPostOption = True



if __name__ == '__main__':
    runner = CertsCreatorOptions()
    try:
        runner.parseOptions() # When given no argument, parses sys.argv[1:]
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
