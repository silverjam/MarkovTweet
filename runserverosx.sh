#!/bin/sh

d=`dirname $0`
python2.5 $d/vendor/google_appengine/dev_appserver.py $d/markov --show_mail_body --smtp_host=smtp.comcast.net --debug
