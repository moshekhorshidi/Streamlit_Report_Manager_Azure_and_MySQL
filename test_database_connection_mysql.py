import mysql.connector

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="your_host_cards_local_or_server",
    user="your_user_name",
    password="your_password",
    database="sakila"
)