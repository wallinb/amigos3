#!/bin/bash
echo 3 >/sys/class/gpio/wdt_ctl/data
sleep 1
echo 0 >/sys/class/gpio/wdt_ctl/data
sleep 1
echo 3 >/sys/class/gpio/wdt_ctl/data
