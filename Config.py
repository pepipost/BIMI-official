class Config:
    """
    Base Configurations
    """
    APP_HOST="" #Defaults to 127.0.0.1 For Dev instance
    APP_PORT= ""#Numerical value Defaults to 5000 For Dev instance
    BASE_URL_API="" #Inactive
    DEBUG=False #Set False for production. Enables debug mode for python and vue

    """
    Static Files Configuration
    """
    STATIC_FOLDER="./static" #Folder for static assets files sucha as images , css and storage files
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
    LOGGING_LEVEL="" # Inactive
    #LOGGING_TYPE = FILE/DB/ALL
    LOGGING_TYPE="" # Inactive
    
    """
    SVG Configuration
    """
    RNG_SCHEMA_FILE = "svg_schema/svg_12_ps.rnc"
    STORAGE_DIR = STATIC_FOLDER+"/storage/"

    """
    FILE UPLOAD SETTINGS
    """
    ALLOWED_EXTENSIONS = {'svg', 'pem'}
    STORAGE_SVG_DIR = STORAGE_DIR+"svgs/"
    STORAGE_CERT_DIR = STORAGE_DIR+"certificates/"
