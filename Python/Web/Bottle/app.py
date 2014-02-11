from bottle import Bottle,route,run,template,get,post,request,static_file,error

app = Bottle()

@app.route('/')
def index():
  return 'Welcome to My Home!!'

@app.route('/index.html')
def homepage():
  return template('index')

@app.route('/hello/<name>')
def greet(name='world'):
  return template('Hello {{name}},how are you?',name=name)

@app.route('/show/<number:int>')
def showNumber(number=0):
  return template('You are visiting page {{number}}',number=number)

@app.get('/login') # or @route('/login')
def login():
    return '''
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''

@app.post('/login') # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    return 'Username=',username

@app.route('/static/<filename>')
def server_static(filename):
  return static_file(filename,root='./static/')

@app.route('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath,root='./static')

@app.error(404)
def error404(error):
  return template('index')

run(app,host='localhost',port='8080',debug=True)
