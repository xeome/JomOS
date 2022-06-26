#!/bin/bash

## ANSI Colors (FG & BG)
RED="$(printf '\033[31m')" GREEN="$(printf '\033[32m')" ORANGE="$(printf '\033[33m')" BLUE="$(printf '\033[34m')"
MAGENTA="$(printf '\033[35m')" CYAN="$(printf '\033[36m')" WHITE="$(printf '\033[37m')" BLACK="$(printf '\033[30m')"
REDBG="$(printf '\033[41m')" GREENBG="$(printf '\033[42m')" ORANGEBG="$(printf '\033[43m')" BLUEBG="$(printf '\033[44m')"
MAGENTABG="$(printf '\033[45m')" CYANBG="$(printf '\033[46m')" WHITEBG="$(printf '\033[47m')" BLACKBG="$(printf '\033[40m')"

export color_norm='\033[0m'

#Get username
username=$(whoami)

## Reset terminal colors
reset_color() {
    printf '\033[37m'
}

abort() {
    trap '' EXIT
    printf "${RED}ERROR: %s\\n${color_norm}" "${@}" >&2
    exit 1
}

echo $RED
cat <<EOF
              ........              │|      JomOS alpha 0.1                                                     
         ..................         │|  JomOS is a meta Linux distribution which allows users to mix-and-match
      ........................      │|  well tested configurations and optimizations with little to no effort 
     ..............;ooc........     │|   
   ................;ddl..........   │|  JomOS integrates these configurations into one largely cohesive system.
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  ........:oo:.....cddc...........  │|  
   .......'lddl::coddl'..........   │|  
     .......,:clllc:,..........     │|  
       .......................      │|  
         ..................         │|  Continuing will:
              ........              │|  - Convert existing installation into JomOS

EOF

echo "Starting installation"

physmem=$(awk '/MemTotal/{print $2}' /proc/meminfo)
physmemg=1 #$(($physmem / 1048576))
swappinessraw=$((400 / $physmemg))
#swappiness=$((  ))
vfscachepressureraw=$(($swappiness * 2))
echo $swappiness
