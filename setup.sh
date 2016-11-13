#!/usr/bin/env bash

psql --dbname=postgres -c "CREATE DATABASE qoops;"
psql -f tables.sql
pip3 install -r requirements.txt