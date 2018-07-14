#!/bin/bash

yes "Here is a sample sentence. Please repeat." | head -n 500000 > medium_test.txt
yes "Here is a sample sentence. Please repeat." | head -n 5000000 > large_test.txt
