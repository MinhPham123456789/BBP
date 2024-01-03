# Run this with sudo
!#/bin/bash

apt install whois

# External tool installation

## Snrublist3r installation
rm -rf ~/BBP_sus_tools_base/
mkdir ~/BBP_sus_tools_base
cd ~/BBP_sus_tools_base
git clone https://github.com/b3n-j4m1n/snrublist3r.git
pip install -r ./snrublist3r/requirements.txt
## Chaos ProjectDiscovery
go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest
# Note: Add export CHAOS_KEY=CHAOS_API_KEY in bash profile script