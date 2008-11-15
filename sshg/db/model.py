# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import inspect

from axiom import errors, item
from axiom.attributes import (boolean, integer, reference, text, timestamp,
                              inmemory, SQLAttribute, AND)
from epsilon.extime import Time
from OpenSSL import crypto

class NotUnique(ValueError):
    """Item is not unique on database"""

class NotInstanceOf(Exception):
    """The attribute passed is not instantiated"""

class ToDictMixIn(object):
    def toDict(self):
        attrs_dict = {}
        for attr in inspect.getmembers(self):
            attribute = getattr(self, attr)
            if isinstance(attribute, SQLAttribute):
                attrs_dict[attr] =  attribute
        return attrs_dict

class Certificate(item.Item):
    typeName = 'cert'
    schemaVersion = 1
    privateKey = text(indexed=True, caseSensitive=True, allowNone=False)
    privateKey.unique = True
    content = text(caseSensitive=True, allowNone=False)
    content.unique = True
    serial = integer(indexed=True, allowNone=False)
    revoked = boolean(default=False, allowNone=False)
    rootCA = boolean(default=False, allowNone=False)

    # Private Attributes
    _cert = inmemory()

    @property
    def cert(self):
        try:
            return self._cert
        except AttributeError:
            # _cert hasn't been loaded yet
            self._cert = crypto.load_certificate(crypto.FILETYPE_PEM,
                                                 self.content)
            return self._cert

    @property
    def subject(self):
        return self.cert.get_subject()

    @property
    def issuer(self):
        return self.cert.get_issuer()


    @classmethod
    def getSerial(self, store):
        try:
            return store.query(Certificate).getColumn("serial").max() + 1
        except ValueError:
            return None

    @classmethod
    def create(Class, privateKey, content, serial, **kw):
        if not isinstance(privateKey, unicode):
            privateKey = unicode(privateKey)
        if not isinstance(content, unicode):
            content = unicode(content)
        if 'DN' in kw:
            kw['DN'] = unicode(kw['DN'])
        if 'store' not in kw:
            raise Exception("You must pass a store")
        store = kw.get('store')
        query_args = [getattr(Class, 'privateKey')==privateKey,
                      getattr(Class, 'content')==content,
                      getattr(Class, 'serial')==serial]
        for key, val in kw.iteritems():
            if hasattr(Class, key):
                attr = getattr(Class, key)
                if isinstance(attr, SQLAttribute):
                    if hasattr(attr, 'unique') and getattr(attr, 'unique'):
                        query_args.append(attr==val)
        try:
            if store.findUnique(Class, AND(*query_args)):
                raise NotUnique("An equal certificate already exsits")
        except errors.ItemNotFound:
            return Class(privateKey=privateKey, content=content,
                         serial=serial, **kw)


class User(item.Item, ToDictMixIn):
    typeName = 'user'
    schemaVersion = 1

    username = text(indexed=True, caseSensitive=True, allowNone=False)
    username.unique = True
    added = timestamp(allowNone=False, defaultFactory=Time)
    last_login = timestamp(allowNone=False, defaultFactory=Time)
    lastUsedKey = reference(doc="Key used on last login")

    @classmethod
    def create(Class, username, **kw):
        if not isinstance(username, unicode):
            username = unicode(username)
        if 'store' not in kw:
            raise Exception("You must pass a store")
        store = kw.get('store')
        query_args = [getattr(Class, 'username')==username]
        for key, val in kw.iteritems():
            if hasattr(Class, key):
                attr = getattr(Class, key)
                if isinstance(attr, SQLAttribute):
                    if hasattr(attr, 'unique') and getattr(attr, 'unique'):
                        query_args.append(attr==val)
        try:
            if store.findUnique(Class, AND(*query_args)):
                raise NotUnique("A user with that username already exists")
        except errors.ItemNotFound:
            return Class(username=username, **kw)

    @property
    def keys(self):
        for key in self.store.query(PubKey, PubKey.user==self):
            yield key

    @property
    def repos(self):
        for relation in self.store.query(UserRepoManyToMany,
                                         UserRepoManyToMany.user==self):
            yield relation.repo

    def addRepo(self, repo):
        if not isinstance(repo, Repository):
            raise NotInstanceOf
        relation = UserRepoManyToMany(repo=repo, user=self, store=self.store)

    def getRepo(self, reponame):
        if not isinstance(reponame, unicode):
            reponame = unicode(reponame)
        for repo in self.repos:
            if repo.name == reponame:
                return repo
        return None

    def addPubKey(self, key):
        if not isinstance(key, unicode):
            key = unicode(key)
        return PubKey.create(self, key, store=self.store)


