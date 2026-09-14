import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='root', db='ticket_management', port=3306)
cur = conn.cursor()
cur.execute('SHOW TABLES')
tables = [row[0] for row in cur.fetchall()]

sql_dump = []
sql_dump.append('-- MySQL database dump for ticket_management\n')
sql_dump.append('SET FOREIGN_KEY_CHECKS=0;\n\n')

for table in tables:
    cur.execute(f'SHOW CREATE TABLE `{table}`')
    create_sql = cur.fetchone()[1]
    sql_dump.append(f'DROP TABLE IF EXISTS `{table}`;\n{create_sql};\n\n')
    
    cur.execute(f'SELECT * FROM `{table}`')
    rows = cur.fetchall()
    if rows:
        cur.execute(f'DESCRIBE `{table}`')
        columns = [f'`{col[0]}`' for col in cur.fetchall()]
        cols_str = ', '.join(columns)
        for row in rows:
            values = []
            for val in row:
                if val is None:
                    values.append('NULL')
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                elif isinstance(val, bool):
                    values.append('1' if val else '0')
                else:
                    escaped = str(val).replace('\\', '\\\\').replace("'", "\\'")
                    values.append(f"'{escaped}'")
            val_str = ', '.join(values)
            sql_dump.append(f'INSERT INTO `{table}` ({cols_str}) VALUES ({val_str});\n')
        sql_dump.append('\n')

sql_dump.append('SET FOREIGN_KEY_CHECKS=1;\n')
conn.close()

with open('database_dump.sql', 'w', encoding='utf-8') as f:
    f.writelines(sql_dump)

print('database_dump.sql created successfully!')
