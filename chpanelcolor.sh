#!/usr/bin/env bash

set -eu

# Set the background color of xfce4-panel; takes 4 arguments:
# R G B A, ranging from 0.0 to 1.0.
#
# Tested only with xfce4-panel 4.13.4 which uses four doubles for
# <property name="background-rgba" type="array">

r=$1
g=$2
b=$3
a=$4

panel=panel-1

set-xfce4-panel-property() {
    xfconf-query --channel xfce4-panel -p "$@"
}

# https://docs.xfce.org/xfce/xfconf/xfconf-query
set-xfce4-panel-property /panels/"$panel"/background-rgba --create \
    -t double -t double -t double -t double \
    -s $r -s $g -s $b -s $a

# Force a whole-panel redraw by toggling background-style
set-xfce4-panel-property /panels/"$panel"/background-style -s 0
set-xfce4-panel-property /panels/"$panel"/background-style -s 1
