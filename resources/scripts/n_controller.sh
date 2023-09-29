#!/bin/bash

for((i=1;i<=$2;i++))
do
    python controller.py $1 $i
done