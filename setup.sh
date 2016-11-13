#!/usr/bin/env bash

sudo -u qoops psql --dbname=postgres -c "CREATE DATABASE qoops;"
sudo -u qoops psql -f tables.sql
pip3 install -r requirements.txt