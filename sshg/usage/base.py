# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import sys
import getopt
from ConfigParser import SafeConfigParser
from twisted.python import usage

class BaseOptions(usage.Options):
    def opt_version(self):
        """Show version"""
        print os.path.basename(sys.argv[0]), '- 0.1'
    opt_v = opt_version

    def opt_help(self):
        """Show this help message"""
        super(BaseOptions, self).opt_help()
    opt_h = opt_help

    def getService(self):
        print "No subcommand issued"
        self.opt_help()
