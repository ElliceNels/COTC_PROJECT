import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword"
)

c = db.cursor()


def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
    c.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")

    # TODO: Create actual DB

    # Save (commit) the changes and close the connection
    db.commit()
    db.close()