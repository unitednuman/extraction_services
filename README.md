# extraction_service

This repo contains the backend codebase for extraction_services which runs multiple scrappers

## Deployment Steps
These are simple steps will help you to deploy the project with docker or without dockers if you only want to check APIs
because the scrappers won't run without dockers

### Step 1: Clone the repository
If you haven't cloned the repo, clone it then move to the repo folder.
```shell
git clone https://github.com/faizanalhassan/extraction_service.git
cd src
```
### Step 2: Setup environment
You need to create .env files. in `extraction_service/src/services`
and copy every thing from `example_env.txt` and paste in .env file and provide your 
database credentials.

### Step 3: Run the project
Open a terminal and move to project  `extraction_service\deploy\dev` and run:
```shell
docker-compose build
```
Then
```shell
docker-compose up -d
```
or if you don't want to run in background
```
docker-compose up
```

The goto `http://localhost/swagger` to see if your project is running.
