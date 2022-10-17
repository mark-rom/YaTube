## YaTube ##
### Description: ###
YaTube is a social network allowing it's users to make posts, share them in groups, subscribe to other users and comment on their posts. Unauthorized users are allowed to read.

YaTube реализован на view-функциях чистого `Django 2.2.16` и имеет ользовательский интерфейс.

## How to start project: ##

### Clone repo: ###

    git clone https://github.com/mark-rom/YaTube.git

### Go to new dir using command line: ###
    cd YaTube

### Create and activate virtual environment: ###
    python3.9 -m venv env

###### on Mac OS
    source env/bin/activate

###### on Windows
    source venv/Scripts/activate

### Set requirements from requirements.txt: ###
### Update pip:
    python3 -m pip install --upgrade pip

### Set requirements:
    pip install -r requirements.txt
  
### Make migrations: ###
    python3 manage.py migrate

### Start the project: ###
    python3 manage.py runserver
