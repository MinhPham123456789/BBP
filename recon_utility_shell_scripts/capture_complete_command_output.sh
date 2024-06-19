#!/bin/bash

capture_complete_command_output(){
    complete_output=$(bash -c "$1")
    echo "${complete_output}"
}

capture_complete_command_output "$1"
