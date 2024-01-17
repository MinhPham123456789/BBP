import shlex
import os
import subprocess
import configparser
from recon_exceptions import *
from recon_utils import *

class Nmap:
    """
    This class initiates an object to carry out nmap commands inside python
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.target = target
        self.tool = "nmap"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.target)
        self.timeout = 100
        self.timestamp = timestamp
        self.debug = debug

    def nmap_remove_unnecessary_data(self, output):
        line_array = output.split("\n")
        output = "\n".join(line_array[1:-1]) # Remove 1st line has timestamp and last line has duration run
        return output

    def run_command(self):
        if check_command_existence(self.tool):
            cmd = prepare_command(self.command)
            sub_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate()
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd) + '"\n\n' + errs.decode('utf8'))

                # Response is bytes so decode the output and return
                clean_output = self.nmap_remove_unnecessary_data(output.decode('utf8').strip())
                self.output = f"Command: {self.command}\n{clean_output}"
                print(f"[Process]{self.tool} completed!")
                if self.debug:
                    print(self.output)
                return self.output
        else:
            raise NotInstalledError()
    
