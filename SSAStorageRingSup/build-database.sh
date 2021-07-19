#!/bin/sh
set -exu

[ -z "$1" ] && echo "arg 1) TOP" && exit 1 || TOP=$1

python __run__.py

cat SI*.db | \
    grep record | \
    grep AlarmConfig | \
    grep -Po  '(?<=")(.*?)(?="\){)' | \
    sort -u \
    > SSAStorageRing01Alarms.req

cat SI*.db | \
    grep record | \
    grep OffsetConfig | \
    grep -Po  '(?<=")(.*?)(?="\){)' | \
    sort -u  \
    > SSAStorageRing01Offsets.req

sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Offsets.req > SSAStorageRing02Offsets.req
sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Alarms.req > SSAStorageRing02Alarms.req
cat SSAStorageRing01*.req > ${TOP}/autosave/SSAStorageRing/SSAStorageRing01.req
cat SSAStorageRing02*.req > ${TOP}/autosave/SSAStorageRing/SSAStorageRing02.req

find . -type f -name "SI*.db" -exec sed -i -e 's/RA-ToSIA01/$(P)/g' {} \;
