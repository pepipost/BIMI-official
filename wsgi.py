import site
import sys

site.addsitedir('/opt/bimi_update/env/lib/python3.6/site-packages')
sys.path.insert(0, '/opt/bimi_update')

from app import application  # for example, should be app

if __name__ == "__main__":
    application.run()
