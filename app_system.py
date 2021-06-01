from logging import error
from flask import Flask, session
from flask import render_template, request
from flask import url_for, redirect, send_file
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from werkzeug.utils import secure_filename
import mysql.connector
import os
from random import randint

from __main__ import app
from __main__ import mydb

app.config['UPLOAD_FOLDER'] = 'recommendations'
app.config['MAX_CONTENT_PATH'] = 2000


'''
session[USER] = currently logged in user (UID);
session[ROLE] = current user's role
'''
@app.route('/admissions/', methods=['GET','POST'])
def loginApps():
    try:
        role = session['ROLE']
        if role == 0:
            return redirect(url_for('appPortalApps'))
        elif role in [3,4,6]:
            return redirect(url_for('facultyPortalApps'))
        elif role == 5:
            return redirect(url_for('adminPortalApps'))
        else:
            return redirect(url_for('login'))
    except KeyError:
        return redirect(url_for('login'))

    # login page, allow any user to login
    # to system. Redirect to appropriate portal
    # upon logging in. If a user is already 
    # logged in, redirect
    # try:
    #     role = session['ROLE']
    #     if role == 0:
    #         return redirect(url_for('appPortalApps'))
    #     elif role in [3,4,6]:
    #         return redirect(url_for('facultyPortalApps'))
    #     elif role == 5:
    #         return redirect(url_for('adminPortalApps'))
    # except KeyError:
    #     pass
    
    # if request.method == 'POST':
    #     c = mydb.cursor(dictionary=True)
    #     username = request.form['username']
    #     password = request.form['password']
    #     c.execute('SELECT * FROM users NATURAL JOIN roles WHERE email=%s', (username,))
    #     result = c.fetchone()
    #     c.close()
    #     if result == None:
    #         return render_template('login.html', credsInvalid=True)
    #     # verify password
    #     if(pbkdf2_sha256.verify(password, result['passw'])):
    #         session['USER'] = result['UID']
    #         session['ROLE'] = result['roleID']
    #         if session['ROLE'] == 0:
    #             return redirect(url_for('appPortalApps'))
    #         elif session['ROLE'] == 5:
    #             return redirect(url_for('adminPortalApps'))
    #         elif session['ROLE'] in [3,4,6]:
    #             return redirect(url_for('facultyPortalApps'))
    #     else:
    #         # password didnt match
    #         return render_template('login.html', credsInvalid=True)
        
    # return render_template('applicant_login.html', credsInvalid=False)



@app.route('/admissions/faculty-portal', methods=['GET'])
def facultyPortalApps():
    # faculty portal: shows a list of 
    # pending applications for review
    if not validateRole([3,4,6]):
        return redirect(url_for('login'))
    uid = session['USER']

    c = mydb.cursor(dictionary=True)
    c.execute('SELECT email FROM users WHERE UID=%s', (uid,))
    username = c.fetchone().get('email')
    c.close()
    
    return render_template('faculty_portal.html', username=username, role=session['ROLE'])



@app.route('/admissions/admin-portal', methods=['GET'])
def adminPortalApps():
    if not validateRole([5]):
        return redirect(url_for('login'))
    return render_template('admin_portal.html')



@app.route('/admissions/add-user', methods=['GET','POST'])
def addUserApps():
    if not validateRole([5]):
        return redirect(url_for('login'))

    if request.method == 'POST':
        c = mydb.cursor()
        username = request.form.get('username')
        #check if user already in database
        c.execute('SELECT * FROM users WHERE email=%s', (username,))
        results = c.fetchone()
        if (results != None):
            message = "Email already taken."
            c.close()
            return render_template('add_user_form.html', message=message)
        # ok to register
        username = request.form['username']
        password = pbkdf2_sha256.hash(request.form['password']) # hash password for safe keeping
        role = int(request.form['role'])
        c.execute(
            'INSERT INTO users (UID,email,passw) VALUES (NULL,%s,%s)', (
                username, password
            )   
        )
        c.execute('SELECT UID FROM users WHERE email=%s',(username,))
        uid = c.fetchone()[0]
        c.execute(
            'INSERT INTO roles VALUES (%s,%s)', (
                uid, role
            )   
        )
        c.close()
        mydb.commit()
        return redirect(url_for('adminPortalApps'))
    
    return render_template('add_user_form.html', message=None)



