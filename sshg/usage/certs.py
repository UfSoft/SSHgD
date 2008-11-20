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
import random
import getpass
import itertools

from axiom.errors import DuplicateUniqueItem, ItemNotFound
from twisted.python import usage

from OpenSSL import crypto

try:
    from sshg.usage.base import BaseOptions as RootBaseOptions
except ImportError:
    sys.path.insert(0, '.')
    from sshg.usage.base import BaseOptions as RootBaseOptions

from sshg.db.model import Certificate

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

    def opt_version(self):
        """Show version"""
        print os.path.basename(sys.argv[0]), '- 0.1'
    opt_v = opt_version

    def opt_help(self):
        """Show this help message"""
        usage.Options.opt_help(self)
    opt_h = opt_help

    def postOptions(self):
        self.parent.postOptions()
        self.executeCommand()

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

    def generatePrivateKey(self):
        privateKey = crypto.PKey()
        privateKey.generate_key(crypto.TYPE_RSA, 1024)
        password = ask_password()
        encryption_args = password and ["DES-EDE3-CBC", password] or []
        privateKeyData = crypto.dump_privatekey(crypto.FILETYPE_PEM,
                                                privateKey,
                                                *encryption_args)
        return privateKey, privateKeyData.strip()

    def generateCertificateRequest(self, privateKey):
        certReq = crypto.X509Req()
        subject = self.updateDestinguishedName(certReq.get_subject())
        certReq.set_pubkey(privateKey)
        certReq.sign(privateKey, "md5")
        return certReq

    def generateCertificate(self, privateKey, serial,
                            issuer=None, issuerPrivateKey=None):

        cert = crypto.X509()
        cert.set_subject(self.updateDestinguishedName(cert.get_subject()))
        cert.set_pubkey(privateKey)
        cert.set_serial_number(serial)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(self.opts.get('years'))
        if not issuer and not issuerPrivateKey:
            # Generating a RootCA
            cert.set_issuer(self.updateDestinguishedName(cert.get_subject()))
            cert.add_extensions([
                crypto.X509Extension('basicConstraints', True, 'CA:TRUE')
            ])
            cert.sign(privateKey, "md5")
        elif issuer and issuerPrivateKey:
            cert.set_issuer(issuer)
            cert.sign(issuerPrivateKey, "md5")
        return crypto.dump_certificate(crypto.FILETYPE_PEM, cert).strip()

    def postOptions(self):
        self.parent.postOptions()
        years = self.opts['years']
        try:
            years = int(years)
        except ValueError:
            print "Please pass an integer"
            sys.exit(1)
        if years < 1:
            print "Certificate will need to be valid for at least one year"
            sys.exit(1)
        self.opts['years'] = 60 * 60 * 24 * 365 * years

        country = self.opts['country']
        if len(country) > 2:
            print "Please use the short name of your country, for USA it's US"
            sys.exit(1)
        self.opts['country'] = country
        self.executeCommand()


    def executeCommand(self):
        raise NotImplementedError


class NewCA(BaseCertOptions):
    longdesc = """Create a new root certificate which will be used to issue both
    server and client certificates which are then use in authentication."""

    optParameters = [
        ["start-serial", None, random.randint(1000, 10000),
         "Initial serial sequence number. If not provided a default random one "
         "will be generated.", int],
        ["cert-name", None, "cacert.pem", "Certificate Name"],
        ["common-name", None, "CaCert", "The Root CA common name"],
    ]

    def executeCommand(self):
        serial = Certificate.getSerial(self.parent.store) or \
                                                self.opts.get('start-serial')

        serial = serial == 0 and 1 or serial # Serial shouldn't be 0

        privateKey, privateKeyData = self.generatePrivateKey()
        content = self.generateCertificate(privateKey, serial)
        Certificate.create(privateKeyData, content, serial, rootCA=True,
                           store=self.parent.store)
        sys.exit(0)

class NewCert(BaseCertOptions):
    longdesc = "Create a new certificate which will be signed by the root CA."

    optParameters = [
        ["rootca", None, None, "The RootCA ID.", int],
    ]

    def executeCommand(self):
        rootCA = None
        store = self.parent.store
        if self.opts.get('rootca'):
            rootCA = self.parent.store.findUnique(
                            Certificate,
                            Certificate.storeID==self.opts.get('rootca'),
                            Certificate.rootCA==True
                     )
        else:
            try:
                rootCA = store.findUnique(Certificate, Certificate.rootCA==True)
            except DuplicateUniqueItem:
                print "There is more than one Root CA in the database."
                print "You need to specify the ID of the Root CA certificate", \
                      "to use"
                sys.exit(1)
            except ItemNotFound:
                print "There's no Root CA in the database yet. Please ", \
                      "generate one first"
                sys.exit(1)

        rootCaCert = crypto.load_certificate(crypto.FILETYPE_PEM,
                                             rootCA.content)

        try:
            rootPrivateKey = crypto.load_privatekey(
                crypto.FILETYPE_PEM, rootCA.privateKey, ask_password
            )
        except crypto.Error, error:
            print "Private key needs password and wrong password entered:",
            print error[0][0][2]
            sys.exit(1)
        print "Generating new private key"
        serial = Certificate.getSerial(self.parent.store)
        privateKey, privateKeyData = self.generatePrivateKey()
        content = self.generateCertificate(privateKey, serial,
                                           issuer=rootCaCert.get_issuer(),
                                           issuerPrivateKey=rootPrivateKey)
        Certificate.create(privateKeyData, content, serial,
                           rootCaID=rootCA.storeID, store=store)
        sys.exit(0)


