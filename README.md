
MobilityAPI
===============
An open source implementation of the [OGC](https://www.ogc.org/) [Moving-Features API](https://ogcapi.ogc.org/movingfeatures/overview.html) based on [MobilityDB](https://github.com/MobilityDB/MobilityDB/)

<img src="doc/images/mobilitydb-logo.svg" width="200" alt="MobilityDB Logo" />

MobilityDB is developed by the Computer & Decision Engineering Department of the [Université libre de Bruxelles](https://www.ulb.be/) (ULB) under the direction of [Prof. Esteban Zimányi](http://cs.ulb.ac.be/members/esteban/). ULB is an OGC Associate Member and member of the OGC Moving Feature Standard Working Group ([MF-SWG](https://www.ogc.org/projects/groups/movfeatswg)).

<img src="doc/images/OGC_Associate_Member_3DR.png" width="100" alt="OGC Associate Member Logo" />

More information about MobilityDB, including publications, presentations, etc., can be found in the MobilityDB [website](https://mobilitydb.com).

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
- Run with integration tests: ./run.sh --with-tests 
(note: this takes a while due to data preprocessing - expect 23 min if the json data file is not present, 21 sec otherwise )
- If necessary, download ships datasets from: [Denmark Ships DataSets](http://aisdata.ais.dk/?prefix=2024/) aisdk_2024-08-07.zip in data folder
- Manual get requests links on demo.txt
## Usage
Send http requests to the api using any http service.
As an example, your can use the ais.sql that will create ships and ship2 tables containing ships data.
To do that you will have to change the path in the script to the path of your .csv file.
Here is a link to download ships datasets: [Denmark Ships DataSets](http://aisdata.ais.dk/?prefix=2024/)
## Developement
This project is in progress.

## History and Acknowledgements

MobilityAPI builds on the foundation laid by **[pg_mfserv](https://github.com/MobilityDB/pg_mfserv)**, an OGC API – Moving Features prototype authored at ULB in early 2024. The pg_mfserv initial implementation provided the Python-server skeleton, the OGC endpoint shape, and the PyMEOS-based MobilityDB integration pattern that MobilityAPI extends with a structured resource layout, comprehensive test coverage, and OGC-conformant request/response handling.

**pg_mfserv** is preserved in archived form at [`MobilityDB/pg_mfserv`](https://github.com/MobilityDB/pg_mfserv) for historical reference and scholarly attribution; active development continues in this repository.

Contributors to the lineage, in chronological order:

- **Maxime Schoemans** ([@mschoema](https://github.com/mschoema)) — pg_mfserv founding author (initial commit, OGC-API endpoint design).
- **Victor Morabito** ([@MrMaxime1er](https://github.com/MrMaxime1er)) — pg_mfserv main developer (column-discovery, request handling, exception handling, route refactors — March 2024).
- **Sirine Meraoui** ([@sirimeraoui](https://github.com/sirimeraoui)) — current MobilityAPI maintainer (structured resource layout, test infrastructure, OGC conformance, documentation).

See [`AUTHORS.md`](AUTHORS.md) for the complete contributor list.

## License
##Poetry
poetry install