@app.route('/admissions/app-portal', methods=['GET'])
def appPortalApps():
    # applicant portal: allows user
    # to see the status of their app
    if not validateRole([0]):
        return redirect(url_for('login'))
    uid = session['USER']

    c = mydb.cursor(dictionary=True)
    c.execute('SELECT email,fname,lname FROM users WHERE UID=%s', (uid,))
    result = c.fetchone()
    username = result['email']
    fname = result['fname']
    lname = result['lname']

    c.execute('SELECT * FROM applicantInfo WHERE UID=%s', (uid,))
    info = c.fetchone()

    semester = None
    degree = None
    if info != None:
        semester = info['admissionSemester']
        degree = info['degreeSought']
        if (degree == 'MS'):
            degree = "Master's"
        else:
            degree = "PHD"
    

    status = None
    missing = []
    if info != None:
        if not info['transcript']:
            status = 'INCOMPLETE'
            missing.append('Transcipt')
        if not info['recommendations']:
            status = 'INCOMPLETE'
            missing.append('Three Recommendations')
        if info['decision_made']:
            if info['app_accepted']:
                status = 'ACCEPTED!'
                missing = []
            else:
                status = 'REJECTED'
        elif len(missing) == 0:
            status = 'UNDER REVIEW'

    return render_template(
        'applicant_portal.html', 
        username=username, 
        fname=fname,
        lname=lname,
        uid=uid,
        user=info,
        semester=semester,
        degree=degree,
        status=status,
        missing=missing
    )



@app.route('/admissions/application', methods=['GET','POST'])
def applicationApps():
    # application for user to fill out
    if not validateRole([0]):
        return redirect(url_for('login'))
    uid = session['USER']

    if request.method == 'POST':
        c = mydb.cursor()
        application = request.form

        # applicant info
        fname = application['fname']
        lname = application['lname']
        address = application['address']
        ssn = application['SSN']
        phone = application['phone']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        c.execute( 'UPDATE users SET fname=%s, lname=%s, address=%s, SSN=%s, phone=%s WHERE UID=%s',
            (   
                fname,
                lname,
                address,
                ssn,
                phone,
                uid
            )
        )

        # academic info
        degreeSought = application['degree_apply']
        admitSemester = str(application['admission_semester']) + str(application['admission_year'])
        priorWork = application['priorWork']
        interests = application['interest']

        #GRE
        verbal = application['verbal']
        quant = application['quant']

        c.execute( 'INSERT INTO applicantInfo VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (   
                uid, 
                timestamp, 
                0, 0, None, 0, 0, None, 0, 
                degreeSought,
                admitSemester,
                priorWork,
                interests,
                verbal,
                quant,
                None, None,
            )
        )

        # MS degree info
        if 'type_MS' in application:
            dtype = 'MS'
            major = application['MS_major']
            school = application['MS_school']
            gpa = application['MS_GPA']
            yearObtained = application['MS_prior_year']
            c.execute( 'INSERT INTO degreeInfo VALUES (%s,%s,%s,%s,%s,%s)',
                (uid, dtype, major, school, gpa, yearObtained)
            )
        
        # BA degree info
        if 'type_B' in application:
            dtype = 'B'
            major = application['B_major']
            school = application['B_school']
            gpa = application['B_GPA']
            yearObtained = application['B_prior_year']
            c.execute( 'INSERT INTO degreeInfo VALUES (%s,%s,%s,%s,%s,%s)',
                (uid, dtype, major, school, gpa, yearObtained)
            )
        
        c.close()
        mydb.commit()
        return redirect(url_for('appPortalApps'))
    return render_template('application_form.html')



@app.route('/admissions/logout', methods=['GET'])
def logoutApps():
    # logout a currently logged in user
    session.pop('USER', None)
    session.pop('ROLE', None)
    return redirect(url_for('login'))



