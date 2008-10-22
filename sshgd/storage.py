# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import stat

from twisted.conch.ssh import keys
from twisted.persisted import dirdbm

from zope.interface import implements

from sshgd.interfaces import StorageInterface


class ShelfStorage(dirdbm.Shelf):
    implements(StorageInterface)

    defaults = {
        'repos': {
            'testproject': {
                'path': '/home/vampas/projects/L10nManager/testproject/',
                'users': ['vampas']
            }
        },
        'users': {
            'vampas': {
                'keys': [keys.Key.fromFile(
                            filename=os.path.expanduser('~/.ssh/id_rsa.pub'))]
            }
        }
    }

    def __init__(self, dbpath):
        dirdbm.Shelf.__init__(self, dbpath)
        if not os.listdir(self.dname):
            # Directory just created, fill-in some defaults
            self.update(self.defaults)
            # Directory should be readable by current user only
            os.chmod(self.dname, stat.S_IREAD + stat.S_IWRITE + stat.S_IEXEC)

    def add_user(self, username):
        """add user to storage"""
        if username not in self.get('users'):
            self.get('users')[username] = {}

    def add_user_key(self, username, key):
        """add a public key to specified username"""
        if username in self['users']:
            user = self.get('users').get(username)
            if not 'keys' in user:
                user['keys'] = []
            user['keys'].append(keys.Key.fromString(key))

    def get_user_keys(self, username):
        """get a list of the username's stored keys"""
        if username in self['users']:
            return self.get('users').get(username).get('keys')
        return []

    def add_repo(self, repo_name, repo_path):
        """add repo to storage"""
        current_repos = self.get('repos')
        current_repos.update({repo_name: {'path': repo_path,
                                          'users': []}})
        self['repos'] = current_repos

    def add_repo_user(self, repo_name, username):
        """add username to specified repo"""
        current_repos = self.get('repos')
        current_repos[repo_name]['users'].append(username)
        self['repos'] = current_repos

    def get_repos(self):
        """get all available repositories"""
        return self.get("repos")

    def get_repo_users(self, repo_name):
        """return a list of the specified repo users"""
        return self.get('repos')[repo_name]['users']
