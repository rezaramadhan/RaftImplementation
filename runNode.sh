#!/bin/bash

gnome-terminal -e "bash -c \"./node.py 0; exec bash\""
gnome-terminal -e "bash -c \"./node.py 1; exec bash\""
gnome-terminal -e "bash -c \"./node.py 2; exec bash\""
# gnome-terminal -e "bash -c \"./node.py 8000; exec bash\""
# gnome-terminal -e "bash -c \"./node.py 9000; exec bash\""
