#!/bin/bash

echo "init of server.json"
echo "{}" > /var/lib/snapserver/server.json
echo "spotify starting"
snapserver -s "spotify:///librespot?name=Spotify&username=${SPOT_USERNAME}&password=${SPOT_PASSWORD}&devicename=Deck&bitrate=320&killall=false"