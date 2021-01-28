FROM debian:stable-slim

RUN apt update && \
    apt install snapclient alsa-utils dnsutils procps curl inetutils-ping -y && \
    echo "dtoverlay=hifiberry-dacplus\nforce_eeprom_read=0" >> /boot/config.txt
CMD /usr/bin/snapclient -h $SNAPSERVER