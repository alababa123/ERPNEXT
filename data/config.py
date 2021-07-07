from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("IP")  # Тоже str, но для айпи адреса хоста
loc_photo_worker = env.str("loc_photo_worker")
loc_photo_foreman = env.str("loc_photo_foreman")
loc_pass_worker = env.str("loc_pass_worker")
loc_pass_foreman = env.str("loc_pass_foreman")

user = env.str("user")
password = env.str("password")
host = env.str("host")
port = env.int("port")
database = env.str("database")
