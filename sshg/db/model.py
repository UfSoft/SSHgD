# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from axiom import errors, item, attributes
from epsilon.extime import Time

class NotUnique(ValueError):
    """Item is not unique on database"""

class NotInstanceOf(Exception):
    """The attribute passed is not instantiated"""

class User(item.Item):
    typeName = 'user'
    schemaVersion = 1

    username = attributes.text(indexed=True, caseSensitive=True,
                               allowNone=False)
    username.unique = True
    added = attributes.timestamp(allowNone=False, defaultFactory=Time)

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
                if isinstance(attr, attributes.SQLAttribute):
                    if hasattr(attr, 'unique') and getattr(attr, 'unique'):
                        query_args.append(attr==val)
        if query_args:
            for item in store.query(Class, attributes.AND(*query_args)):
                raise NotUnique("A user with that username already exists")
        return Class(username=username, **kw)


    @property
    def keys(self):
        keys = []
        for key in self.store.query(PubKey, PubKey.user==self):
            yield key

    @property
    def repos(self):
        return self.store.query(UserRepoManyToMany,
                                UserRepoManyToMany.user==self)

    def addRepo(self, repo):
        if not isinstance(repo, Repository):
            raise NotInstanceOf
        relation = UserRepoManyToMany(repo=repo, user=self, store=self.store)

    def addPubKey(self, key):
        pubkey = PubKey.create(self, key, store=self.store)
        print "pubkey", pubkey
        return pubkey

class PubKey(item.Item):
    typeName = 'pubkey'
    schemaVersion = 1

    key = attributes.text(indexed=True, allowNone=False, caseSensitive=True)
    key.unique = True
    added = attributes.timestamp(allowNone=False, defaultFactory=Time)
    user = attributes.reference(allowNone=False)


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
                if isinstance(attr, attributes.SQLAttribute):
                    if hasattr(attr, 'unique') and getattr(attr, 'unique'):
                        query_args.append(attr==val)
        if query_args:
            for item in store.query(Class, attributes.AND(*query_args)):
                raise NotUnique("A pubkey with this value already exists")
        print 1
        pubkey = Class(key=pubkey, user=user, **kw)
        print 2
#        pubkey.user = user
        print 3
        return pubkey


class UserRepoManyToMany(item.Item):
    typeName = 'user_repo_relationship'
    scemaVersion = 1

    user = attributes.reference(allowNone=False)
    repo = attributes.reference(allowNone=False)

class Repository(item.Item):
    typeName = 'repo'
    schemaVersion = 1

    name = attributes.text(indexed=True, allowNone=False, caseSensitive=True)
    name.unique = True
    path = attributes.text(indexed=True, allowNone=False, caseSensitive=True)
    path.unique = True
    added = attributes.timestamp(allowNone=False, defaultFactory=Time)


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
                if isinstance(attr, attributes.SQLAttribute):
                    if hasattr(attr, 'unique') and getattr(attr, 'unique'):
                        query_args.append(attr==val)
        for item in store.query(Class, attributes.AND(*query_args)):
            raise NotUnique("A repository with these values already exists")
        return Class(name=name, path=path, **kw)

    @property
    def users(self):
        for match in self.store.query(UserRepoManyToMany,
                                      UserRepoManyToMany.repo==self):
            yield match.user

    def addUser(self, user):
        if not isinstance(user, User):
            user = User(username=user, store=self.store)
        relation = UserRepoManyToMany(user=user, repo=self, store=self.store)


#class RootCertificate(item.Item):
#    typeName = 'rootca'
#    schemaVersion = 1
#
#    privKey = attributes.text(indexed=True, allowNone=False, caseSensitive=True)
#    cretificate = attributes.text(indexed=True, allowNone=False,
#                                  caseSensitive=True)

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
