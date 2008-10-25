# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

try:
    from sshg.usage.service import SSHgDOptions, ServiceMaker
except ImportError:
    # Package is not yet installed
    import os, sys
    sys.path.insert(0, os.path.abspath('.'))
    from sshg.usage.service import SSHgDOptions, ServiceMaker

# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.
serviceMaker = ServiceMaker()
