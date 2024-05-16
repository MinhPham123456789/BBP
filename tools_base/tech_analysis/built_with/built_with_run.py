import requests
import configparser
import requests
from bs4 import BeautifulSoup as bs

from recon_utils import *

class BuiltWithAnalysis:
    """
    This class initiates an object to carry out a request to BuiltWith website to 
    detect the target's technologies
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.subdomain_target = target
        self.tool = "built_with_analysis"
        self.command_config_path = command_config_path
        self.url = get_command(self.command_config_path, self.tool)
        self.url = replace_target(self.url, self.subdomain_target)
        self.timeout = 10
        self.output = ""
        self.timestamp = timestamp
        self.debug = debug

    def run_command(self):
        req = requests.get(url=self.url, timeout=self.timeout)
        self.output = f'URL: {self.url}\n'
        if req.status_code == 200:
            html_reader = bs(req.content.decode('utf-8'), 'html.parser')
            divs_list = html_reader.find_all('div', {'class':'card-body pb-0'})
            h6_tag_text_lists = [] # Leave here for potential usage
            a_tag_text_lists = [] # Leave here for potential usage
            for div_item in divs_list:
                h6_list_temp = div_item.find_all('h6', {'class':'card-title text-secondary'})
                h6_list = [h6_item.text for h6_item in h6_list_temp]
                h6_text = ' aka '.join(h6_list)
                h6_tag_text_lists.append(h6_text)
                a_list_temp = div_item.find_all('a', {'class':'text-dark'})
                a_list = [a_item.text for a_item in a_list_temp]
                a_text = ', '.join(a_list)
                a_tag_text_lists.append(a_text)
                self.output = f'{self.output}\n{h6_text}:\n{a_text}\n'
        else:
            error_text = f'{str(req.status_code)}\nContent:\n{req.text}\n'
            self.output = f'{self.output}\n{error_text}'
        print(f"[Process]{self.tool} completed!")
        if self.debug:
            print(self.output)
        return self.output