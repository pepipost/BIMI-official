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
