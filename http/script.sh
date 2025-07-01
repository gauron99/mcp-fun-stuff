#!/bin/bash


for i in $(seq 1 10); 
do
	name=David$i
	echo $name
	python client.py $name &
done
