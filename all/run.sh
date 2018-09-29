#!/bin/bash
sudo /opt/redis-4.0.8/src/redis-server /opt/redis-4.0.8/src/redis.conf &
cd /opt/all/FlaskRestful
sudo python3 SysFlaskRestful.py &
sudo /opt/all/influxdb-1.6.1-1/usr/bin/influxd &

