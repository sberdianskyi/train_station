
# Train Station API

The Train Station API allows you to store data about train stations, 
trains, routes, tickets and crews. You have the ability to create, read, 
update and delete entries related to medical transport.

## Installation using GitHub

Install PostgresSQL and create DB

```shell
git clone https://github.com/sberdianskyi/train_station
cd train-station
python -m venv venv
venv\Scripts\activate # for Windows
source vevn/bin/activate # for MacOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Don't forget to fill your .env file according to .env_example

## Run with Docker

Docker should be installed and you need to be in directory with docker-compose.yaml file

```shell
docker-compose build ...
docker-compose up ...
```

And state what happens step-by-step.

## Getting access

register a new user using the /api/user/register/ endpoint. 
Obtain an authentication(access) token by sending a POST request 
to the /api/user/token/ endpoint with your email and password. 
Use the obtained token in the authorization header for accessing 
protected endpoints (Authoriazation: Bearer <Your access token>). 
Be free to explore various endpoints for different functionalities 
provided by the API.


## Features

* JWT Authentication
* Admin panel (/admin/)
* Documentation (located at api/schema/swagger-ui/)
* Managing Orders and Tickets
* Creating Routes with Stations
* Distance between stations is calculated based on coordinates.
* Creating Journeys, Crews, Trains, Train Types
* Filtering Journeys using different parameters
* Uploading images for each Crew
