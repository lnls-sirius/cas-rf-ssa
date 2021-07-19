#!/bin/sh
set -exu

[ -z "$1" ] && echo "arg 1) TOP" && exit 1 || TOP=$1

python3 ${TOP}/SSABoosterSup/__run__.py > SSABooster.db

cat ${TOP}/SSABoosterSup/SSABooster.db | \
    grep record | \
    grep AlarmConfig | \
    grep -Po  '(?<=")(.*?)(?="\){)' \
	> ${TOP}/SSABoosterSup/SSABoosterAlarms.req

cat ${TOP}/SSABoosterSup/SSABooster.db | \
    grep record | \
    grep OffsetConfig | \
    grep -Po  '(?<=")(.*?)(?="\){)' \
	> ${TOP}/SSABoosterSup/SSABoosterOffsets.req
