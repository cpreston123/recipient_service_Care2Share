# recipient_service_Care2Share

## Overview

Simple Hello World FastAPI to help students get their first VM deployed on a cloud.
Recipient service for Care2Share Application (microservice) (containerized with Docker).
Running on Port 8002.

## Execution

### AWS Instance

- Create a "free tier" compatible instance.
- Make sure you setup free tier alerting emails.
- I chose Ubuntu Linux.
- You can use the default VPC but create a new security group.
- Make sure you enable remote access.
- Create a new key pair and save the .pem file somewhere safe.
- When EC2 instance is running, connect to it by selecting the instance and then
the connect menu option. Use the default connection manager.

### Running Application Locally / on GCP

- Some commands:
```
sudo apt update

sudo apt install python3 python3-pip -y

git clone https://github.com/cpreston123/recipient_service_Care2Share.git

sudo apt install python3.12-venv

sudo python3 -m venv ./venv

source venv/bin/activate

docker compose up --build

### Remote Access

- Navigate to the security group.
- Add an inbound rule for TCP, port 8002 and 0.0.0.0/0

<img src="inbound-rules.jpg">

- Go back to EC2 instance configuration and get public IP address.
- Mine was 53.208.146.60
- Navigate to http://54.208.146.60:8000/ (__Make sure you use HTTP. Browser default to HTTPS.__)

# Finish

- Shutdown and terminate your instance.
- We can make another one later.






