# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.web import xmlrpc

from sshg.config import resources

class BaseXMLRPCResource(xmlrpc.XMLRPC):
    def __init__(self, store, allowNone=False):
        xmlrpc.XMLRPC.__init__(self, allowNone=allowNone)
        self.resource = resources.ConfigResource(store)

class Users(BaseXMLRPCResource):

    def xmlrpc_add(self, username):
        added = self.resource.addUser(username)
        if added:
            return 'User "%s" added' % added.username
        return 'Failed to add user "%s"' % added.username

    #def xmlrpc_get(self, username):
    #    return self.resource.getUser(username)

    def xmlrpc_addPubKey(self, username, pubkey):
        pubKeyAdded = self.resource.addPubKey(username, pubkey)
        if pubKeyAdded:
            return 'Public key for user "%s" added' % username
        return 'Failed to add public key for user "%s"' % username

    def xmlrpc_getUserPubKeys(self, username):
        keys = [k.key for k in self.resource.getUserPubKeys(username)]
        if not keys:
            "No keys available"
        return keys

class Repositories(BaseXMLRPCResource):

    def xmlrpc_add(self, name, path):
        repo = self.resource.addRepository(name, path)
        if repo:
            return 'Repository with the name "%s" added' % name
        return 'Failed to add repository'


    def xmlrpc_addUser(self, reponame, username):
        repouser = self.resource.addRepositoryUser(reponame, username)
        if repouser:
            return 'User "%s" added to repository' % username
        return 'Failed to add user "%s" to repository' % username

    def xmlrpc_getUsers(self, reponame):
        users = [u.username for u in self.resource.getRepositoryUsers(reponame)
                 if u]
        if not users:
            return "No users available"
        return users


class RPCResource(xmlrpc.XMLRPC):
    def __init__(self, store, allowNone=False):
        xmlrpc.XMLRPC.__init__(self, allowNone=allowNone)
        users = Users(store, allowNone)
        repos = Repositories(store, allowNone)

        self.putSubHandler('users', users)
        self.putSubHandler('repos', repos)