class PubKey(item.Item, ToDictMixIn):
    typeName = 'pubkey'
    schemaVersion = 1

    key = text(indexed=True, allowNone=False, caseSensitive=True)
    key.unique = True
    added = timestamp(allowNone=False, defaultFactory=Time)
    used = timestamp(allowNone=False, defaultFactory=Time)
    user = reference(allowNone=False)


    @classmethod
    def create(Class, user, pubkey, **kw):
        if not isinstance(user, User):
            raise Exception("user must be a class instance of User")
        if not isinstance(pubkey, unicode):
            pubkey = unicode(pubkey)
        if 'store' not in kw:
            raise Exception("You must pass a store")
        store = kw.get('store')

        query_args = [getattr(Class, 'key')==pubkey]
        for key, val in kw.iteritems():
            if hasattr(Class, key):
                attr = getattr(Class, key)
                if isinstance(attr, SQLAttribute):
                    if hasattr(attr, 'unique') and getattr(attr, 'unique'):
                        query_args.append(attr==val)
        try:
            if store.findUnique(Class, AND(*query_args)):
                raise NotUnique("A pubkey with this value already exists")
        except errors.ItemNotFound:
            return Class(key=pubkey, user=user, **kw)

    def updateUsed(self):
        self.user.last_login = self.used = Time()


class UserRepoManyToMany(item.Item, ToDictMixIn):
    typeName = 'user_repo_relationship'
    scemaVersion = 1

    user = reference(allowNone=False)
    repo = reference(allowNone=False)
    admin = boolean(default=False, allowNone=False)

class Repository(item.Item):
    typeName = 'repo'
    schemaVersion = 1

    name = text(indexed=True, allowNone=False, caseSensitive=True)
    name.unique = True
    path = text(indexed=True, allowNone=False, caseSensitive=True)
    path.unique = True
    added = timestamp(allowNone=False, defaultFactory=Time)


    @classmethod
    def create(Class, name, path, **kw):
        if not isinstance(name, unicode):
            name = unicode(name)
        if not isinstance(path, unicode):
            path = unicode(path)
        if 'store' not in kw:
            raise Exception("You must pass a store")
        store = kw.get('store')

        query_args = [getattr(Class, 'name')==name,
                      getattr(Class, 'path')==path]
        for key, val in kw.iteritems():
            if hasattr(Class, key):
                attr = getattr(Class, key)
                if isinstance(attr, SQLAttribute):
                    if hasattr(attr, 'unique') and getattr(attr, 'unique'):
                        query_args.append(attr==val)
        try:
            if store.findUnique(Class, AND(*query_args)):
                raise NotUnique("A repository with these values already exists")
        except errors.ItemNotFound:
            return Class(name=name, path=path, **kw)

    @property
    def users(self):
        for match in self.store.query(UserRepoManyToMany,
                                      UserRepoManyToMany.repo==self):
            yield match.user

    def addUser(self, user):
        if not isinstance(user, User):
            try:
                user = self.store.findUnique(User, User.username==user)
            except errors.ItemNotFound:
                return None
        relation = UserRepoManyToMany(user=user, repo=self, store=self.store)
        return user

    def isManager(self, username):
        pass

#class RepositoryManagers(item.Item, ToDictMixIn):
#    typeName = 'user_repo_relationship'
#    scemaVersion = 1
#
#    user = reference(allowNone=False)
#    repo = reference(allowNone=False)


if __name__ == '__main__':
    from axiom.store import Store
    s = Store('test.db')
    user1 = User.create(username='Foo', store=s)
    try:
        user1 = User.create(username='Foo', store=s)
    except NotUnique:
        print "not unique"
    user2 = User.create(username='Foo1', store=s)

    user1.addPubKey("abc")

    print 'keys', list(user1.keys)

    repo = Repository.create('testproject',
                             '/home/vampas/projects/L10nManager/testproject/',
                             store=s)
    repo.addUser(user1)
    repo.addUser(user2)

    print "repo users"
    for user in repo.users:
        print "User:", user, "Keys:", list(user.keys)
