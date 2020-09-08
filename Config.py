class Config():
    """
    Base Configurations
    """
    APP_HOST="" #Defaults to 127.0.0.1
    APP_PORT="" #Defaults to 5000
    BASE_URL_API="" #Beta
    DEBUG=True #Set False for production. Enables debug mode for python and vue

    """
    Static Files Configuration
    """
    STATIC_FOLDER="./templates/jinjaTemplate/assets" #Folder for static assets files sucha as images and css
    TEMPLATE_FOLDER="./templates/jinjaTemplate" #Folder For index.html file
    HOME_PAGE="pages/main.html" #Landing Page

    """
    Database Configuration
    """
    DB_HOST="localhost"
    DB_NAME="test"
    DB_USERNAME="root"
    DB_PASSWORD=""

    """
    Log Configuration
    """
    LOG_FILE_PATH="logs/"
    LOG_FILE_NAME="app.log"
    #LOG_LEVEL = INFO/DEBUG/WARNING
    LOGGING_LEVEL=""
    #LOGGING_TYPE = FILE/DB/ALL
    LOGGING_TYPE=""

    """
    SVG Configuration
    """
    RNG_SCHEMA_FILE = "svg_schema/svg_12_ps.rnc"
    STORAGE_SVG_DIR = "storage/svgs/"