@app.route('/admissions/register', methods=['GET','POST'])
def applicantRegisterApps():
    # allows an applicant to register an account
    message = None
    if request.method == 'POST':
        c = mydb.cursor()
        username = request.form.get('username')
        #check if user already in database
        c.execute('SELECT * FROM users WHERE email=%s', (username,)  )
        results = c.fetchone()
        if (results != None):
            message = "Email already taken."
            c.close()
            return render_template('applicant_register.html', message=message)
        # ok to register
        username = request.form.get('username')
        password = pbkdf2_sha256.hash(request.form.get('password')) # hash password for safe keeping
        role = 0
        c.execute(
            'INSERT INTO users (UID,email,passw) VALUES (%s,%s,%s)', (
                None, username, password
            )   
        )  
        c.execute('SELECT UID FROM users WHERE email=%s',(username,))
        uid = c.fetchone()[0]
        c.execute(
            'INSERT INTO roles VALUES (%s,%s)', (
                uid, role
            )   
        )
        c.close()
        mydb.commit()
        message = 'Registration successful!'
    return render_template('applicant_register.html', message=message)
  


@app.route('/admissions/active-apps', methods=['GET','POST'])
def viewAppsApps():
    if not validateRole([3,4,5,6]):
        return redirect(url_for('login'))

    c = mydb.cursor(dictionary=True)
    query = 'SELECT * FROM users NATURAL JOIN applicantInfo WHERE decision_made=0'
    
    if request.method == 'POST':
        if 'degree' in request.form.keys():
            if request.form['degree'] == 'masters':
                query += ' AND degreeSought="MS"'
            elif request.form['degree'] == 'phd':
                query += ' AND degreeSought="PHD"'
    
    query += ' ORDER BY submitted'
    c.execute(query)
    apps = c.fetchall()

    query = 'SELECT UID FROM reviewInfo WHERE reviewerUID=%s'
    c.execute(query,(session['USER'],))
    reviews = c.fetchall()
    reviewed = []
    for r in reviews:
        reviewed.append(r['UID'])

    c.close()

    return render_template('active_applications.html', apps=apps, reviewed=reviewed)



@app.route('/admissions/reviewed-apps', methods=['GET','POST'])
def reviewedApps():
    if not validateRole([4,5,6]):
        return redirect(url_for('login'))
    c = mydb.cursor(dictionary=True)
    query = '''SELECT * FROM users 
                NATURAL JOIN applicantInfo 
                WHERE app_reviewed=1 and
                decision_made=0
                ORDER BY submitted
            '''

    c.execute(query)
    apps = c.fetchall()

    c.close()
    
    return render_template('reviewed_applications.html', apps=apps)



@app.route('/admissions/applications/<UID>', methods=['GET','POST'])
def viewApplicationApps(UID):

    if not validateRole([0,3,4,5,6]):
        return redirect(url_for('login'))

    if session['ROLE'] == 0 and str(session['USER']) != UID:
        return redirect(url_for('login'))
    c = mydb.cursor(dictionary=True)

    if request.method == 'POST':

        reviewerUID = session['USER']
        recommendation = int(request.form['decision'])
        letter = request.form['rating']
        comments = request.form['comments']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute( 'INSERT INTO reviewInfo Values (%s,%s,%s,%s,%s,%s)', 
            (UID, reviewerUID, recommendation, letter, comments, timestamp)
        )
        c.execute('UPDATE applicantInfo SET app_reviewed=1 WHERE UID=%s', (UID,))
        c.close()
        mydb.commit()
        return redirect(url_for('viewAppsApps'))

    c.execute('SELECT roleID FROM roles WHERE UID=%s',(UID,))
    app = c.fetchone()
    if (app['roleID'] != 0):
        return redirect(url_for('viewAppsApps'))
    reviewed = False

    c.execute('SELECT * FROM applicantInfo WHERE UID=%s',(UID,))
    applicant = c.fetchone()
    c.execute('SELECT * FROM users WHERE UID=%s',(UID,))
    userInfo = c.fetchone()
    c.execute('SELECT * FROM degreeInfo WHERE UID=%s',(UID,))
    degrees = c.fetchall()
    c.execute('SELECT * FROM recInfo WHERE UID=%s',(UID,))
    recs = c.fetchall()
    c.execute('SELECT * FROM reviewInfo WHERE UID=%s and reviewerUID=%s',(UID,session['USER']))
    if c.fetchone() != None:
        reviewed = True

    c.close()
    return render_template(
        'application_view.html',
        role=session['ROLE'],
        user=userInfo,
        applicant=applicant,
        degrees=degrees,
        recs=recs,
        reviewed=reviewed
    )



