# Process_Mining_Version_2
Process mining tool for thesis. Version 2

# Installation
- Create a venv with the requirements.txt
  - pip install -r requirements.txt
  - sudo apt-get install -y graphviz
- Create postgres container with
   sudo docker run --name pmt_postgres -p 5432:5432 -e POSTGRES_PASSWORD=your password -d postgres



Details of database:
- 'NAME': 'postgres',
- 'USER': 'postgres', 
- 'PASSWORD': 'pmt12345678', 
- 'HOST': 'localhost', 
- 'PORT': '5432',

# Install pm4py:

There is a docker image so we will use it to enable pm4py

Pull docker image:
- docker pull pm4py/pm4py-core:latest

Run pm4py docker image:
- docker run --name pmt_pm4py -d -it pm4py/pm4py-core:latest bash

# To start the containers
- sudo docker start pmt_postgres
- sudo docker start pmt_pm4py