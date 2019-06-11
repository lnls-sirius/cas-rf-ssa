# Makefile for Asyn SSABooster support
#
# Created by root on Mon Jun 10 16:54:12 2019
# Based on the Asyn streamSCPI template

TOP = .
include $(TOP)/configure/CONFIG

DIRS := configure
DIRS += $(wildcard *[Ss]up)
DIRS += $(wildcard *[Aa]pp)
DIRS += $(wildcard ioc[Bb]oot)
DIRS += SSATestingServer

include $(TOP)/configure/RULES_TOP
