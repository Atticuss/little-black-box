#!/bin/sh

set -e

KIBANA_CONF_FILE="/opt/kibana/config/kibana.yml"
BASE=/opt/kibana
KIBANA_ES_URL=${KIBANA_ES_URL:-http://elasticsearch:9200}
KIBANA_HOST=${KIBANA_HOST:-0.0.0.0}

if [ ! -z "${ES_PLUGINS_INSTALL}" ]; then
   OLDIFS=$IFS
   IFS=','
   for plugin in ${ES_PLUGINS_INSTALL}; do
      if ! $BASE/bin/kibana-plugin list | grep -qs ${plugin}; then
         until $BASE/bin/kibana-plugin install ${plugin}; do
           echo "failed to install ${plugin}, retrying in 3s"
           sleep 3
         done
      fi
   done
   IFS=$OLDIFS
fi

#sed -i "s;.*elasticsearch\.url:.*;elasticsearch\.url: ${KIBANA_ES_URL};" "${KIBANA_CONF_FILE}"
#sed -i "s;.*server\.host:.*;server\.host: ${KIBANA_HOST};" "${KIBANA_CONF_FILE}"

#if [ -n "${KIBANA_INDEX}" ]; then
#    echo "setting index!"
#    sed -i "s;.*kibana\.index:.*;kibana\.index: ${KIBANA_INDEX};" "${KIBANA_CONF_FILE}"
#fi

# mesos-friendly change
unset HOST
unset PORT

exec /opt/kibana/bin/kibana
