from flask import Flask, request, session, redirect, url_for, render_template
import smtplib
from email.message import EmailMessage
from flaskext.mysql import MySQL
import pymysql 
import re 

app = Flask(__name__)
app.secret_key = '89fd465fda7d8a64as5d4as'
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'qwertyashwath'
app.config['MYSQL_DATABASE_DB'] = 'testdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   return redirect(url_for('home'))

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        time = request.form['time']
        cursor.execute('UPDATE bookings SET appt_time = %s WHERE booking_id = %s', (time,booking_id))
        cursor.execute('SELECT * FROM bookings WHERE booking_id = %s', (booking_id))
        account = cursor.fetchone()
        patient = account['patient_name']
        patient_email = account['patient_email']
        date = account['appt_date']
        conn.commit()
        
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login('maduraihospitals@gmail.com', 'gjimdjyuhtaiypgb')

        msg = EmailMessage()
        msg.set_content(f'Hello {patient}!\n\nYour appointment has been fixed by the hospital on {date} at {time}. To book further appointments, checkout our website:\nhttp://localhost:5000\n\n\nThankyou!')

        msg['Subject'] = 'Appointment Confirmed!'
        msg['From'] = 'maduraihospitals@gmail.com'
        msg['To'] = patient_email

        s.send_message(msg)
        s.quit()

    email = session['email']
    cursor.execute('SELECT * FROM bookings where doctor_email=%s', (email))
    appointments = cursor.fetchall()
    return render_template('appointments.html',appointments=appointments)

@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    msg = ''

    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'cpassword' in request.form and 'email' in request.form:

        name = request.form['name']
        password = request.form['password']
        cpassword = request.form['cpassword']
        email = request.form['email']
        hospital = request.form['hospital']
        add1 = request.form['add1']
        add2 = request.form['add2']
        city = request.form['city']
        pincode = request.form['pincode']
        startday = request.form['startday']
        endday = request.form['endday']
        time1 = request.form['time1']
        time2 = request.form['time2']

        cursor.execute('SELECT * FROM doctor WHERE email = %s', (email))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not password or not cpassword or not email:
            msg = 'Please fill out the form!'
        elif not password==cpassword:
            msg = 'Both the passwords must match with each other!'
        else:
            cursor.execute('INSERT INTO doctor VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, email, password, hospital, time1, time2, startday, endday, add1, add2, city, pincode)) 
            conn.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('doctor_login'))

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
        
    return render_template('doctorRegister.html', msg=msg)

@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    msg = ''

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor.execute('SELECT * FROM doctor WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
   
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']

            return redirect(url_for('home'))
        
        else:
            msg = 'Incorrect username/password!'

    return render_template('doctorLogin.html',msg=msg)

@app.route('/search', methods=['GET', 'POST'])
def search():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        email = request.form['browser']
        cursor.execute('SELECT * FROM doctor WHERE email = %s', (email))
        account = cursor.fetchone()
        if account:
            return render_template('doctorInfo.html', account=account)
        else:
            print('Select one among the following!')

    cursor.execute('SELECT * FROM doctor')
    doctors = cursor.fetchall()
    return render_template('search.html',doctors=doctors)

@app.route('/book', methods=['GET', 'POST'])
def book():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        doctor_email = request.form['doctor']
        patient_email = request.form['email']
        name = request.form['patient']
        age = request.form['age']
        relation = request.form['relation']
        date = request.form['date']
        time = request.form['time']
        cursor.execute('INSERT INTO bookings VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL)', (doctor_email, patient_email, name, age, relation, time, date))
        conn.commit()

        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login('maduraihospitals@gmail.com', 'gjimdjyuhtaiypgb')

        msg = EmailMessage()
        msg.set_content(f'Hello Doctor!\n\nThere is a new appointment requested from {name}, Age: {age}. To confirm the appointment, check with our website:\nhttp://localhost:5000\n\n\nThankyou!')

        msg['Subject'] = 'New Appointment!'
        msg['From'] = 'maduraihospitals@gmail.com'
        msg['To'] = doctor_email

        s.send_message(msg)
        s.quit()

        return render_template('booking.html')
    return redirect(url_for('search'))

if __name__ == '__main__':
    app.run(host="localhost", port=4000, debug=True)