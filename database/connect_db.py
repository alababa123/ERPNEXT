import mariadb
from data.config import user, password, host, port, database
conn = mariadb.connect(
    user=user,
    password=password,
    host=host,
    port=port,
    database=database
)
cur = conn.cursor()
cur1 = conn.cursor()