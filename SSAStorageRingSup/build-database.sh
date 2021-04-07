#!/bin/sh
set -exu

[ -z "$1" ] && echo "arg 1) TOP" && exit 1 || TOP=$1

python ring.py > SSAStorageRing01.db
cat SSAStorageRing01.db | grep record | grep AlarmConfig | grep -Po  '(?<=")(.*?)(?="\){)' > SSAStorageRing01Alarms.req
cat SSAStorageRing01.db | grep record | grep OffsetConfig | grep -Po  '(?<=")(.*?)(?="\){)' > SSAStorageRing01Offsets.req
sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01.db > SSAStorageRing02.db
sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Offsets.req > SSAStorageRing02Offsets.req
sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Alarms.req > SSAStorageRing02Alarms.req

cat SSAStorageRing01*.req > ${TOP}/autosave/SSAStorageRing/SSAStorageRing01.req
cat SSAStorageRing02*.req > ${TOP}/autosave/SSAStorageRing/SSAStorageRing02.req