@app.route('/admissions/render-decision/<UID>', methods=['GET','POST'])
def renderDecisionApps(UID):

    if not validateRole([4, 6]):
        return redirect(url_for('login'))
    c = mydb.cursor(dictionary=True)

    if request.method == 'POST':
        query = 'UPDATE applicantInfo SET decision_made=1'
        decision = request.form['decision']
        program = request.form['major']
        advisor = request.form['advisor']
        if (decision == 'Admit with Aid' or decision == 'Admit without Aid' or decision == 'Borderline Admit'):
            query += ', app_accepted=1'
            c.execute(' UPDATE applicantInfo SET program=%s, advisor=%s WHERE UID=%s ',
                (program, advisor, UID)
            )
        else:
            query += ', app_accepted=0'
        query += ' WHERE UID=%s'
        c.execute(query, (UID,))

        c.close()
        mydb.commit()
        return redirect(url_for('reviewedApps'))
        

    c.execute('SELECT roleID FROM roles WHERE UID=%s',(UID,))
    user = c.fetchone()
    if (user['roleID'] != 0):
        return redirect(url_for('viewAppsApps'))


    c.execute(
        ''' SELECT * FROM applicantInfo 
            NATURAL JOIN users 
            WHERE UID=%s''', 
            (UID,)
    )
    applicant = c.fetchone()

    c.execute( 
        ''' SELECT * FROM reviewInfo INNER JOIN users
            ON users.UID=reviewInfo.reviewerUID 
            WHERE reviewInfo.UID=%s ''',
            (UID,) 
    )
    reviews = c.fetchall()

    c.execute(
        'SELECT * FROM users NATURAL JOIN roles WHERE roleID=3 OR roleID=6'
    )
    advisors = c.fetchall()

    c.close()

    return render_template(
        'decision_view.html',
        applicant=applicant,
        reviews=reviews,
        advisors=advisors
    )



@app.route('/admissions/accept', methods=['GET'])
def acceptDecisionApps():
    if not validateRole([0]):
        return redirect(url_for('login'))
    uid = session['USER']

    c = mydb.cursor(dictionary=True)
    c.execute(' SELECT * FROM applicantInfo WHERE UID=%s ', (uid,))
    info = c.fetchone()
    if info == None:
        return redirect(url_for('login'))
    if not info['app_accepted']:
        return redirect(url_for('login'))

    if info['degreeSought'] == 'MS':
        program = 'Masters'
    else:
        program = 'PHD'

    c.execute(' INSERT INTO student VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (
            uid,
            info['program'],info['program'],
            program, info['degreeSought'],
            info['admissionSemester'],
            info['interests'],
            info['priorWork'],
            None,
            info['advisor']
        )
    )
    
    c.execute('UPDATE roles SET roleid=1 WHERE UID=%s',(uid,))
    session['ROLE'] = 1
    mydb.commit()
    c.close()
    return redirect(url_for('home'))



@app.route('/admissions/request-recommendation', methods=['GET','POST'])
def requestRecApps():
    if not validateRole([0]):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        c = mydb.cursor(dictionary=True)
        c.execute( 'SELECT fname, lname FROM users WHERE UID=%s', (session['USER'],) )
        name = c.fetchone()
        return render_template(
            'recommendation_email.html', 
            uid=session['USER'],
            fname=name['fname'],
            lname=name['lname'],
            email=request.form['email']
        )

    return render_template('recommendation_request.html')



