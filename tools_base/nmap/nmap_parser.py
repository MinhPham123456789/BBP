from xml.etree import ElementTree as ET
import re
from xml.etree.ElementTree import ParseError
from .nmap_exceptions import *

"""
When building up the dictionary to be print by the print_nmap_xml
when there is a nested dictionary
Put the sub dictionary/ies in a list to be parsed later on ([{},{}])
The key of the sub dictionary/ies is the sub section name so name it reasonably
"""

def get_xml_root(command_output):
    try:
        return ET.fromstring(command_output)
    except ParseError:
        raise NmapXMLParserError()

def get_scan_metadata(xml_root):
    """
    This function gets metadata in nmaprun tag, which is actually
    the root node
    :param xml_root: root node of the nmap XML output
    :return:
        A dictionary storing the metadata of the scan
    """
    attribute_list = ["args", "version", "startstr"]
    nmaprun_dict = {}
    for att in attribute_list:
        nmaprun_dict[att] = xml_root.get(att)
    return nmaprun_dict

def get_hosts_list(xml_root):
    hosts = xml_root.findall("host")
    return hosts

def get_host_basic_data(host_node):
    attribute_list = ["starttime", "endtime"]
    host_basic_data_dict = {}
    for att in attribute_list:
        host_basic_data_dict[att] = host_node.get(att)
    host_basic_data_dict["status"] = host_node.find("status").get("state")
    host_basic_data_dict["address"] = host_node.find("address").get("addr")
    hostscript_output = get_host_script(host_node)
    host_basic_data_dict["hostscripts"] = hostscript_output
    # if hostscript_output is not None:
    #     host_basic_data_dict["hostscripts"] = hostscript_output
    # else:
    #     host_basic_data_dict["hostscripts"] = [None]
    return host_basic_data_dict

def get_host_script(host_node):
    host_script_node = host_node.find("hostscript")
    if host_script_node is None:
        return None
    host_scripts_list = host_script_node.findall("script")
    host_script_dicts_list = []
    host_script_attributes = ["id", "output"]
    for host_script in host_scripts_list:
        host_script_dict = {}
        for host_script_att in host_script_attributes:
            host_script_dict[host_script_att] = host_script.get(host_script_att)
        host_script_dicts_list.append(host_script_dict)
    return host_script_dicts_list


def get_extra_ports(host_node):
    extra_ports_dict = {}
    extra_ports_node = host_node.find("ports").find("extraports")
    attribute_list = ["state", "count"]
    for att in attribute_list:
        extra_ports_dict[att] = extra_ports_node.get(att)
    extra_reasons_list = []
    extra_reasons = extra_ports_node.findall("extrareasons")
    reason_atttributes = ["reason", "count"]
    for ex_reason_node in extra_reasons:
        reason_dict = {}
        for reason_att in reason_atttributes:
            reason_dict[reason_att] = ex_reason_node.get(reason_att)
        extra_reasons_list.append(reason_dict)
    extra_ports_dict["extrareasons"] = extra_reasons_list
    return extra_ports_dict

def get_ports_list(host_node):
    """
    This function returns ports list inside a host node
    :param host_node: host xml node
    :return:
        A list of ports in the chosen host xml node
    """
    port_node = host_node.find("ports")
    ports = port_node.findall("port")
    return ports

def get_port_data(port_node):
    attribute_list = ["protocol", "portid"]
    port_dict = {}
    # Get port tag data
    for att in attribute_list:
        port_dict[att] = port_node.get(att)
    # Get state tag data
    state_node = port_node.find("state")
    port_dict["state"] = state_node.get("state")
    port_dict["reason"] = state_node.get("reason")
    # Get service tag data
    service_dict = {}
    service_attributes = ["name", "servicefp", "product", "version", "ostype", "extrainfo", "conf"]
    service_node = port_node.find("service")
    for service_att in service_attributes:
        service_dict[service_att] = service_node.get(service_att)
    # Get the CPE tag data and put it in the service dict
    cpe_nodes_list = service_node.findall("cpe")
    if len(cpe_nodes_list) > 0:
        for index in range(0, len(cpe_nodes_list)):
            service_dict[f"cpe{index}"] = cpe_nodes_list[index].text.split(":",1)[1]
    # Put service_dict inside port_dict
    port_dict["service"] = []
    port_dict["service"].append(service_dict)
    # Get script output in port
    script_output = get_script_output(port_node)
    port_dict["scripts"] = script_output
    return port_dict

def get_script_output(port_node):
    scripts_list = port_node.findall("script")
    if len(scripts_list) == 0:
        return None
    script_dicts_list = []
    script_attributes = ["id", "output"]
    for script_item in scripts_list:
        script_dict = {}
        for script_att in script_attributes:
            script_dict[script_att] = script_item.get(script_att)
        script_dicts_list.append(script_dict)
    return script_dicts_list

def get_scan_summary(xml_root):
    runstats_node = xml_root.find("runstats")
    runstats_dict = {}
    runstats_dict["summary"] = runstats_node.find("finished").get("summary")
    return runstats_dict

def construct_nmap_data_to_be_parsed(xml_output_string):
    xml_root = get_xml_root(xml_output_string)
    hosts_list = get_hosts_list(xml_root)
    hosts_data_list = []
    sections_list = []
    # Get the scan metadata
    hosts_data_list.append([[get_scan_metadata(xml_root)]])
    sections_list.append(["SCAN METADATA"])
    if len(hosts_list) > 0:
        for host_node in hosts_list:
            section_names = []
            one_host_data_list = []
            # Get host data
            one_host_data_list.append([get_host_basic_data(host_node)])
            section_names.append("HOST")
            # Get extra port data
            one_host_data_list.append([get_extra_ports(host_node)])
            section_names.append("EXTRA PORT DETAILS")
            # Get ports data
            ports_list = get_ports_list(host_node)
            if ports_list is not None:
                port_data_dicts_list = []
                for port_node in ports_list:
                    port_data_dicts_list.append(get_port_data(port_node))
                one_host_data_list.append(port_data_dicts_list)
                section_names.append("PORTS")
                hosts_data_list.append(one_host_data_list)
                sections_list.append(section_names)
    # Get summary
    hosts_data_list.append([[get_scan_summary(xml_root)]])
    sections_list.append(["SUMMARY"])
    return hosts_data_list, sections_list
