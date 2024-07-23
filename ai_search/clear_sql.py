import sqlite3

conn = sqlite3.connect('/home/data/ssd-1/zy/dooyeed/AI_search.db')
cursor = conn.cursor()

cursor.execute(f"DROP TABLE IF EXISTS searchHistory")

conn.commit()

conn.close()
