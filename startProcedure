#!/bin/sh

/usr/bin/pinSetup.sh 
/usr/bin/theWeather_system_server &
/usr/bin/sendIP.py &

echo "Done with service" > /dev/kmsg
exit