from __future__ import absolute_import

from func.minion.modules import func_module
import func.minion.modules.onode
from func.minion.modules.onode.common import delegate_methods


class Storage(func_module.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "opennode storage module"


from opennode.cli.actions import storage as mod
delegate_methods(Storage, mod)
