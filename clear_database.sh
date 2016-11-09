!#/usr/bin/bash

psql --dbname=postgres -c "DROP DATABASE qoops;" 
psql --dbname=postgres -c "CREATE DATABASE qoops;"
psql -f tables.sql;
