# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from zope.interface import Interface

class StorageInterface(Interface):

    def save(self):
        """save current status of storage"""

    def add_user(self, username):
        """add user to storage"""

    def add_user_key(self, username, key):
        """add a public key to specified username"""

    def get_user_keys(self, username):
        """get a list of the username's stored keys"""

    def add_repo(self, repo_name, repo_path):
        """add repo to storage"""

    def add_repo_user(self, repo_name, username):
        """add username to specified repo"""

    def get_repo_users(self, repo_name):
        """return a list of the specified repo users"""
