#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <app> <start_number>"
    exit 1
fi

app="$1"
start_number="$2"

results=$(ls "$app/migrations" | grep -E '^[0-9]{4}.*\.py$' | awk -v app="$app" -v start_number="$start_number" '$1 > start_number {print app "/migrations/" $1}')

if [ -z "$results" ]; then
    echo "No matching migration files found to purge."
    exit 0
fi

echo "$results"

read -p $'\e[1;31mWARNING: \e[1mThe migration files listed above will be deleted. Do you want to proceed? (y/n): \e[0m' answer

if [ "$answer" == "y" ]; then
    echo "Deleting files..."
    echo "$results" | xargs rm
    echo "Files deleted."
fi