#class SignCert(BaseOptions):
#    longdesc = """Sign an already created certificate pair with the root CA."""
#
#    optParameters = [
#        ["cert-name", None, "newcert.pem", "Certificate Name"],
#        ["rootca-pk-file", None, "./.ssh/private/cakey.pem",
#         "The Root CA private key file"],
#        ["cacert", None, "./.ssh/cacert.pem",
#         "The Root CA certificate file path"]
#    ]
#
#    def executeCommand(self):
#        print "This command does not currently do anything"
#        sys.exit(0)

class ExportCerts(BaseOptions):
    longdesc = """Export certificates in store"""

    optParameters = [
        ["output-dir", "O", './', "Output directory"],
        ["id", "i", None, "certificate id", int],
    ]
    optFlags = [
        ["include-private-key", "I", "Include Certificate's private key."]
    ]

    writeMode = 'w'

    def opt_output_dir(self, output_dir):
        output_dir = os.path.abspath(os.path.expanduser(output_dir))
        if not os.path.exists(output_dir):
            os.makedirs(os.path.join(output_dir, 'private'),
                        stat.S_IREAD + stat.S_IWRITE + stat.S_IEXEC)
        self.opts['output-dir'] = output_dir


    def executeCommand(self):
        id = self.opts.get('id')
        store = self.parent.store
        output_base_dir = self.opts.get('output-dir')
        try:
            certificate = store.findUnique(Certificate,
                                           Certificate.storeID==id)
        except ItemNotFound:
            print "No certificate by the id %s in store" % id
            sys.exit(1)

        outpath = os.path.join(output_base_dir, "%i.pem" % id)
        print 'Exporting certificate with id %i to "%s" ...' % (id, outpath),

        if self.opts.get('include-private-key'):
            print "including private-key ...",
            open(outpath, self.writeMode).write(certificate.privateKey + '\n')
            self.writeMode = 'a'

        open(outpath, self.writeMode).write(certificate.content + '\n')
        print "Done."
        sys.exit(0)


class ListCerts(BaseOptions):
    longdesc = """List certificates in store"""

    def executeCommand(self):
        store = self.parent.store
        query = store.query(Certificate)
        maxid = max([len(str(i.storeID)) for i in query])
        maxserial = max([len(i.rootCA and "*%s" % i.serial or
                             str(i.serial)) for i in query]
                        + [len('Serial')])
        maxCN = max([len(i.subject.CN) for i in query] + [len("Common Name")])
        maxIS = max([len(i.issuer.CN) for i in query] +
                    [len("Issuer (Root CA ID)")])
        format = ' %%s %%-%ds | %%-%ds | %%-%ds | %%-%ds' % (
            maxid, maxserial, maxCN, maxIS)
        header = format % ('', 'ID', 'Serial', 'Common Name',
                           "Issuer (Root CA ID/Serial)")
        print
        print header
        print '-'*len(header)
        for item in query:
            print format % (item.rootCA and "*"  or ' ',
                            item.storeID, item.serial, item.subject.CN,
                            item.issuer.CN + (
                                hasattr(item.rootCaCert, 'storeID') and
                                " (%s/%s)" % (
                                    item.rootCaCert.storeID,
                                    item.rootCaCert.serial) or ''))
        print '\n * - Root Certificate\n'
        sys.exit(0)


class CertsCreatorOptions(BaseOptions):
    hasRunPostOptions = False
    subCommands = [
        ["newca", None, NewCA, "Create new Root CA"],
        ["newcert", None, NewCert, "Create new certificate"],
        ["list", None, ListCerts, "List certificates in store"],
        ["export", None, ExportCerts, "Export certificates in store"],
#        ["sign", None, SignCert, "Sign an already created certificate"]
    ]

    @property
    def store(self):
        self.parent.postOptions()
        return self.parent.storage

    def postOptions(self):
        pass


if __name__ == '__main__':
    runner = CertsCreatorOptions()
    try:
        runner.parseOptions() # When given no argument, parses sys.argv[1:]
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
