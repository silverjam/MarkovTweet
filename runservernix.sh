#!/bin/sh

d=`dirname $0`
dev_appserver.py $d/markov --show_mail_body --smtp_host=smtp.comcast.net --debug
