#!/bin/bash
###############################
#  Author: Dharshin De Silva  #
###############################
if [ $# -lt 1 ]
then
  echo "Syntax: ./gnmap2csv direcotory-with-.gnmap-files"
  exit -1
fi

echo "\"IP Address\",\"TCP/UDP\",\"Port\",\"Service\""
cat $1/*.gnmap |  grep '/open/' | sort -u | awk -F'Host: | \(\).+Ports: |, ' '{ printf "%s", $2; first=1; for(i=3; i < NR; i++) { split($i,a,"/"); if(a[2]=="open") { if(first==0) { print""; } printf ",%s,%s,%s",a[3],a[1],a[7]; first=0; } } print""; }'