# BIMI-official
Brand Indicators for Message Identification or BIMI (pronounced: Bih-mee) is an emerging email specification that enables the use of brand-controlled logos within supporting email clients

Current Setup is for development purposes.

## Requirements
  - python >= 3
  - pip dependency manager
  - virtualenv - To create a python virtual environment
  - java - To parse xml file

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

## Edit configuration file

you can find custom configuration file here -> [custom_config.py](https://github.com/pepipost/BIMI-official/blob/master/custom_config.md)

### Run the application
```sh
$ python .\app.py
```

### Helpful links
[https://bimigroup.org/](https://bimigroup.org/)

[https://pepipost.com/tutorials/bimi/](https://pepipost.com/tutorials/bimi/)

