import sqlite3 

connection=sqlite3.connect('student.db')

cursor=connection.cursor()

table_info=''' CREATE TABLE STUDENT(NAME VARCHAR(25),
 CLASS VARCHAR(25) , SECTION VARCHAR(25), MARKS INT)'''

cursor.execute(table_info)

cursor.execute('''INSERT INTO STUDENT VALUES('AMIT','Data Science','C',94) ''')
cursor.execute('''INSERT INTO STUDENT VALUES('JUHI','Data Analytics','B',88) ''')
cursor.execute('''INSERT INTO STUDENT VALUES('SUNIL','Data Engineering','C',58) ''')
cursor.execute('''INSERT INTO STUDENT VALUES('MAHESH','TECH','A',75) ''')
cursor.execute('''INSERT INTO STUDENT VALUES('DEEPAK','Data Science','D',75) ''')


print('The inserted Records are: ')

data=cursor.execute('''SELECT * FROM STUDENT''')

for row in data:
    print(row)

connection.commit()

connection.close()


