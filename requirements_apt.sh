# Run this with sudo
!#/bin/bash

apt install whois

# External tool installation
# With project using golang, relative binary paths are used

## Seclists


## Wordlist Asset Notes

## Snrublist3r installation
rm -rf ~/BBP_sus_tools_base/
mkdir ~/BBP_sus_tools_base
cd ~/BBP_sus_tools_base
git clone https://github.com/b3n-j4m1n/snrublist3r.git
pip install -r ./snrublist3r/requirements.txt

## paramspider
git clone https://github.com/devanshbatham/ParamSpider.git

## DomainTrail
git clone https://github.com/gatete/DomainTrail.git

## Chaos ProjectDiscovery
go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest
# Note: Add export CHAOS_KEY=CHAOS_API_KEY in bash profile script

## gobuster
sudo apt install gobuster

## gopsider
sudo apt install gospider

## hakrawler
git clone https://github.com/hakluke/hakrawler.git
cd ./hakrawler/
go build
cd ~/BBP_sus_tools_base

## waybackurls
git clone https://github.com/tomnomnom/waybackurls.git

## gau
git clone https://github.com/lc/gau.git
cd ./gau/cmd/gau
go build
cd ~/BBP_sus_tools_base

## katana
git clone https://github.com/projectdiscovery/katana.git
cd ./katana/cmd/katana
go build
cd ~/BBP_sus_tools_base