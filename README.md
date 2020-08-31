# BIMI-official
Brand Indicators for Message Identification or BIMI (pronounced: Bih-mee) is an emerging email specification that enables the use of brand-controlled logos within supporting email clients

Current Setup is for development purposes.

## Requirements
  - python >= 3
  - pip dependency manager
  - virtualenv - To create a python virtual environment

## Installation
### Check Python installation
```sh
$ python --version
```
You check [python installation steps](https://www.python.org/downloads/), in case of issues.

### Check pip installation
```sh
$ pip --version
```
[Install pip](https://pip.pypa.io/en/stable/installing/) in case it isn't installed.

### Clone Bimi project from git repository
```sh
$ git clone https://github.com/Hiteshpandey/BIMI-official.git bimi
$ cd bimi
```

### Install Virtualenv
```sh
$ pip install virtualenv
```

### Create a virtual environment
```sh
$ python -m venv env
```
This should create a folder named env inside your bimi setup folder. This might look something like this path C:/bimi/env.

### Activate virtual environment
```sh
# For linux
$ source ./env/bin/activate

# For windows
.\env\Scripts\activate
```

### Install dependencies
```sh
$ pip install -r requirements.txt
```

### Edit Configuration File
In the root folder there is file name Config.py which helps you setup the initilization of the python app.
Here are those parameters.
```sh

    Base Configurations
    ===================
    APP_HOST="" #Defaults to 127.0.0.1
    APP_PORT="" #Defaults to 5000
    BASE_URL_API="" #Inactive
    DEBUG=True #Set False for production

    Static Files Configuration
    ==========================
    STATIC_FOLDER="./templates/jinjaTemplate/assets" #Folder for static files
    TEMPLATE_FOLDER="./templates/jinjaTemplate" #Folder For html files
    HOME_PAGE="pages/main.html" #Landing Page

    Database Configuration
    ======================
    DB_HOST="localhost"
    DB_NAME="test"
    DB_USERNAME="root"
    DB_PASSWORD=""

    Log Configuration
    =================
    LOG_FILE_PATH="logs/"
    LOG_FILE_NAME="app.log"
    LOGGING_LEVEL="" # Inactive
    LOGGING_TYPE="" # Inactive
```

### Run the application
```sh
$ python .\app.py
```
