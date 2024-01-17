import shlex
import subprocess
from recon_exceptions import *
from recon_utils import *

class Whois:
    """
    This class initiates an object to carry out whois commands inside python
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.target = target
        self.tool = "whois"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.target)
        self.timeout = 10
        self.output = ""
        self.timestamp = timestamp
        self.debug = debug
        
    def run_command(self):
        if check_command_existence(self.tool):
            cmd = prepare_command(self.command)
            sub_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate(timeout=self.timeout)
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd) + '"\n\n' + errs.decode('utf8'))

                # Response is bytes so decode the output and return
                self.output = f"Command: {self.command}\n{output.decode('utf8').strip()}" 
                # saving output to self.output does not work in multi process
                # because the self.output is allocated in different memory address so when reach the logging section the self.output is empty
                print(f"[Process]{self.tool} completed!")
                if self.debug:
                    print(self.output)
                return self.output
        else:
            raise NotInstalledError()

    # def get_output(self): # Does not work in multi process because the self.output is allocated in different memory address so
    # when reach the logging section the self.output is empty
    #     print(self.output)
    #     return self.output