from xml.etree import ElementTree as ET
import configparser
import os
import re
from recon_utils import *

class Logging:
    """This class create an object to record the output by the tools in an XML text"""
    def __init__(self, target_name, config_path, timestamp, log_type="main"):
        self.target_name = target_name
        self.config_path = config_path
        self.base_dir = get_env_values(self.config_path, 'log', 'base_path')
        self.log_type = log_type

        if self.log_type == "main":
            self.target_dir = f"{self.base_dir}/{target_name}"
            self.root = ET.Element("ReconLog")
        elif self.log_type == "subdomain":
            subdomain_tools_log_path = get_env_values(self.config_path, 'log', 'subdomain_tools_log_path')
            self.target_dir = f"{self.base_dir}/{target_name}/{subdomain_tools_log_path}"
            self.root = ET.Element("SubdomainToolsLog")
        elif self.log_type == "params":
            params_tools_log_path = get_env_values(self.config_path, 'log', 'params_tools_log_path')
            self.target_dir = f"{self.base_dir}/{target_name}/{params_tools_log_path}"
            self.root = ET.Element("ParamsToolsLog")
        else:
            print(f"[Error] The Logging type '{self.log_type}' does not exist")

        # Create directory
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
            
        self.timestamp = timestamp
        xml_timestamp_node = ET.SubElement(self.root, 'TimeStamp')
        xml_timestamp_node.text = self.timestamp
        xml_target_node = ET.SubElement(self.root, 'Target Domain')
        xml_target_node.text = self.target_name

    def add_tool_log(self, tool_tag_name, expected_command, output):
        output_array = output.split("\n")
        if output_array[0] in expected_command:
            print(f"[Error] Logging different command than the expected command for tool '{tool_tag_name}'")
        xml_tool_node = ET.SubElement(self.root, f"{tool_tag_name}_output", command=expected_command)
        xml_tool_node.text = "\n".join(output_array)

    def save_log(self):
        xml_file_name = self.timestamp
        tree = ET.ElementTree(self.root)
        tree.write(f"{self.target_dir}/{xml_file_name}.xml")
        return f"{self.target_dir}/{xml_file_name}.xml"

    def get_output_order(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        output_order = config['log']['output_order']
        return output_order.split(',\n')

    def get_target_logs_dir(self):
        return self.target_dir


