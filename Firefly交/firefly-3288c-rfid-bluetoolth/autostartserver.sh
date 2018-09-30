#!/bin/bash
#sudo hciconfig hci0 iscan
#sudo sdptool add SP
#sudo hciconfig hci0 noauth
sudo /opt/redis-4.0.8/src/redis-server /opt/redis-4.0.8/src/redis.conf
#sudo cd /opt/RFIDBluetooth-3288c
cd /opt/RFIDBluetooth
#sudo bt_load_broadcom_firmware &
sudo python3 /opt/RFIDBluetooth/RfidReadBluetoothServer.py
