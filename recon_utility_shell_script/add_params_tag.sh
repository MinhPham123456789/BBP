#!/bin/bash

add_params_tag()
{
    if [[ $1 == *"?"* ]]; then
        echo "[dyn_url] $1"
    elif [[ $1 == *".js" ]]; then
        echo "[javascript] $1"
    else
        echo "[url] $1"
    fi
}

while IFS= read -r line 
do
    add_params_tag $line
done
