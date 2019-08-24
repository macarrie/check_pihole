#!/usr/bin/env python2

import json
import optparse
import os
import sys
import time
import urllib2

VERSION = "0.1"
 
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

GREEN = '#2A9A3D'
RED = '#FF0000'
ORANGE = '#f57700'
GRAY = '#f57700'

parser = optparse.OptionParser("%prog [options]", version="%prog " + VERSION)
parser.add_option('-H', '--hostname', dest="hostname", help='Hostname to connect to')
parser.add_option('-p', '--port', dest="port", type="int", default=80, help='Flemzerd port (default: 80)')
parser.add_option('-S', '--use-ssl', dest="https", type="int", default=0,  help='Use SSL')

perfdata = []
output = ""

def add_perfdata(name, value, min="", max="", warning="", critical=""):
    global perfdata
    perfdata.append("%s=%s;%s;%s;%s;%s" % (name, value, min, max, warning, critical))

def exit(status, exit_label=""):
    global perfdata
    global output

    label = exit_label
    color = GRAY

    if status == OK:
        if not label:
            label = "OK"
        color = GREEN
    elif status == WARNING:
        if not label:
            label = "WARNING"
        color = ORANGE
    elif status == CRITICAL:
        if not label:
            label = "CRITICAL"
        color = RED
    else:
        if not label:
            label = "UNKNOWN"
        color = GRAY

    print "<span style=\"color:%s;font-weight: bold;\">[%s]</span> %s | %s" % (color, label, output, " ".join(perfdata))
    sys.exit(status)


def get_stats(hostname, port, https):
    global output

    if https == 1:
        host = "https://%s:%d" % (hostname, port)
    else: 
        host = "http://%s:%d" % (hostname, port)

    url = "%s%s" % (host, "/admin/api.php?summaryRaw")

    try:
        start = time.time()
        req = urllib2.urlopen(url)
        end = time.time()

        data = req.read()
    except urllib2.URLError as e:
        output += "Could not contact pihole: %s" % e
        exit(CRITICAL)

    parsed_data = json.loads(data)

    add_perfdata("response_time", end - start)

    add_perfdata("ads_blocked_today",       parsed_data["ads_blocked_today"])
    add_perfdata("ads_percentage_today",    parsed_data["ads_percentage_today"])
    add_perfdata("clients_ever_seen",       parsed_data["clients_ever_seen"])
    add_perfdata("dns_queries_all_types",   parsed_data["dns_queries_all_types"])
    add_perfdata("dns_queries_today",       parsed_data["dns_queries_today"])
    add_perfdata("domains_being_blocked",   parsed_data["domains_being_blocked"])
    add_perfdata("privacy_level",           parsed_data["privacy_level"])
    add_perfdata("queries_cached",          parsed_data["queries_cached"])
    add_perfdata("queries_forwarded",       parsed_data["queries_forwarded"])
    add_perfdata("reply_CNAME",             parsed_data["reply_CNAME"])
    add_perfdata("reply_IP",                parsed_data["reply_IP"])
    add_perfdata("reply_NODATA",            parsed_data["reply_NODATA"])
    add_perfdata("reply_NXDOMAIN",          parsed_data["reply_NXDOMAIN"])
    add_perfdata("status",                  parsed_data["status"])
    add_perfdata("unique_clients",          parsed_data["unique_clients"])
    add_perfdata("unique_domains",          parsed_data["unique_domains"])


    output = "PiHole stats collected"
    exit(OK)

if __name__ == '__main__':
    # Ok first job : parse args
    opts, args = parser.parse_args()
    if args:
        parser.error("Does not accept any argument.")

    port = opts.port
    hostname = opts.hostname
    if not hostname:
        # print "<span style=\"color:#A9A9A9;font-weight: bold;\">[ERROR]</span> Hostname parameter (-H) is mandatory"
        output = "Hostname parameter (-H) is mandatory"
        exit(CRITICAL, "ERROR")

    get_stats(hostname, port, opts.https)
