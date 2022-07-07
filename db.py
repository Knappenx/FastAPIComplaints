import databases
import sqlalchemy
from decouple import config

DATABASE_URL = "postgresql://{}:{}@localhost:{}/{}".format(config('DB_USER'), config('DB_PASS'), config('DB_PORT'), config('DB_NAME'))
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()