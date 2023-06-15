Backend Coding Challenge

# Deployment
1. Docker (docker build -t api . && docker container run api)
2. Locally run:
  - python3 -m venv env (python3.10 used)
  - source env/bin/activate
  - pip install -r requirements.txt
  - python dbsetup.py -m up
  - uvicorn main:app --reload
# Tests
Run __pytest__ in the root directory of this project
# Logs
Logs are stored in logs folder and if the folder doesn't exist its created
