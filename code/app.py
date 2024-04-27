from flask import Flask, render_template, redirect, request, flash, session
from database import User, add_db, open_db, File , Contact

#files upload
from werkzeug.utils import secure_filename
from common.file_utils import *
app = Flask(__name__)
app.secret_key='thisissupersecretkeyfornoone'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("Email=>",email)
        print("Password=>",password)
        if len(email) == 0 and len(password) == 0:
            flash('credentials cannot be empty', 'error')
            return redirect('/login')
        try:
            db = open_db()
            user = db.query(User).filter_by(email=email,password=password).first()
            if user:
                session['isauth'] = True
                session['email'] = user.email
                session['id'] = user.id
                session['username'] = user.username
                db.close()
                flash('login successfull','success')
                return redirect('/') 
            else:
                flash('email or password is wrong','danger')
        except Exception as e:
            flash(f'Error: {e}','danger')    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username') 
        email = request.form.get('email')
        password = request.form.get('password1')
        cpassword = request.form.get('password2')
        print(username,email,password,cpassword)
       
        if len(username)==0 or len(email)==0 or len(password)==0 or len(cpassword)==0:
            flash("All fields are required", 'error')
            return redirect('/register') #reload the page
        try:
            user=User(username=username, email=email, password=password)
            add_db(user)
            flash("Account created", 'success')
            return redirect('/')
        except Exception as e:
            flash(f"Error {e}", 'error')
            return redirect('/register')
    return render_template('register.html')

@app.route('/file/upload', methods=['GET', 'POST'])
def file_upload():
    if not session.get('isauth'):
        return redirect('/login')
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        for file in files:
            if file:
                name = secure_filename(file.filename)
                path = upload_file(file, name)
                file_entry = File(path=path, user_id=1)  # Assuming File model exists with appropriate fields
                add_db(file_entry)  # Save file entry to the database

        flash("Files uploaded successfully", 'success')
    return render_template('upload.html')

@app.route('/file/list', methods=['GET','POST'])
def file_list():
    if not session.get('isauth'):
        return redirect('/login')
    db = open_db()
    files = db.query(File).all()
    return render_template('display_list.html', files=files)

@app.route('/file/<int:id>/view/')
def file_view(id):
    if not session.get('isauth'):
        return redirect('/login')
    db = open_db()
    file = db.query(File).get(id)
    return render_template('view_file.html', file=file)

@app.route('/detect/<int:id>', methods=['GET', 'POST'])
def detect_in_image(id):
    db = open_db()
    file = db.query(File).get(id)
    # make detection
    detections = None
    return render_template(f'/view_file.html', file=file, detections=detections)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def detect_in_image(id):
    return redirect('/file/list')
@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/contact' ,methods=['GET','POST'])
def contact_info():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        phone = request.form['phone']
        # print(name, subject, email, message)
        if len(name) == 0 or len(phone) == 0 or len(email) == 0 or len(message) == 0:
            flash("All fields are required", 'error')
            return redirect('/contact')
        contact = Contact(name=name, phone=phone, email=email, message=message)
        add_db(contact)
        flash("Message sent successfully", 'success')
        return redirect('/contact')

    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 