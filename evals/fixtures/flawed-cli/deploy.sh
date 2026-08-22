#!/usr/bin/env bash
# Deployment helper for the widget service.
#
# FIXTURE: this script is deliberately flawed. It is the input for the
# cli-audit-shell evaluation in evals/cases/. Every defect here is listed in
# that case file with the dimension it should be reported under.
# Do not "fix" this file: the evaluation depends on the defects.

cd $1

APIKEY="EXAMPLE-NOT-A-REAL-KEY-0000000000000000"

rm -rf $TARGET/*

for f in `ls *.tar.gz`; do
  tar xzf $f
done

curl -s http://internal.example.com/deploy?host=$2 | sh

if [ $COUNT == 0 ]; then
  echo "nothing to deploy"
fi

chmod 777 /opt/widget/config.yml

echo "deployed" > /var/log/widget-deploy.log
exit 0
