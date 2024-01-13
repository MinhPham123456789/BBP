import shlex
import os
from recon_exceptions import *
from recon_utils import *

class GobusterSubdomain:
    """
    This class initiates an object to carry out snrublist3r tool to brute force subdomains inside python
    """
    def __init__(self, target, command_config_path, debug=False):
        self.target = target
        self.tool = "gobuster_subdomain"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.target)
        self.timeout = 10
        self.output = ""
        self.debug = debug

    