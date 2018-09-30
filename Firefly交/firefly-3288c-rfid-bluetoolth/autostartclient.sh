#!/bin/bash
sudo /opt/redis-4.0.8/src/redis-server /opt/redis-4.0.8/src/redis.conf
cd /opt/RFIDBluetooth
sudo python3 /opt/RFIDBluetooth/RfidReadBluetooth.py
