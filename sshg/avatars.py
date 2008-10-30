# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import binascii
import shutil
import tempfile

from twisted.conch.unix import UnixConchUser
from twisted.conch.ssh import session, filetransfer, keys
from twisted.conch.ssh.filetransfer import SFTPError
from twisted.internet import defer
from twisted.python import components, log
from twisted.spread.pb import Avatar

from sshg.db.model import User
from sshg.sessions import MercurialSession
from sshg.sftp import SFTPFileTransfer, FileTransferServer

class ConfigServerPerspective(Avatar):
    def __init__(self, cert_fingerprint):
        self.fingerprint = cert_fingerprint

    def logout(self):
        print "ConfigServerPrespective.logout() called", self.fingerprint
        print self.factory.protocol
        print self.factory.protocol.localObjects
        print dir(self.factory.protocol)

    def perspective_getRepos(self):
        print "perspective_getRepos()"
#        return {}
        return self.factory.storage.get('repos')

    def perspective_addRepos(self, name, path):
        existing_repos = self.factory.storage.get('repos')
        if name in existing_repos:
            return "Error: A repository by that name already exists"
        for values in existing_repos.itervalues():
            if values.get('path') == path:
                return "Error: A repository with that path is already being managed"
        self.factory.storage.add_repo(name, path)
        return "Repository Added"

class ConfigClientPerspective(Avatar):
    def __init__(self, username):
        self.username = username

    def logout(self):
        print "ConfigCl ientPrespective.logout() called"

    def perspective_getRepos(self):
        return self.factory.storage.get('repos')

class MercurialUser(UnixConchUser):
    homeDir = None

    def __init__(self, username):
        UnixConchUser.__init__(self, username)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})
        self.subsystemLookup.update({'sftp': FileTransferServer})

    def _runAsUser(self, f, *args, **kw):
        # Override UnixConchUser._runAsUser because we're not changing
        # uid's nor gid's.
        # Home directories are created and destroyed and populated at runtime
        # because they will only hold the public keys file
        try:
            f = iter(f)
        except TypeError:
            f = [(f, args, kw)]
        for i in f:
            func = i[0]
            args = len(i)>1 and i[1] or ()
            kw = len(i)>2 and i[2] or {}
            try:
                r = func(*args, **kw)
            except filetransfer.SFTPError:
                # Maybe uploading a file bigger than it should be?
                break
        return r

    def getHomeDir(self):
        if self.homeDir:
            return self.homeDir

        self.homeDir = tempfile.mkdtemp()
        log.msg('Creating home directory for user "%s": %s' % (self.username,
                                                               self.homeDir))
        store = self.factory.store
        self.user = store.findUnique(User,
                                     User.username==unicode(self.username))
        self.keys = [k.key.strip() for k in self.user.keys]

        # Populate keys file with current user's keys
        self.keys_file_path = os.path.abspath(os.path.join(self.homeDir,
                                                           "keys"))
        keys_file = open(self.keys_file_path, 'w')
        for key in self.keys:
            keys_file.write(key.strip() + '\n')
        keys_file.close()

        # Store modified time
        #self.keys_file_mtime = os.path.getmtime(self.keys_file_path)
        self.keys_file_mtime = os.path.getatime(self.keys_file_path)
        return self.homeDir

    def logout(self):
        return defer.maybeDeferred(self._logout)

    def _logout(self):
        log.msg('User "%s" logging out' % self.username)
        if self.homeDir:
            log.msg("Checking if user updated the public keys file")
            # Perhaps check each file in the user home dir???
            #if os.path.getmtime(self.keys_file_path) > self.keys_file_mtime:
            file_keys = []
            lineno = 1
            for line in open(self.keys_file_path):
                key = line.strip()
                if not self.validPublicKey(key):
                    log.msg("Ignoring line %i. Invalid key" % lineno )
                elif key == self.user.lastUsedKey.key:
                    log.msg("Key on line %i was used to login. "
                            "Skipping." % lineno)
                    if key in self.keys:
                        self.keys.pop(self.keys.index(key))
                else:
                    file_keys.append(key)
                lineno += 1
            new_keys = []
            deleted_keys = 0
            added_keys = 0
            for key in file_keys:
                if key in self.keys:
                    #log.msg("Key exists in database: %s" % key)
                    self.keys.pop(self.keys.index(key))
                elif key not in self.keys:
                    new_keys.append(key)
            for dbkey in self.user.keys:
                # Any existing keys in self.keys were deleted from file and
                # thus should be deleted from database
                if dbkey.key in self.keys:
                    #log.msg("Deleting Key: %r" % dbkey.key)
                    deleted_keys += 1
                    dbkey.deleteFromStore()
            for key in new_keys:
                # Add new keys to database
                #log.msg("Adding new key: %r" % key)
                added_keys += 1
                self.user.addPubKey(key)

            log.msg("User %s added %s and removed %s keys." % (
                    self.username, added_keys, deleted_keys))
            # Now remove any evidences from the file system
            log.msg("Removing temporary home dir of user %s" % self.username)
            shutil.rmtree(self.homeDir, True)
        log.msg('User "%s" logged out' % self.username)

    def validPublicKey(self, pubKeyString):
        try:
            key = keys.Key.fromString(data=pubKeyString)
        except (binascii.Error, keys.BadKeyError):
            return False
        return True



components.registerAdapter(MercurialSession, MercurialUser, session.ISession)
components.registerAdapter(SFTPFileTransfer, MercurialUser,
                           filetransfer.ISFTPServer)
