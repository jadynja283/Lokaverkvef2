#Jadyn Margrét
from bottle import run, route, template, request, response, redirect, static_file
import datetime, pymysql, os
import bottle
import beaker
from sys import argv
from beaker.middleware import SessionMiddleware


session_opts = {
    'session.type': 'file',
    # 'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)


connection = pymysql.connect(host='tsuts.tskoli.is',
                             user='3009002830',
                             password='maggamusla123',
                             db='3009002830_vef2lokaverkefni')

expire_date = datetime.datetime.now()
expire_date = expire_date + datetime.timedelta(days=90)

conn_cur = connection.cursor()

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./storedfiles')

@route('/')
def index():
    return template("mainpage.tpl")

@route('/login')
def login():
    return template("login.tpl", message=" ")

@route('/login', method="POST")
def login_post():
    conn_cur.execute('SELECT Username, Password FROM Users')
    users = conn_cur.fetchall()

    user_list = []
    for i, x in users:
        user_list.append([i, x])

    signinUser = request.forms.get('username')
    signinPass = request.forms.get('pass')

    global user
    user = signinUser.strip("'")
    signIn = list((signinUser, signinPass))

    for notandanafn, lykilord in user_list:
        if signIn[0] == notandanafn and signIn[1] == lykilord:
            response.set_cookie("name", user, secret="logged-in", expires=expire_date)
            redirect('/todo')
            break
    return template('login.tpl', message="Innskráning hefur ekki staðist")


@route('/signup')
def signup():
    return template("signup.tpl", message=" ")

@route('/signup', method="POST")
def signup_post():
    conn_cur.execute('SELECT * FROM Users')
    users = conn_cur.fetchall()

    user_list = []
    for i, x, z in users:
        user_list.append([i, x])

    signupUser = request.forms.get('username')
    displayUser = request.forms.get('displayname')
    signUpPass = request.forms.get('pass')
    confirmpass = request.forms.get('confirmpass')
    signUp = list((signupUser, signUpPass))

    complete = False
    for notendanafn, lykilord in user_list:
        if signUp[0] != notendanafn and signUpPass == confirmpass:
            complete = True

        if complete == True:
            conn_cur.execute('INSERT INTO Users VALUES(%s, %s, %s)', (signupUser, displayUser, signUpPass))
            connection.commit()
            conn_cur.execute('CREATE TABLE IF NOT EXISTS ' + str(signupUser) +
                             ' (Name VARCHAR(50) NOT NULL, ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT);')
            connection.commit()
            return template('signup.tpl', message="Nýskráning hefur staðist")
        else:
            return template('signup.tpl', message="Nýskráning hefur ekki staðist")

@route('/todo')
def todo():
    if request.get_cookie("name", secret="logged-in"):
        user_database = request.get_cookie("name", user, secret="logged-in")
        all_data = conn_cur.execute('SELECT * FROM ' + user_database)
        everything = conn_cur.fetchall()

        dblist = []
        for i in everything:
            dblist.append(i)

        row_1 = dblist
        return template('todo.tpl', data_1=row_1)
    else:
        redirect('/')

@route('/delete', method="POST")
def deletetodo():
    deleterow = request.forms.get('deltodo')
    conn_cur.execute('DELETE FROM ' + user + ' WHERE ID = %s', deleterow)
    connection.commit()
    redirect('/todo')

@route('/add', method="POST")
def updatetodo():
    chore = request.forms.get('adding')
    conn_cur.execute("INSERT INTO " + user + "(Name) VALUES ('" + chore + "');")
    connection.commit()
    redirect('/todo')

@route('/signout')
def logout():
    response.set_cookie("name", user, secret="logged-in", max_age=0)
    redirect('/')

run(host="0.0.0.0", port=os.environ.get('PORT', 5000), reloader=True, debug=True)
