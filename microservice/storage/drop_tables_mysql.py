import mysql.connector
db_conn = mysql.connector.connect(host="lab6kafka.canadacentral.cloudapp.azure.com", user="user",
password="", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE aircraft_location, aircraft_time_until_arrival''')
db_conn.commit()
db_conn.close()
