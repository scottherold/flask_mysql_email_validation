from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
import datetime
import re
app = Flask(__name__)
app.secret_key = 'shhhDontTell'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def boot_up():
    return redirect('/users')

@app.route('/users')
def index():
    render_template('index.html')

    

@app.route('/success')
def success():
    mysql = connectToMySQL("emails")
    all_emails = mysql.query_db("SELECT emails.email, DATE_FORMAT(emails.created_at, '%m/%d/%Y %h:%i %p') AS date FROM emails ORDER BY emails.created_at ASC")
    return render_template('success.html', emails=all_emails)

@app.route('/create_user', methods=['POST'])
def validate_user():
    mysql = connectToMySQL("emails")
    duplicate_validation = mysql.query_db("SELECT emails.email FROM emails")
    for email in duplicate_validation:
        if request.form['email'] == email['email']:
            flash(u'Email is already in use!','error')
            return redirect('/')
    if len(request.form['email']) < 1:
        flash(u'Email is required!','error')
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash(u'Invalid email!','error')
        return redirect('/')
    else:
        session['email'] = request.form['email']
        return redirect('/user_validated')

@app.route('/user_validated')
def create_user():
    mysql = connectToMySQL("emails")
    query = "INSERT INTO emails (email, created_at, updated_at) VALUEs (%(email)s, NOW(), NOW());"
    data = {
        'email': session['email']
    }
    new_email_id = mysql.query_db(query, data)
    flash(u'The email address you entered ' + session['email'] + ' is a VALID email address! Thank You!','success')
    return redirect('/success')

@app.route('/delete', methods=['POST'])
def delete_user():
    mysql = connectToMySQL("emails")
    query = "DELETE FROM emails WHERE emails.email=%(email)s;"
    data = {
        'email': request.form['delete_email']
    }
    delete_email_id = mysql.query_db(query, data)
    flash(u'The email address ' + request.form['delete_email'] + ' has been deleted','success')
    return redirect('/success')

if __name__=="__main__":
    app.run(debug=True)