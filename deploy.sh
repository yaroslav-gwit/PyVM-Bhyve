#!/usr/bin/env bash

#_ CHECK IF USER IS ROOT _#
if [ "$EUID" -ne 0 ]; then echo " 🚦 ERROR: Please run this script as root user!" && exit 1; fi

#_ INSTALL THE REQUIRED PACKAGES _#
pkg update -y
pkg upgrade -y
pkg install -y nano micro bash bmon iftop mc fusefs-sshfs pftop fish nginx 
pkg install -y rsync gnu-watch tmux fping qemu-utils python39 py39-devtools
pkg install -y htop curl wget gtar unzip pv sanoid cdrkit-genisoimage openssl
pkg install -y bhyve-firmware bhyve-rc grub2-bhyve uefi-edk2-bhyve uefi-edk2-bhyve-csm

#_ PULL THE GITHUB REPO _#
if [[ ! -d /opt/hoster-red/ ]]; then
    mkdir -p /opt/hoster-red/
    git clone https://github.com/yaroslav-gwit/PyVM-Bhyve.git /opt/hoster-red/
else
    cd /opt/hoster-red/
    git pull
fi
if [[ ! -f /opt/hoster-red/.gitignore ]]; then echo "vm_images" > .gitignore; fi

#_ GENERATE SSH KEYS _#
if [[ ! -f /root/.ssh/id_rsa ]]; then ssh-keygen -b 4096 -t rsa -f /root/.ssh/id_rsa -q -N ""; else echo "Old key was found"; fi
if [[ ! -f /root/.ssh/config ]]; then touch /root/.ssh/config && chmod 600 /root/.ssh/config; fi

#_ INCLUDE SSH KEYS _#
#cat /root/.ssh/id_rsa.pub

#_ REGISTER IF REQUIRED DATASETS EXIST _#
ENCRYPTED_DS=`zfs list | grep -c "zroot/vm-encrypted"`
UNENCRYPTED_DS=`zfs list | grep -c "zroot/vm-unencrypted"`
ZFS_RANDOM_PASSWORD=`openssl rand -base64 32 | sed "s/=//g" | sed "s/\///g" | sed "s/\+//g"`

#_ CREATE ZFS DATASETS IF THEY DON'T EXIST _#
if [[ ${ENCRYPTED_DS} < 1 ]]
then
    echo -e "${ZFS_RANDOM_PASSWORD}" | zfs create -o encryption=on -o keyformat=passphrase zroot/vm-encrypted
fi

if [[ ${UNENCRYPTED_DS} < 1 ]]
then
    zfs create zroot/vm-unencrypted
fi

#_ BOOTLOADER OPTIMISATIONS _#
BOOTLOADER_FILE="/boot/loader.conf"
CMD_LINE='fusefs_load="YES"'
if [[ `grep -c ${CMD_LINE} ${BOOTLOADER_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${BOOTLOADER_FILE}; fi
CMD_LINE='vm.kmem_size="330M"'
if [[ `grep -c ${CMD_LINE} ${BOOTLOADER_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${BOOTLOADER_FILE}; fi
CMD_LINE='vm.kmem_size_max="330M"'
if [[ `grep -c ${CMD_LINE} ${BOOTLOADER_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${BOOTLOADER_FILE}; fi
CMD_LINE='vfs.zfs.arc_max="40M"'
if [[ `grep -c ${CMD_LINE} ${BOOTLOADER_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${BOOTLOADER_FILE}; fi
CMD_LINE='vfs.zfs.vdev.cache.size="5M"'
if [[ `grep -c ${CMD_LINE} ${BOOTLOADER_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${BOOTLOADER_FILE}; fi

#_ PF CONFIG BLOCK IN rc.conf _#
RC_CONF_FILE="/etc/rc.conf"
CMD_LINE='pf_enable="yes"'
if [[ `grep -c ${CMD_LINE} ${RC_CONF_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${RC_CONF_FILE}; fi
CMD_LINE='pf_rules="/etc/pf.conf"'
if [[ `grep -c ${CMD_LINE} ${RC_CONF_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${RC_CONF_FILE}; fi
CMD_LINE='pflog_enable="yes"'
if [[ `grep -c ${CMD_LINE} ${RC_CONF_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${RC_CONF_FILE}; fi
CMD_LINE='pflog_logfile="/var/log/pflog"'
if [[ `grep -c ${CMD_LINE} ${RC_CONF_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${RC_CONF_FILE}; fi
CMD_LINE='pflog_flags=""'
if [[ `grep -c ${CMD_LINE} ${RC_CONF_FILE}` < 1 ]]; then echo ${CMD_LINE} >> ${RC_CONF_FILE}; fi

#_ SET CORRECT PROFILE FILE _#
cat << 'EOF' | cat > /root/.profile
# $FreeBSD$
# This is a .profile template for FreeBSD Bhyve Hosters

PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin:~/bin
export PATH
HOME=/root
export HOME
TERM=${TERM:-xterm}
export TERM
PAGER=less
export PAGER

# set ENV to a file invoked each time sh is started for interactive use.
ENV=$HOME/.shrc; export ENV

# Query terminal size; useful for serial lines.
if [ -x /usr/bin/resizewin ] ; then /usr/bin/resizewin -z ; fi

# Uncomment to display a random cookie on each login.
# if [ -x /usr/bin/fortune ] ; then /usr/bin/fortune -s ; fi

EDITOR=micro
export EDITOR

HOSTER_RED_WD="/opt/hoster-red/"
export HOSTER_RED_WD

VENV="yes"
export VENV
EOF
