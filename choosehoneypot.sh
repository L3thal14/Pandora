#!/bin/bash
# useradd1.sh - A simple shell script to display the form dialog on screen
# set field names i.e. shell variables
port1="."
port2="."
port3="."
port4="."
port5="."
port6="."
portslist=("ssh" "ftp" "smb" "stmp" "telnet" "vnc")
# open fd
exec 3>&1

# Store data to $VALUES variable
VALUES=$(dialog --ok-label "Submit" \
      --backtitle "Pandora" \
      --title "Honeypot Deployment" \
      --form "Choose the Honeypots you wish to deploy to your network and mention the corresponding port numbers by replacing the '.' with your desired port number." \
15 50 0 \
    "SSH:" 1 1    "$port1"     1 10 10 0 \
    "FTP:"    2 1    "$port2"      2 10 15 0 \
    "SMB:"    3 1    "$port3"      3 10 8 0 \
    "STMP:"     4 1    "$port4"     4 10 40 0 \
    "TELNET:"     5 1    "$port5"     5 10 40 0 \
    "VNC:"     6 1    "$port6"     6 10 40 0 \
2>&1 1>&3)

# close fd
exec 3>&-

responsearray=($VALUES)
for ((i = 0; i < ${#responsearray[@]}; i++)); do if [ "${responsearray[$i]}" != "." ]; then DESTINATIONS="$DESTINATIONS${portslist[$i]}:${responsearray[$i]}," ; fi; done

(crontab -l 2>/dev/null; echo "@reboot /usr/bin/env python3 -m honeypots --setup ${DESTINATIONS%?} --config /var/log/psad/config.json &") | crontab -


