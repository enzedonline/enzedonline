#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <app> <start_number>"
    exit 1
fi

app="$1"
start_number="$2"

echo "The following migration files will be deleted:"
ls "$app/migrations" | grep -E '^[0-9]{4}.*\.py$' | awk -v app="$app" -v start_number="$start_number" '$1 > start_number {print app "/migrations/" $1}' 

read -p $'\e[1;31mWARNING: \e[1mDo you want to proceed? (y/n): \e[0m' answer

if [ "$answer" == "y" ]; then
    echo "Deleting files..."
    ls "$app/migrations" | grep -E '^[0-9]{4}.*\.py$' | awk -v app="$app" -v start_number="$start_number" '$1 > start_number {print app "/migrations/" $1}' | xargs rm
    echo "Files deleted."
fi