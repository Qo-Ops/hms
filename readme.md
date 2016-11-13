In order to run this project on your computer you need to have the following applications installed locally:
python3
postgresql (>=9.5) (with psql console)
pip3
bash

You also need a local user 'qoops' that needs to have access to database
Postgresql needs to be configured as follows:
user 'qoops'
run on port 5432
not require a password on connection

Before running the application for the first time you need to run ./setup.sh first.
To run the application run ./start.sh in shell