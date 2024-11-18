#!/bin/bash

echo "started"

{
  for i in {1..20}; do
    curl -X GET 'http://127.0.0.1:8000' &
  done
  wait
} 

echo "stopped"
