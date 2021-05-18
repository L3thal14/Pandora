#!/bin/bash

if [ $UID -ne 0 ]
then
 echo "Please run this script as root: sudo install.sh"
 exit 1
fi
chmod a+x choosehoneypot.sh
chmod a+x cronscripts.sh
apt-get -y install dialog
if dialog --title "Welcome to the installation of Pandora" \
--backtitle "Pandora" \
--yesno "Hey Hey! You're about to install Pandora to turn this system into an IDS/honeypot. This install process will change some things on your Pi." 20 60


then echo "continue"
else 
     exit 1
fi

if dialog --title "Updates" \
--backtitle "Pandora" \
--yesno "Let's install some updates. Answer 'no' if you are just experimenting and want to save some time. Otherwise, shall we update now?" 7 60

then 
apt-get update
apt-get dist-upgrade

fi

dialog --infobox "Installing a bunch of software like the log monitoring service and other dependencies...\n" 20 60

apt-get -y install psad msmtp msmtp-mta iptables-persistent libnotify-bin fwsnort 
pip3 install python-dotenv
pip3 install --yes honeypots
cp PSAD2json.py /var/log/psad
cp config.json /var/log/psad
cp activityJSONlogger.py /var/log/psad
cp .env /var/log/psad
cp smtp_email.py /var/log/psad
cp -r dummyserver /var/log/psad
cp cronscripts.sh /var/log/psad
cp emailscript.sh /var/log/psad
ver=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
cp -r honeypots /usr/local/lib/python${ver}/dist-packages

./choosehoneypot.sh


if dialog --title "Email notifications" \
--backtitle "Pandora" \
--yesno "Do u want to be notified over email?" 7 60

then 
user_input=$(\
  dialog --title "Frequency of Email notifications" \
       --backtitle "Pandora" \
         --inputbox "How frequently do you want to be notified in minutes(60-720)?" 8 40 \
  3>&1 1>&2 2>&3 3>&- \
)
exec 3>&1

# Store data to $VALUES variable
VALUES=$(dialog --ok-label "Submit" \
      --backtitle "Pandora" \
      --title "Setting up SMTP server" \
      --form "Provide gmail ID and password for the SMTP server and the email for receiving the logs." \
   15 50 0 \
    "Email Address:" 1 1    "$fromaddr"     1 15 35 0 \
    "Password:"    2 1    "$passwd"      2 15 30 0 \
    "Receive at:"    3 1    "$toaddr"      3 15 35 0 \
2>&1 1>&3)

# close fd
exec 3>&-
arrayfinal=($VALUES)

export fromaddr=${arrayfinal[0]}
export passwd=${arrayfinal[1]}
export toaddr=${arrayfinal[2]}
(crontab -l 2>/dev/null; echo "*/$user_input * * * * /usr/bin/env python3 /var/log/psad/smtp_email.py $fromaddr $passwd $toaddr") | crontab -     
fi
dialog --infobox "Configuration files created. Next we will move those files to the right places." 20 60

iptables --flush
iptables -A INPUT -p igmp -j DROP
iptables -A INPUT -j LOG
iptables -A FORWARD -j LOG
service netfilter-persistent save
service netfilter-persistent restart
psad --sig-update
service psad restart
(crontab -l 2>/dev/null; echo "*/2 * * * * /usr/bin/env python3 /var/log/psad/PSAD2json.py &") | crontab -
(crontab -l 2>/dev/null; echo "*/2 * * * * /usr/bin/env python3 /var/log/psad/activityJSONlogger.py &") | crontab -
(crontab -l 2>/dev/null; echo "@reboot sudo /var/log/psad/cronscripts.sh &") | crontab -
printf "\n \n ok, now reboot and you should be good to go. Then, go portscan the Pandora from another machine and see if you get an alert!\n"

