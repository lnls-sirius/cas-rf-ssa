#!/bin/sh

# Start the first process
./socat.sh -D
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start socat.sh: $status"
  exit $status
fi

# Start the second process
./Sirius-CAS-RF-RING.py -D

while sleep 1.; do
  ps aux |grep socat.sh |grep -q -v grep
  SOCAT_STATUS=$?
  # If the greps above find anything, they exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $SOCAT_STATUS -ne 0 ]; then
    
    # Start the first process
    ./socat.sh -D
    status=$?
    echo "Failed to start socat.sh: $status"

  fi
done