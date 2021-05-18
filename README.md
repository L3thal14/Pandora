# Pandora

With the growing need for protection from cyber-attacks and cybercrimes, it is of utmost importance to develop efficient methods, which take inspiration from previous literature and evolve upon them. Any intercommunication and storage of data on the internet are becoming precarious. It becomes vital to keep our home network well updated in terms of security, curtail loopholes and ensure data integrity and incorruptibility. It is now essential that we protect and secure our home networks and devices from cyber-attacks. This repository contains the code for a ready-to-deploy Intrusion Detection Honeypot that monitors, logs, and notifies the spoof attempts by attackers to break into the system in real-time.

## Installation

You can run this on any Debian-based Linux system. (Tested on Ubuntu 18.04) <br/>
Deploy the flask server in the `deploy-server` folder to any PaaS of your choice.
Run the following commands from the terminal:

1.  `git clone https://github.com/L3thal14/Pandora.git`
2.  `cd Pandora`
3.  `nano .env`
4.  Edit the .env file as `DEPLOY_URL="http://<YOUR_FLASK_SERVER>/"`
5.  Edit line 48 of `dummyserver/details.html` as `let url = "http://<YOUR_FLASK_SERVER>/httplogs";`
6.  `chmod a+x install.sh`
7.  `sudo ./install.sh`

Please note: Installing this will cause some changes in your system. So it is advised to use a Raspberry Pi instead. Most notably, it will change your iptables. Please proceed with caution if you are using the system for other purposes. You can use a VM for testing purposes.

**NOTE :** Head over to [https://www.google.com/settings/security/lesssecureapps](https://www.google.com/settings/security/lesssecureapps) and turn it ON to allow sending emails via SMTP.
