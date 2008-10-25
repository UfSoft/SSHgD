## -*- coding: utf-8 -*-
## vim: sw=4 ts=4 fenc=utf-8 et
## ==============================================================================
## Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
##
## Please view LICENSE for additional licensing information.
## ==============================================================================
#
#import sqlalchemy as sqla
#from sqlalchemy.orm import mapper, relation
#from sqlalchemy.ext.associationproxy import association_proxy
#
#from twisted.internet import defer
#
#from sasync.database import AccessBroker, transact
#
#class PubKey(object):
#    def __init__(self, key):
##        self.user = user
#        self.key = key
#
#class User(object):
##    repos = association_proxy('_repos', 'username')
#    def __init__(self, username):
#        self.username = username
#
#class Repository(object):
##    users = association_proxy('_users', 'username')
#    def __init__(self, name, path):
#        self.name = name
#        self.path = path
#
#class Repouser(object):
#    pass
#
##class PublicKey(AccessBroker):
##    def startup(self):
##        return self.table('keys',
##            sqla.Column('id', sqla.Integer, primary_key=True),
##            sqla.Column('key', sqla.Text, nullable=False)
##        )
##
##    @transact
##    def addKey(self, key):
##        return self.keys.insert().execute(key=key).fetchall()
##
##class User(AccessBroker):
##    def startup(self):
##        return self.table('users',
##            sqla.Column('id', sqla.Integer, primary_key=True),
##            sqla.Column('username', sqla.Text(50), nullable=False),
##            sqla.Column('keys', None, sqla.ForeignKey('keys.id'))
##        )
##
##    @transact
##    def add(self, username):
##        return self.users.insert().execute(username=username).fetchall()
#
#class DatabaseBroker(AccessBroker):
#    def startup(self):
#        users = self.table('users',
#            sqla.Column('username', sqla.Text(50), primary_key=True),
##            sqla.Column('keys_id', None, sqla.ForeignKey('keys.key'))
#        )
#        keys = self.table('keys',
#            sqla.Column('key', sqla.Text, primary_key=True),
#            sqla.Column('user_id', None, sqla.ForeignKey('users.username'))
#        )
#        repositories = self.table('repositories',
#            sqla.Column('name', sqla.Text(50), primary_key=True),
#            sqla.Column('path', sqla.Text, nullable=False)
#        )
#        repousers = self.table('repousers',
#            sqla.Column("repo_user", None, sqla.ForeignKey('users.username'),
#                        primary_key=True),
#            sqla.Column("repo_name", None, sqla.ForeignKey('repositories.name'),
#                        primary_key=True)
#        )
#
#        def gotTables(null):
#            print "mapping tables"
#            mapper(PubKey, self.keys)
#            mapper(User, self.users, properties=dict(
#                    keys = relation(PubKey, backref='user'),
#                    repos = relation(Repository, secondary=self.repousers)))
#            mapper(Repository, self.repositories, properties=dict(
#                    users = relation(User, secondary=self.repousers)
#            ))
#            mapper(Repouser, self.repousers)
#        deferred = defer.DeferredList([keys, users, repositories, repousers])
#        deferred.addCallback(gotTables)
#        return deferred
#
#
#    @transact
#    def addPubKey(self, username, key):
#        user = self.session.query(User).get(username)
#        if not user:
#            raise Exception, "User does not exist"
#        print 1, user.__dict__
#        key = self.session.query(PubKey).get(key)
#        if key:
#            user.keys.append(key)
#        else:
#            key = PubKey(key)
#            self.session.save(key)
#            user.keys.append(key)
#        return key #self.session.commit()
##        if key is None:
##            key = PubKey(user, key)
##        user.keys.append(key)
#
#    @transact
#    def getPubKeys(self, username):
##        session = self.getSession()
#        user = self.session.query(User).get(username)
#        return user.keys
#
#    @transact
#    def addUser(self, username):
#        user = self.session.query(User).get(username)
#        if user:
#            raise Exception, "User already exists"
#        user = User(username)
#        self.session.save(user)
#        return user #self.session.commit()
##        return user
#
#    @transact
#    def addRepository(self, name, path):
#        repo = self.session.query(Repository).get(name)
#        if repo:
#            raise Exception, "A repository by that name already exists"
#        repo = self.session.query(Repository).filter_by(path=path).first()
#        if repo:
#            raise Exception, "A repository with that path already exists"
#        repo = Repository(name, path)
#        self.session.save(repo)
#        return #self.session.commit()
##        return repo
#
#if __name__ == '__main__':
#    from twisted.internet import reactor
#
#    DbBroker = DatabaseBroker('sqlite:///database.db')
#
#    def prt(result):
#        print 2, result
#
#    def error(trace):
#        print trace.getTraceback()
#        DbBroker.shutdown()
#        try:
#            reactor.stop()
#        except:
#            pass
#
#
##    d = DbBroker.addUser("foo", session=True) #.addCallback(prt).addErrback(error)
##    print 3, d.__dict__
###    DbBroker.addPubKey("foo", "aaa", session=True).addCallback(prt).addErrback(error)
###    DbBroker.getPubKeys("foo", session=True).addCallback(prt).addErrback(error)
##    d.addCallback(lambda x: DbBroker.addPubKey("foo", "aaa", session=True))
##    d.addCallback(prt).addErrback(error)
##    d.addCallback(lambda x: DbBroker.getPubKeys("foo", session=True))
##    d.addCallback(prt).addErrback(error)
###    d.addCallback(prt).addErrback(error)
###    DbBroker.addPubKey("foo", "aaa")
###    print DbBroker.getPubKeys("foo", session=True)
#    u = DbBroker.addUser("foo", session=True).addCallback(prt).addErrback(error)
#    DbBroker.addPubKey("foo", "aaa", session=True).addCallback(prt).addErrback(error)
#
#    reactor.run()
