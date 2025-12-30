import sqlite3

conn = sqlite3.connect('indoor_nav.db')
cursor = conn.cursor()

# Check existing tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Add floor_plan_image column if floors table exists
if ('floors',) in tables:
    try:
        cursor.execute('ALTER TABLE floors ADD COLUMN floor_plan_image TEXT')
        conn.commit()
        print('Column floor_plan_image added to floors table')
    except sqlite3.OperationalError as e:
        print(f'Column may already exist: {e}')
else:
    print('floors table does not exist')

conn.close()
