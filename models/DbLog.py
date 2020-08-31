from Config import Config
import mysql.connector
from mysql.connector import errorcode
from utils.Log import logger

class DbLog():
    def __init__(self):
        """ self.host = Config.DB_HOST
        self.db = Config.DB_NAME
        self.username = Config.DB_USERNAME
        self.password = Config.DB_PASSWORD """
        self.config = {
                    'user': Config.DB_USERNAME,
                    'password': Config.DB_PASSWORD,
                    'host': Config.DB_HOST,
                    'database': Config.DB_NAME,
                    'raise_on_warnings': True
                    }

    def connect(self):
        try:
            cnx = mysql.connector.connect(**self.config)
            logger.info("Connecting to MYSQL Database %s Using Host: %s,Username: %s, Password: %s ", self.config['database'],self.config['host'],self.config['user'],self.config['password'])       
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                logger.info("Something is wrong with your user name or password")
                cnx = mysql.connector.connect(**self.config)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                logger.info("Database does not exist")
            else:
                print(err)
                logger.info(err)
        else:
            return cnx
    
    def createLog(self):
        conn = self.connect()
        cursor = conn.cursor()
        query = ("SELECT * FROM pushed")
        cursor.execute(query)
        for (data) in cursor:
            print("data is %d",format(data))
            response = data[0]
        cursor.close()
        conn.close()
        return response
