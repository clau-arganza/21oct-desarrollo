'''
- Help: --help
- First time: create new db --createndb 1 / --createndb True
- Next: to show all usersdata in users --showusers 1 / --showusers True
'''

import sqlite3, argparse

#conectar
#conexion = sqlite3.connect("db_user.db")
def connectdb(dbfile):
    return sqlite3.connect(dbfile)

users_dbfile = "db_user.db"
connexion = connectdb(users_dbfile)

#rellenar con usuarios por defecto - Esto se usaría para root y admins de inicio
def prefillusers():
    connexion.execute("insert into users(nickname,birthday,passw,blocked) values (?,?,?,?)", ("pepeuser", "2020-11-15", "pepepassw", 0))
    connexion.execute("insert into users(nickname,birthday,passw,blocked) values (?,?,?,?)", ("sarauser", "2000-11-15", "sarapassw", 0))
    connexion.execute("insert into users(nickname,birthday,passw,blocked) values (?,?,?,?)", ("mariouser", "2010-11-15", "mariopassw", 0))
    connexion.execute("insert into users(nickname,birthday,passw,blocked) values (?,?,?,?)", ("lolauser", "2005-11-15", "lolapassw", 0))
    connexion.execute("insert into users(nickname,birthday,passw,blocked) values (?,?,?,?)", ("jorgeuser", "2000-11-15", "jorgepassw", 1))
    connexion.execute("insert into users(nickname,birthday,passw,blocked) values (?,?,?,?)", ("alejauser", "2015-11-15", "alejopassw", 1))
    connexion.commit()

def createdb():
    #crear la tabla usuarios sino existe
    #En la primera ejecución crea el archivo .db
    try:
        connexion.execute("""create table users (
                                codigo integer primary key autoincrement,
                                nickname text,
                                birthday text,
                                passw text,
                                blocked int(1)
                            )""")
        print("users table created")
        prefillusers()                  
    except sqlite3.OperationalError:
        print("users table already exists")            

    #cerrar conexión
    connexion.close()

#query to find one user
def find_user(nickname, passw):

    result = None
    #connexion = connectdb(users_dbfile)

    cursor = connexion.execute("select nickname, birthday, blocked from users where nickname=? and passw=?" , (nickname, passw))
    row = cursor.fetchone()

    if row != None:
        result = row

    connexion.close()

    return result

def all_users():
    result = None
    #connexion = connectdb(users_dbfile)

    cursor = connexion.execute("select * from users")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
#show users data
#all_users()

#Args - control execution from terminal
fileparser = argparse.ArgumentParser()
fileparser.add_argument("--createndb", help="Initial execution")
fileparser.add_argument("--showusers", help="Show all users in db")
fileargs = fileparser.parse_args()
#print(fileargs)
if fileargs.createndb:
    createdb()
elif fileargs.showusers:
    all_users()





