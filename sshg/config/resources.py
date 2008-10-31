# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from axiom.errors import ItemNotFound
from sshg.db import model

class ConfigResource(object):
    def __init__(self, store):
        self.store = store

    def addUser(self, username):
        user = model.User.create(username, store=self.store)
        return user

    def getUser(self, username):
        try:
            return self.store.findUnique(model.User,
                                         model.User.username==username)
        except ItemNotFound:
            return None

    def delUser(self, username):
        try:
            user = self.store.findUnique(model.User,
                                         model.User.username==username)
            user.deleteFromStore()
        except ItemNotFound:
            return False
        return True

    def addPubKey(self, username, pubkey):
        if not isinstance(username, unicode):
            username = unicode(username)
        if not isinstance(pubkey, unicode):
            pubkey = unicode(pubkey)

        try:
            user = self.store.findUnique(model.User,
                                         model.User.username==username)
        except ItemNotFound:
            return "No such user"
        try:
            user.addPubKey(pubkey)
            return "OK"
        except Exception, err:
            raise err
            return "Something failed %s" % err

    def getPubKeys(self, username):
        username = unicode(username)
        try:
            user = self.store.findUnique(model.User,
                                         model.User.username==username)
        except ItemNotFound:
            return "No such user"
        return user.keys

    def addRepository(self, name, path):
        if not isinstance(name, unicode):
            name = unicode(name)
        if not isinstance(path, unicode):
            path = unicode(path)

        repo = model.Repository(store=self.store, name=name, path=path)
        return repo

    def addRepositoryUser(self, reponame, username):
        if not isinstance(reponame, unicode):
            reponame = unicode(reponame)
        if not isinstance(username, unicode):
            username = unicode(username)
        try:
            repo = self.store.findUnique(model.Repository,
                                         model.Repository.name==reponame)
            repo.addUser(username)
        except ItemNotFound:
            return None

    def getRepository(self, reponame):
        if not isinstance(reponame, unicode):
            reponame = unicode(reponame)
        try:
            return self.store.findUnique(model.Repository,
                                         model.Repository.name==reponame)
        except ItemNotFound:
            return None

    def getRepositoryUsers(self, reponame):
        if not isinstance(reponame, unicode):
            reponame = unicode(reponame)
        try:
            return self.store.findUnique(model.Repository,
                                         model.Repository.name==reponame).users
        except ItemNotFound:
            return []

if __name__ == '__main__':
    f = ConfigResource("abc")
    f.addUser('foo')
