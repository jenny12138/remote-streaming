#!/bin/bash

echo "Create new WIFI network or connect to existing wifi network? Type NEW or EXISTING. Otherwise, to shut down wifi network, type SHUTDOWN"
read MODE

if [ "$MODE" = "NEW" ]; then
    echo "con-name?"
    read CONNAME
    echo "ssid?"
    read SSID
    echo "password?"
    read PASSWORD
    nmcli -s dev wifi hotspot con-name $CONNAME password $PASSWORD ssid $SSID
    echo "Network $CONNAME successfully created and connected."
elif [ "$MODE" = "EXISTING" ]; then
    echo "name (con-name, not SSID) of the wifi network you wish to connect to?"
    read NAME
    nmcli con up $NAME
    echo "You have successfully connected to $NAME."
elif [ "$MODE" = "SHUTDOWN" ]; then
    echo "name (con-name, not SSID) of the wifi network you wish to shut down?"
    read NAME
    nmcli con down $NAME
    echo "You have successfulluy shut down $NAME"
else
    echo "please choose one of the given options and try again."
fi