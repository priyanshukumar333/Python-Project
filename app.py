from flask import Flask,render_template,session,request,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import os , bcrypt


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db=SQLAlchemy(app)
app.secret_key='secret_key'

class User(db.Model):
    id=db.Column(db.Integer , primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
    address=db.Column(db.String(100),nullable=False)

    def __init__(self,name,email,password,address):
        self.name=name
        self.email=email
        self.password=bcrypt.hashpw(password.encode('utf-8') , bcrypt.gensalt()).decode('utf-8')
        self.address=address
    def check_password(self,password): 
        return bcrypt.checkpw(password.encode('utf-8') , self.password.encode('utf-8'))
  
with app.app_context():
    if not os.path.exists('users.db'):
        db.create_all()
     
@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
        address=request.form.get('address')
        user=User(name=name,email=email,password=password,address=address)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')  

@app.route("/login" , methods=['GET','POST'])
def login(): 
  if request.method == 'POST':
      email=request.form.get('email') 
      password=request.form.get('password')
      user=User.query.filter_by(email=email).first()

      if user and user.check_password(password):
          session['email'] = user.email
          return redirect('/dashboard')
      else:
          return render_template('login.html' ,error='Invalid user')  
  return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    if session['email']:
        user=User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html',user=user)
    return redirect('/login.html') 
     
@app.route("/logout")
def logout():
    session.pop('email' , None)
    return redirect('/login') 
          

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
       name=request.form.get('name')
       email=request.form.get('email')
       password=request.form.get('password')
       address=request.form.get('address')

    try:
        exist= User.query.filter_by(email=email).first()
        if exist:
            print("this user email present")
        else:
            new_user=User(name=name,email=email,password=password,address=address)
            db.session.add(new_user)
            db.session.commit()
    except Exception as e:
      print(f"error using user{e}")
    U=User.query.all()      
    return render_template('index.html', users=U)

@app.route('/update/<int:id>',methods=['GET','POST'])
def update_user(id):
    user=User.query.get_or_404(id)
    if request.method == 'POST':
       user.name = request.form.get('name')
       user.email=request.form.get('email')

       try:
              db.session.commit()
              return redirect('/')
       except Exception as e:
             db.session.rollback()
       return f"Error updating user:{e}"
    return render_template ('update.html',user=user)

@app.route('/delete/<int:id>',methods=['GET','POST'])
def delete_user(id):
    user=User.query.get_or_404(id)
    if request.method == 'POST':
       user.name = request.form.get('name')
       user.email=request.form.get('email')

       try:
              db.session.delete(user)
              db.session.commit()
       except Exception as e:
             db.session.rollback()
             return f"Error updating user:{e}"
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)