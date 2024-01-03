import os
import difflib

class VersionControl:
    def __init__(self, target_logs_dir, new_log_name, DEBUG=False):
        self.target_logs_dir = target_logs_dir
        self.version_logs_dir = f"{self.target_logs_dir}/version_comparison"
        self.check_version_logs_dir_existence()
        self.new_log_name = new_log_name
        self.previous_log_name = self.get_previous_log_name()
        self.debug = DEBUG

    def check_version_logs_dir_existence(self):
        if not os.path.exists(self.version_logs_dir):
            os.makedirs(self.version_logs_dir)

    def get_previous_log_name(self):
        files = [f"{self.target_logs_dir}/{file}" for file in os.listdir(self.target_logs_dir) if (file.lower().endswith('.xml'))]
        path = self.target_logs_dir
        if len(files) == 1:
            return ""
        files.sort(key=os.path.getmtime, reverse=True)
        return files[1]

    def compare_version(self):
        if self.debug:
            print(f"previous_log_name: {self.previous_log_name}")
        if len(self.previous_log_name) != 0:
            with open(f"{self.previous_log_name}", 'r') as pl:
                previous_log = pl.readlines()
                previous_log = previous_log[1:] # Remove 1st line with timestamp triggering wrong alert
            with open(f"{self.target_logs_dir}/{self.new_log_name}", 'r') as nl:
                new_log = nl.readlines()
                new_log = new_log[1:] # Remove 1st line with timestamp triggering wrong alert
            compare_result = []
            for line in difflib.unified_diff(previous_log, new_log, fromfile=self.previous_log_name, tofile=f"{self.target_logs_dir}/{self.new_log_name}", lineterm='', n=0):
                compare_result.append(line)
            compare_result = "\n".join(compare_result)
            if self.debug:
                print(compare_result)
            self.save_version_log(compare_result)
        
    def save_version_log(self, content):
        pl_name = self.previous_log_name.split("/")[-1]
        nl_name = self.new_log_name
        version_log_name = f"{pl_name}_VS_{nl_name}"
        with open(f"{self.version_logs_dir}/{version_log_name}", "w") as vl:
            vl.write(content)
        print(f"Version control log saved to {self.version_logs_dir}/{version_log_name}")
        


