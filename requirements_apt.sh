# Run this with sudo
!#/bin/bash

apt install whois

# External tool installation
rm -rf ~/BBP_sus_tools_base/
mkdir ~/BBP_sus_tools_base
cd ~/BBP_sus_tools_base
git clone https://github.com/b3n-j4m1n/snrublist3r.git
pip install -r ./snrublist3r/requirements.txt
