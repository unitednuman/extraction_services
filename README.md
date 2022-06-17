# extraction_service

This codebase is consists REST API to provide properties and background worker which scrape properties from auction sites 

## Deployment Steps
These are simple steps will help you to deploy the project with docker

### Step 1: Clone the repository
If you haven't cloned the repo, clone it and then move to the repo folder.

### Step 2: Setup environment
You need to create .env files. inside `extraction_service/deploy`
and copy all the variables from `example_env.txt` and paste in .env file, then set your values for all the variables.

### Step 3: Run the project
Open a terminal and move to project  `extraction_service\deploy\` and run:
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

