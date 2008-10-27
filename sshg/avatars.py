# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import shutil

from twisted.spread.pb import Avatar
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh import session, filetransfer
from twisted.python import components, log
from twisted.internet import defer

from sshg.db.model import User
from sshg.sftp import SftpFileTransfer, FileTransferServer

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
                return "Error: A repository with that path is already beeing managed"
        self.factory.storage.add_repo(name, path)
        return "Repository Added"



class ConfigClientPerspective(Avatar):
    def __init__(self, username):
        self.username = username

    def logout(self):
        print "ConfigCl ientPrespective.logout() called"

    def perspective_getRepos(self):
        return self.factory.storage.get('repos')

from twisted.conch.unix import UnixConchUser
class MercurialUser(UnixConchUser):
    homeDir = None

    def __init__(self, username):
        UnixConchUser.__init__(self, username)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})
        self.subsystemLookup.update({'sftp': FileTransferServer})

    def _runAsUser(self, f, *args, **kw):
        try:
            f = iter(f)
        except TypeError:
            f = [(f, args, kw)]
        for i in f:
            func = i[0]
            args = len(i)>1 and i[1] or ()
            kw = len(i)>2 and i[2] or {}
            r = func(*args, **kw)
        return r

    def getHomeDir(self):
        import tempfile
        if not self.homeDir:
            self.homeDir = tempfile.mkdtemp()
            print "Home dir created:", self.homeDir
            store = self.factory.store
            self.user = store.findUnique(User,
                                         User.username==unicode(self.username))
            print "User:", self.user
            self.keys = [k.key for k in self.user.keys]
            self.keys_file_path = os.path.abspath(os.path.join(self.homeDir,
                                                               "keys"))
#            open(self.keys_file_path).write('')
#            os.utime(self.keys_file_path)
            keys_file = open(self.keys_file_path, 'w')
            keys = []
            n = 1
            total = 0
            for key in self.keys:
                keys.append(key.rstrip('\n'))
            while n <= 51200:
                keys_file = open(self.keys_file_path, 'a')
                keys_file.write(keys[0] + '\n')
                keys_file.close()
                n = os.path.getsize(self.keys_file_path)
                total += 1
#            keys_file.close()
            self.keys_file_mtime = os.path.getmtime(self.keys_file_path)
            print "File Size:", os.path.getsize(self.keys_file_path)
            print "Total Keys:", total
        return self.homeDir

    def logout(self):
        defer.maybeDeferred(self._logout)

    def _logout(self):
        log.msg('User "%s" logging out' % self.username)
        if self.homeDir:
            log.msg("Checking if user updated the public keys file")
            print os.stat(self.keys_file_path)
            print self.keys_file_mtime
            print os.path.getmtime(self.keys_file_path)
            if os.path.getmtime(self.keys_file_path) > self.keys_file_mtime:
                for line in open(self.keys_file_path):
                    print repr(line)
                    print repr(line.rstrip())
            print "Removing Home dir:", self.homeDir
            print os.listdir(self.homeDir)
            shutil.rmtree(self.homeDir, True)
        log.msg('User "%s" logged out' % self.username)



from sshg.sessions import MercurialSession
components.registerAdapter(MercurialSession, MercurialUser, session.ISession)
components.registerAdapter(SftpFileTransfer, MercurialUser,
                           filetransfer.ISFTPServer)

#from twisted.conch.unix import SSHSessionForUnixConchUser
#components.registerAdapter(SSHSessionForUnixConchUser, MercurialUser, session.ISession)
