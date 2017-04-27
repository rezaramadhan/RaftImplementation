#!/bin/bash

gnome-terminal -e "bash -c \"./node.py 5000; exec bash\""
gnome-terminal -e "bash -c \"./node.py 6000; exec bash\""
gnome-terminal -e "bash -c \"./node.py 7000; exec bash\""
# gnome-terminal -e "bash -c \"./node.py 8000; exec bash\""
# gnome-terminal -e "bash -c \"./node.py 9000; exec bash\""
