# ~/.bashrc: executed by bash(1) for non-login shells.

export PS1='\h:\w\$ '

umask 077

set -o vi

alias ls='ls -la --color=auto'
alias cdc='cd /media/mmcblk0p1'

source /media/mmcblk0p1/honcho/bin/set_env.sh
