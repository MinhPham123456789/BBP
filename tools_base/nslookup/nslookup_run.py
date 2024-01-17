import shlex
import subprocess
from recon_exceptions import *
from recon_utils import *
import re
import ipaddress

class Nslookup:
    """
    This class initiates an object to carry out nslookup commands inside python
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.target = target
        self.tool = "nslookup"
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
                self.output = f"Command: {self.command}\n{output.decode('utf8').strip()}" # self.output does not work in multi process
                #   because the self.output is allocated in different memory address so when reach the logging section the self.output is empty
                # Run whois IP Address
                whois_ip_output = self.get_whois_ip(self.output)
                self.output = f"{self.output}\n{whois_ip_output}"
                print(f"[Process]{self.tool} completed!")
                if self.debug:
                    print(self.output)
                return self.output
        else:
            raise NotInstalledError()

    def get_whois_ip(self, output):
        result = ""
        domain_ip_addresses_v4 = re.findall(r"Address: ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", output)
        if self.debug:
                print(f"nslookup: {output}")
                print(f"domain's ip addresses:{domain_ip_addresses_v4}")
        # Iterate the ip address v4 through reverse whois
        for ip in domain_ip_addresses_v4:
            cmd = f"whois {ip}"
            cmd = prepare_command(cmd)
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
                whois_ip_output = f"Command: {self.command}\n{output.decode('utf8').strip()}"
            result = f"{result}\n#################################\nip_address_v4: {ip}\nwhois_{ip}:\n{whois_ip_output}\n"
        return result
