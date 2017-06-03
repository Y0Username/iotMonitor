#!/usr/bin/python3

# Copyright 2015-2017 Zack Scholl. All rights reserved.
# Copyright 2015-2017 Yathish S Gangolli. All rights reserved.
# Use of this source code is governed by a AGPL
# license that can be found in the LICENSE file.

import sys
import json
import socket
import time
import subprocess
import os
import glob
import argparse
import logging
import statistics
import atexit
import datetime
import pymongo
import requests
import pub
import traffic
import weather
import timestampnow

logger = logging.getLogger('scan.py')


def restart_wifi():
    os.system("/sbin/ifdown --force wlan0")
    os.system("/sbin/ifup --force wlan0")
    os.system("iwconfig wlan0 mode managed")
    while True:
        ping_response = subprocess.Popen(
            ["/bin/ping", "-c1", "-w100", "lf.internalpositioning.com"], stdout=subprocess.PIPE).stdout.read()
        if '64 bytes' in ping_response.decode('utf-8'):
            break
        time.sleep(1)


def num_wifi_cards():
    cmd = 'iwconfig'
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    output = p.stdout.read().decode('utf-8')
    return output.count("wlan")


def process_scan(time_window):
    logger.debug("Reading files...")
    output = ""
    maxFileNumber = -1
    fileNameToRead = ""
    for filename in glob.glob("/tmp/tshark-temp*"):
        fileNumber = int(filename.split("_")[1])
        if fileNumber > maxFileNumber:
            maxFileNumber = fileNumber
            fileNameToRead = filename
    logger.debug("Reading from %s" % fileNameToRead)
    cmd = subprocess.Popen(("tshark -r "+fileNameToRead+" -T fields -e wlan.sa -e wlan.bssid -e radiotap.dbm_antsignal").split(
    ), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output += cmd.stdout.read().decode('utf-8')

    fingerprints = {}
    relevant_lines = 0
    # print(output)
    for line in output.splitlines():
        try:
            mac, mac2, power_levels = line.split("\t")
            if mac == mac2 or len(mac) == 0:
                continue

            relevant_lines+=1
            rssi = power_levels.split(',')[0]
            if len(rssi) == 0:
                continue

            if mac not in fingerprints:
                fingerprints[mac] = []
            fingerprints[mac].append(float(rssi))
        except:
            pass
    logger.debug("..done")

    # Compute medians
    fingerprints2 = []
    for mac in fingerprints:
        if len(fingerprints[mac]) == 0:
            continue
        fingerprints2.append(
            {"mac": mac, "rssi": int(statistics.median(fingerprints[mac]))})

    logger.debug("Processed %d lines, found %d fingerprints in %d relevant lines" %
                 (len(output.splitlines()), len(fingerprints2),relevant_lines))

    now = datetime.datetime.now()
    # old_payload = {"_id": int(time.time()), "time": now.strftime("%c"), "fingerprints": int(len(fingerprints2)), "signals": fingerprints2}
    # my_payload = {"_id": now.strftime("%c"), "day": now.strftime("%A"), "hour": now.hour, "minute": now.minute, "customers": int(len(fingerprints2))}
    payload = {'time': timestampnow.get_time(), 'pi': int(len(fingerprints2)), 'weather': weather.get_weather_data(), 'traffic': traffic.get_traffic_data()}
    print("Total devices: " + str(len(fingerprints2)))
    return payload


def run_command(command):
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


def tshark_is_running():
    ps_output = subprocess.Popen("ps aux".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ps_stdout = ps_output.stdout.read().decode('utf-8')
    isRunning = 'tshark' in ps_stdout and '[tshark]' not in ps_stdout
    logger.debug("tshark is running: " + str(isRunning))
    return isRunning


def start_scan(wlan):
    if not tshark_is_running():
        # Remove previous files
        for filename in glob.glob("/tmp/tshark-temp*"):
            os.remove(filename)
        logger.info("Starting scan...")
        subprocess.Popen(("/usr/bin/tshark -I -i " + wlan + " -b files:4 -b filesize:1000 -w /tmp/tshark-temp").split(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tshark_is_running()


def stop_scan():
    if tshark_is_running():
        os.system("pkill -9 tshark")
        logger.info("Stopped scan")
        tshark_is_running()

def write_to_db(address, payload):
    #mongodb
    try:
	connection = pymongo.MongoClient(host=[address])
	db = connection.Java
	collection = db.customers
	collection.insert(payload)
        logger.info("Written to DB")
    except pymongo.errors, e:
        print "DB Operation Failed with: %s" % e

def write_to_db_full(address, payload):
    #mongodb
    try:
	connection = pymongo.MongoClient(host=[address])
	db = connection.JavaFull
	collection = db.AllCustomers
	collection.insert(payload)
        logger.info("Written to DB")
    except pymongo.errors, e:
        print "DB Operation Failed with: %s" % e


def main():
    # Check if SUDO
    # http://serverfault.com/questions/16767/check-admin-rights-inside-python-script
    if os.getuid() != 0:
        print("you must run sudo!")
        return

    # Check which interface
    # Test if wlan0 / wlan1
    default_wlan = "wlan0"
    default_single_wifi = False
    if num_wifi_cards() == 1:
        default_single_wifi = True
        default_wlan = "wlan0"

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group", default="", help="group name")
    parser.add_argument("-i", "--interface", default=default_wlan, help="Interface to listen on - default %s" % default_wlan)
    parser.add_argument("-t", "--time", default=60, help="scanning time in seconds (default 60)")
    parser.add_argument("--single-wifi", default=default_single_wifi, action="store_true", help="Engage single-wifi card mode?")
    # parser.add_argument("-d", "--database", default="https://lf.internalpositioning.com", help="send payload to this database")
    parser.add_argument("-d", "--database", default="127.0.0.1:27017", help="send payload to this database")
    parser.add_argument("-n", "--nodebug", action="store_true")
    parser.add_argument("-s", "--sleep", default=10, help="set sleep time in seconds (default 600)" )
    args = parser.parse_args()

    # Check arguments for logging
    loggingLevel = logging.DEBUG
    if args.nodebug:
        loggingLevel = logging.ERROR
    logger.setLevel(loggingLevel)
    fh = logging.FileHandler('scan.log')
    fh.setLevel(loggingLevel)
    ch = logging.StreamHandler()
    ch.setLevel(loggingLevel)
    formatter = logging.Formatter('%(asctime)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    # Startup scanning
    # logger.debug("Starting database " + args.database)

    # logger.debug("Starting database " + args.database)
    # os.system('nohup mongod --dbpath /var/lib/mongodb &')
    # print("Using database " + args.database)
    # logger.debug("Using database " + args.database)
    logger.debug("Setting interface in monitor mode")
    os.system('nexutil -m2')
    # print("Using group " + args.group)
    # logger.debug("Using group " + args.group)

    while True:
        try:
            logger.debug("Starting scan...")
            start_scan(args.interface)
            print("Scan for " + str(float(args.time)) + " seconds" )
            time.sleep(float(args.time))
            logger.debug("Stopping scan...")
            stop_scan()
            payload = process_scan(args.time)
            logger.debug("Publishing to DB...")
            pub.pubsub(payload)
            print("Sleep for " + str(float(args.sleep)) + " seconds" )
            time.sleep(float(args.sleep))  # Wait before getting next window
        except Exception:
            logger.error("Fatal error in main loop", exc_info=True)
            time.sleep(float(args.time))


def exit_handler():
    # print("Exiting...stopping scan..")
    logger.info("Exiting...stopping scan..")
    os.system("pkill -9 tshark")
    # print("Exiting...killing db..")
    # logger.info("Exiting...killing db..")
    # os.system("pkill mongod")
    # print("Exiting...stoping monitor mode..")
    logger.info("Exiting...stopping monitor mode..")
    os.system("nexutil -m0")

if __name__ == "__main__":
    atexit.register(exit_handler)
    main()