@app.route('/admissions/recommendations/<filename>', methods=['GET'])
def getRecApps(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'],filename))



@app.route('/admissions/submit-recommendation/<UID>', methods=['GET','POST'])
def submitRecApps(UID):
    
    if request.method == 'POST':
        c = mydb.cursor()
        form = request.form
        fname = form['fname']
        lname = form['lname']
        email = form['email']
        affil = form['affil']
        title = form['title']
        f = request.files['file']
        filename = secure_filename(f.filename)
        ext = os.path.splitext(filename)[1]

        if (ext != '.pdf'):
            return render_template('recommendation_submit.html', badfile=True)

        filename = str(session['USER']) + "_" + lname + "_" + fname + ext
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        c.execute('SELECT * FROM recInfo WHERE UID=%s and email=%s',(UID,email))
        if (c.fetchone() != None):
            return render_template('recommendation_duplicate.html')

        c.execute('INSERT INTO recInfo VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (UID,fname,lname,email,affil,title,timestamp,filename)
        )

        c.execute('SELECT COUNT(content) FROM recInfo WHERE UID=%s',(UID,))
        num_recs = c.fetchone()[0]
        if num_recs >= 3:
            c.execute('UPDATE applicantInfo SET recommendations=1 WHERE UID=%s', (UID,))

        mydb.commit()  
        c.close()
        return render_template('recommendation_thankyou.html')
    return render_template('recommendation_submit.html',uid=UID)



@app.route('/admissions/find-applicant', methods=['GET','POST'])
def findApplicantApps():
    if not validateRole([3, 4, 5, 6]):
        return redirect(url_for('login'))

    if request.method == 'POST':
        c = mydb.cursor(dictionary=True)
        c.execute('SELECT roleID FROM roles WHERE UID=%s', (request.form['searchQ'],))
        role = c.fetchone()
        c.close()
        if role == None:
            return render_template('applicant_search.html', error=True)
        roleID = role['roleID']
        if roleID != 0:
            return render_template('applicant_search.html', error=True)

        return redirect(url_for('viewApplicationApps', UID=request.form['searchQ']))

    return render_template('applicant_search.html')



@app.route('/admissions/update-application/<UID>', methods=['GET','POST'])
def updateAppApps(UID):

    if not validateRole([0, 4]):
        return redirect(url_for('login'))

    if session['ROLE'] == 0 and str(session['USER']) != UID:
        return redirect(url_for('login'))
    message = False
    if request.method == 'POST':
        c = mydb.cursor()
        form = request.form

        #this is scuffed but im pressed for time
        if 'transcript' in form.keys():
            c.execute('UPDATE applicantInfo SET transcript=1 WHERE UID=%s' , (UID,))
            f = request.files['file']
            filename = secure_filename(f.filename)
            ext = os.path.splitext(filename)[1]

            if (ext != '.pdf'):
                return render_template(
                    'application_update.html', 
                    badfile=True, 
                    UID=UID, 
                    role=session['ROLE']
                )
            filename = "transcript_" + UID + ext
            c.execute('UPDATE applicantInfo SET transcript_path=%s WHERE UID=%s' , (filename,UID,))
            f.save(os.path.join("./transcripts",filename))

        if form['address']:
            c.execute('UPDATE users SET address=%s WHERE UID=%s' , (form['address'], UID,))
        if form['phone']:
            c.execute('UPDATE users SET phone=%s WHERE UID=%s' , (form['phone'], UID,))
        if form['address']:
            c.execute('UPDATE users SET address=%s WHERE UID=%s' , (form['address'], UID,))
        if form['verbal']:
            c.execute('UPDATE applicantInfo SET verbal=%s WHERE UID=%s' , (form['verbal'], UID,))
        if form['quant']:
            c.execute('UPDATE applicantInfo SET quant=%s WHERE UID=%s' , (form['quant'], UID,))
        if form['priorWork']:
            c.execute('UPDATE applicantInfo SET priorWork=%s WHERE UID=%s' , (form['priorWork'], UID,))
        if form['interest']:
            c.execute('UPDATE applicantInfo SET interests=%s WHERE UID=%s' , (form['interest'], UID,))
        
        if 'type_MS' in form.keys():
            c.execute('SELECT * FROM degreeInfo WHERE type="MS" AND UID=%s',(UID,))
            deg = c.fetchone()
            if deg != None:
                c.execute('UPDATE degreeInfo SET major=%s, school=%s, GPA=%s, yearObtained=%s WHERE UID=%s AND type="MS"',
                    (form['MS_major'],form['MS_school'],form['MS_GPA'],form['MS_prior_year'], UID,)
                )
            else:
                c.execute( 'INSERT INTO degreeInfo VALUES (%s,%s,%s,%s,%s,%s)',
                    (UID, "MS", form['MS_major'], form['MS_school'], form['MS_GPA'], form['MS_prior_year'])
                )
        if 'type_BA' in form.keys():
            c.execute('SELECT * FROM degreeInfo WHERE type="B" and UID=%s',(UID,))
            deg = c.fetchone()
            if deg != None:
                c.execute('UPDATE degreeInfo SET major=%s, school=%s, GPA=%s, yearObtained=%s WHERE UID=%s AND type="B"',
                    (form['B_major'],form['B_school'],form['B_GPA'],form['B_prior_year'], UID,)
                )
            else:
                c.execute( 'INSERT INTO degreeInfo VALUES (%s,%s,%s,%s,%s,%s)',
                    (UID, "B", form['B_major'], form['B_school'], form['B_GPA'], form['B_prior_year'])
                )
        
        
        mydb.commit() 
        c.close()
        message = True

    return render_template(
        'application_update.html', 
        message=message, 
        UID=UID, 
        role=session['ROLE']
    )



@app.route('/admissions/transcript/<filename>', methods=['GET'])
def getTranscriptApps(filename):
    return send_file(os.path.join("./transcripts",filename))



@app.route('/admissions/trends', methods=['GET','POST'])
def applicationTrends():
    if not validateRole([3, 4, 5, 6]):
        return redirect(url_for('login'))

    c = mydb.cursor()
    year = None
    c.execute(' SELECT DISTINCT admissionSemester FROM applicantInfo ')
    semesters = c.fetchall()

    if request.method == 'POST':
        year = request.form['year']
        c.execute(' SELECT COUNT(UID) from applicantInfo WHERE admissionSemester=%s', (year,))
        print('YEET')
        num_apps = c.fetchone()[0]
        c.execute(' SELECT AVG(GPA) FROM degreeInfo LEFT JOIN applicantInfo on degreeInfo.UID=applicantInfo.UID WHERE admissionSemester=%s', (year,))
        avg_gpa = c.fetchone()[0]
        c.execute(' SELECT AVG(GPA) FROM degreeInfo LEFT JOIN applicantInfo on degreeInfo.UID=applicantInfo.UID WHERE admissionSemester=%s and degreeSought="MS" ', (year,))
        avg_gpa_m = c.fetchone()[0]
        c.execute(' SELECT AVG(GPA) FROM degreeInfo LEFT JOIN applicantInfo on degreeInfo.UID=applicantInfo.UID WHERE admissionSemester=%s and degreeSought="PHD" ', (year,))
        avg_gpa_p = c.fetchone()[0]
        c.execute(' SELECT AVG(GREverbal) from applicantInfo WHERE admissionSemester=%s', (year,))
        avg_greV = c.fetchone()[0]
        c.execute(' SELECT AVG(GREverbal) from applicantInfo WHERE admissionSemester=%s and degreeSought="MS"', (year,))
        avg_greV_m = c.fetchone()[0]
        c.execute(' SELECT AVG(GREverbal) from applicantInfo WHERE admissionSemester=%s and degreeSought="PHD"', (year,))
        avg_greV_p = c.fetchone()[0]
        c.execute(' SELECT AVG(GREquant) from applicantInfo WHERE admissionSemester=%s', (year,))
        avg_greQ = c.fetchone()[0]
        c.execute(' SELECT AVG(GREquant) from applicantInfo WHERE admissionSemester=%s and degreeSought="MS"', (year,))
        avg_greQ_m = c.fetchone()[0]
        c.execute(' SELECT AVG(GREquant) from applicantInfo WHERE admissionSemester=%s and degreeSought="PHD"', (year,))
        avg_greQ_p = c.fetchone()[0]

        return render_template(
        'applicant_trends.html',
        num_apps=num_apps,
        avg_gpa=avg_gpa,
        avg_gpa_m=avg_gpa_m,
        avg_gpa_p=avg_gpa_p,
        avg_greQ=avg_greQ,
        avg_greQ_m=avg_greQ_m,
        avg_greQ_p=avg_greQ_p,
        avg_greV=avg_greV,
        avg_greV_m=avg_greV_m,
        avg_greV_p=avg_greV_p,
        semesters=semesters,
        year=year
    )

    c.close()
    return render_template(
        'applicant_trends.html',
        semesters=semesters,
        year=year
    )


# encapulates logic to valid role of logged
# in user; if users role doesnt match a role
# in the inputed list of roles, redirect to login
def validateRole(validRoles):
    try:
        role = session['ROLE']
        uid  = session['USER']
        for r in validRoles:
            if r == role:
                return True
        return False
    except KeyError:
        return False



#app.run(host='0.0.0.0', port=8080, debug=True)
