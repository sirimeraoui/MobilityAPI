# MobilityAPI
This server is a Python API that allows GET, POST, PUT, and DELETE operations on MobilityDB. The server utilizes the [PyMEOS](https://github.com/MobilityDB/PyMEOS) library.
This implementation follows the OGC API - Moving Features Standard

## Introduction
This Python API server provides endpoints for interacting with MobilityDB, a temporal extension for PostgreSQL. It allows users to perform CRUD operations (Create, Read, Update, Delete) on MobilityDB data using HTTP methods.

## Features
- Supports GET, POST, PUT, and DELETE operations.
- Integrates the PyMEOS library for seamless interaction with MobilityDB.
- Provides endpoints for managing data stored in MobilityDB.

## Prerequisites
- Linux (ubuntu)
- A recent version of Pyhton


## RUN SERVER
- Make script executable: chmod +x run.sh
- Run only the server: ./run.sh
#### RUN SERVER WITH TESTS
- Download ships datasets from: [Denmark Ships DataSets](http://aisdata.ais.dk/?prefix=2024/) aisdk_2024-08-07.zip in data folder
- Run with integration tests: ./run.sh --with-tests (note: this takes a while due to data preprocessing - expect 23 min )

## Usage
Send http requests to the api using any http service.
As an example, your can use the ais.sql that will create ships and ship2 tables containing ships data.
To do that you will have to change the path in the script to the path of your .csv file.
Here is a link to download ships datasets: [Denmark Ships DataSets](http://aisdata.ais.dk/?prefix=2024/)
## Developement
This project is in progress.
## License
##Poetry
poetry install



