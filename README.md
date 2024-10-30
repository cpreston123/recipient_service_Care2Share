# recipient_service_Care2Share

## Overview
Recipient service for Care2Share Application (atomic service) (containerized with Docker).
Running on Port 8002. 

### Running and Testing on VM
```
source venv/bin/activate
*start docker container*
docker-compose up --build
^Z
bg %1
curl localhost:8002
fg %1
^C
```
On browser, access http://localhost:8002/


### Set up + Running Application Locally
```
sudo apt update

sudo apt install python3 python3-pip -y

git clone https://github.com/cpreston123/recipient_service_Care2Share.git

sudo apt install python3.12-venv

sudo python3 -m venv ./venv

source venv/bin/activate

*start docker container*

docker compose up --build
```
See above "Running and Testing on VM" to test application
