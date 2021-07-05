#!/bin/sh

# adjust these paths for the installation of alom_exporter on your system
daemon="/usr/local/bin/alom_exporter"
daemon_flags="--config /etc/alom_exporter.yaml"
# this user must exist before running the daemon; create it or change the user
daemon_user=_alom_exporter

. /etc/rc.d/rc.subr

pexp="/usr/local/bin/python3.*${daemon}.*"
rc_bg=YES
rc_reload=NO

rc_start() {
  ${rcexec} "${daemon} ${daemon_flags} 2>&1 | \
    logger -p daemon.info -t alom_exporter"
}

rc_cmd $1
