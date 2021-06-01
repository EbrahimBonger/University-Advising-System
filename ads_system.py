
from flask import Flask, session
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import MySQLConnection, Error


app = Flask('app')
# app.secret_key = b'mysecretkey'


# from __main__ import app_system


# from __main__ import mydb

app.secret_key = b'mysecretkey'
mydb = mysql.connector.connect(
  host="localhost",
  user="ebrahim5",
  password="seas",
  database="ads"

)

import app_system

course_taken = {}

@app.route('/')
def home():
  # Render the homepage
  if 'USER' in session:
    c = mydb.cursor(dictionary = True)
    c.execute("SELECT fname, lname FROM users WHERE UID = %s", [session['USER']])
    name = c.fetchone()  

    #if user is a new applicant
    if session['ROLE'] == 0:
      return redirect(url_for('appPortalApps'))
    #if user is a new student
    if session['ROLE'] == 1:
      
      
      # check ALumni
      c = None
      c = mydb.cursor(buffered=True, dictionary=True)
      c.execute('select a.UID from alumni a inner join student s on a.UID=s.UID where a.UID=%s', (session['USER'],))
      alumniUID = c.fetchone()
      
      c.close()
      if alumniUID:
        return render_template('regs_alumniIndex.html', name = name, UID = session['USER']) 
      elif academicSuspensionAds(session['USER']):
        probation = True
        print(probation)
      else:
        probation = False 
        print(probation) 
    



      return render_template('regs_index.html', name = name, UID = session['USER'], probation=probation)
    if session['ROLE'] == 2:
      return render_template('regs_alumniIndex.html')
    #if user is a faculty member
    if session['ROLE'] in [3,6]:
      return render_template('regs_facultyIndex.html', name = name, UID = session['USER'])
    #if user is a grad secretary
    if session['ROLE'] == 4:
      return render_template('regs_gsIndex.html', name = name, UID = session['USER'])
    #if user is an admin
    if session['ROLE'] == 5:
      return render_template('regs_adminIndex.html', name = name, UID = session['USER'])

    return render_template('regs_loginError.html', message = "You are not assigned to any role")
  
  #No UID session established, need to sign in
  return render_template("regs_login.html")


@app.route('/login',methods=['GET', 'POST'])
def login():
  #collect form data
  if request.method == 'POST':
    compareEmail = request.form['email']
    comparePassword = request.form['password']

    c = mydb.cursor(dictionary = True, buffered = True)
    print(compareEmail)
    #select email/pass that matches database
    c.execute(' SELECT * FROM users NATURAL JOIN roles WHERE email=%s', ([compareEmail]))
    results = c.fetchone()
    #if there are no results, login fails
    if results is None:
      return render_template('regs_loginError.html', message="Invalid Username or Password.")

    # check hash to password
    # if(pbkdf2_sha256.verify(comparePassword, results['passw'])):
    #   session['USER'] = results['UID']
    #   session['ROLE'] = results['roleID']
    print(results)
    if compareEmail == results['email'] and comparePassword == results['passw']:
      session['USER'] = results['UID']
      session['ROLE'] = results['roleID']
    else:
      return render_template('regs_loginError.html', message="Invalid Username or Password.")
    
    c.close()
    return redirect('/')

  return render_template('regs_login.html')


@app.route('/logout')
def logout():
  session.clear()
  return redirect('/')

@app.route('/ads')
def hello_world():
  
  session.modified = True
  session.clear()
  return render_template('index.html')

@app.route('/faculty-ads')
def facultyadviser():
  session.modified = True
  session['faculty']['form'].clear()
  return render_template('ads_faculty.html')

@app.route('/student', methods = ['GET', 'POST'])
def student():
    
  UID = session['USER']
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  profile = {}
  profile['role'] = 'Student'

 
  # get advisorUID
  c.execute('SELECT advisorUID, program FROM student WHERE UID=%s', (session['USER'],))
  studentInfo = c.fetchall()

   
  advisorUID = studentInfo[0]['advisorUID']
  program = studentInfo[0]['program']
  profile['program'] = program

  # check if user is alumni
  c.execute('select a.UID from alumni a inner join student s on a.UID=s.UID where a.UID=%s', (UID,))
  
  alumniUID = c.fetchone()

  if alumniUID:
    return "he is alumni"

  # student status
  session['student'] = {}
  session['student']['UID'] = session['USER']
  session['student']['advisorUID'] = advisorUID
  session['student']['program'] = program
  session['student']['formOne'] = {}
  session['student']['application_status'] = None
  session['student']['GPA'] = None
  # session['student']['course_taken'] = get_list_of_courses_taken(session["USER"])
  session['student']['GPA'] = calculateGPAads(session["USER"])   
  
  return render_template('student.html', message=profile)


def academicSuspensionAds(UID):
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  
  c.execute('select count(grade) as count from transcript where grade!=%s and grade!=%s and grade!=%s and grade!=%s and grade!=%s and grade!=%sand UID=%s', ('A', 'A-', 'B+', 'B', 'B-','IP', UID,))
  count = c.fetchone()
  count = count['count']
  
  c.close()
  if count >= 3:
    return True
  else:
    return False  

@app.route('/accountInfoAds', methods= ['GET', 'POST'])
def accountInfoAds():
  session.modified = True
  UID = session['USER']

  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('select a.UID, email, fname, lname, school, major, program, a.yearObtained from alumni a inner join student s on a.UID=s.UID inner join users u on u.UID=a.UID where a.UID=%s', (UID,))

  alumniInfo = c.fetchone()



  # get alumin info
  return render_template('ads_accountInfo.html', profile=alumniInfo)

@app.route('/faculty', methods = ['GET', 'POST'])
def faculty():
  profile = {}
  profile['role'] = 'Faculty'
  session['faculty'] = {}
  session['faculty']['UID'] = session['USER']
  session['faculty']['studentUID'] = {}
  session['faculty']['studentInfo'] = {}
  session['faculty']['studentReport'] = {}
  session['faculty']['applications'] = getApplications(session['USER'])
  session['faculty']['form'] = []
                   
  return render_template('ads_faculty.html', message=profile)


@app.route('/graduateSec', methods = ['GET', 'POST'])
def gradSec():
  session.modified = True
  profile = {}
  c = mydb.cursor(buffered=True, dictionary=True)
  session.modified = True
  UID = session['USER']
  c.execute('select fname, lname, email from users where UID=%s', (UID,))
  info = c.fetchone()
  
  profile['fname'] = info['fname']
  profile['lname'] = info['lname']
  profile['email'] = info['email']
  profile['role'] = 'Graduate Secratery'
  session['gs'] = {}
  session['gs']['students'] = {}
  session['gs']['advisors'] = {}
  session['gs']['UID'] = session["USER"]
  return render_template('ads_gs.html', profile=profile)

@app.route('/ads_student_status', methods=['GET', 'POST'])
def ads_student_status():
  return render_template('ads_student_status.html')

@app.route('/ads_student_academic_status', methods=['GET', 'POST'])
def ads_student_academic_status():

  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('select s.UID, u.fname, u.lname, school, major, program, admissionSemester from users u inner join student s on u.UID=s.UID where s.UID not in (select UID from alumni)')

  
  
  studentInfo = c.fetchall()

  student_good_standing = {}
  student_probation = {}
  for student in studentInfo:
    UID = student['UID']
    gpa = calculateGPAads(UID)
    student['gpa'] = gpa
    if not academicSuspensionAds(UID):
      student_good_standing[UID] = student
    


  return render_template('ads_student_academic_status.html', student_good_standing=student_good_standing)


@app.route('/ads_students_in_probation', methods=['GET', 'POST'])
def ads_students_in_probation():

  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('select s.UID, u.fname, u.lname, school, major, program, admissionSemester from users u inner join student s on u.UID=s.UID where s.UID not in (select UID from alumni)')

  
  
  studentInfo = c.fetchall()

  student_good_standing = {}
  student_probation = {}
  for student in studentInfo:
    UID = student['UID']
    gpa = calculateGPAads(UID)
    student['gpa'] = gpa
    if academicSuspensionAds(UID):
      student_probation[UID] = student
    


  return render_template('ads_students_in_probation.html', student_probation=student_probation)



@app.route('/getStudentList', methods=['GET', 'POST'])
def getStudentList():
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  session.modified = True
  status = 'accepted'
  roleID = 1

 

  c.execute('select s.UID, email, phone, fname, lname, major, school, program, degree, admissionSemester, s.advisorUID  from student s  inner join users u  on s.UID = u.UID inner join appList l on l.UID=s.UID inner join roles r on r.UID=s.UID where status=%s and roleID=%s', (status, roleID))
  students = c.fetchall()
  accepted_students = {}
  decision = ['Approved', 'Denied']
  history = {}

  for student in students:
    UID = student['UID']
    GPA = calculateGPAads(UID)
    student['GPA'] = GPA
    
    advisorUID = student['advisorUID']
    c.execute('select fname, lname from users where UID=%s',(advisorUID,))
    advisor = c.fetchone()
    
    advisorFname = advisor['fname']
    advisorLname = advisor['lname'][0] + ""+"."
    student['advisorName'] = advisorLname + " " + advisorFname
    student['decision'] = decision
    
    accepted_students[UID] = student
        
  mydb.commit()
  c.close()
  return render_template('ads_studentList.html', students=accepted_students, history=history)

@app.route('/final_decision', methods=['GET', 'POST'])
def final_decision():
 
  if request.method == 'POST':
    decision = str(request.form['decision'])
    UID = request.form['UID']
    statusApproved = 'Approved'
    statusDenied = 'Denied'
    c = None
    c = mydb.cursor(buffered=True, dictionary=True)

    if decision == 'Approved':
      roleID = 2
      # c.execute('UPDATE roles SET roleID=%s WHERE UID=%s', (roleID, UID))
      c.execute('INSERT INTO alumni  (UID, yearObtained) VALUES (%s, %s)', (UID, 2021))
      c.execute('UPDATE appList SET status=%s WHERE UID=%s', (statusApproved, UID))
      c.execute('DELETE FROM formOne WHERE UID=%s', (UID,))
    elif decision == 'Denied':
      c.execute('UPDATE appList SET status=%s WHERE UID=%s', (statusDenied, UID))
      c.execute('DELETE FROM formOne WHERE UID=%s', (UID,))

    mydb.commit()  
    c.close()  
    return redirect(url_for('getStudentList'))
    

@app.route('/ads_view_transcript/<int:key>', methods=['GET', 'POST'])
def ads_view_transcript(key):
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  session.modified = True
  UID = key
  
  
  c.execute('select sum(cc.credits) as creditsEarned from transcript t inner join courseSchedule cs on t.courseID=cs.courseID inner join courseCatalog cc on cs.catalogID=cc.catalogID where UID=%s', (UID,))

  creditsEarned = c.fetchone()
  creditsEarned= creditsEarned['creditsEarned']

  

  if creditsEarned is None or creditsEarned == 0:
    creditsEarned = 0
    
  
  c.execute('select department, courseNum, title, grade, credits, transSemester, transAcademicYear from courseCatalog cc inner join courseSchedule cs on cc.catalogID=cs.catalogID inner join transcript t on t.courseID=cs.courseID where UID=%s',(UID,))

  history = c.fetchall()

  c.execute('select s.UID, fname, lname, major, program from users u inner join student s on s.UID=u.UID where s.UID=%s', (UID,))
  profile = c.fetchone()

  profile['gpa'] = calculateGPAads(UID)
  profile['creditsEarned'] = creditsEarned

 
  c.close()
  return render_template('ads_view_transcript.html', history=history, profile=profile)  

@app.route('/ads_alumni_info', methods=['GET', 'POST'])
def ads_alumni_info():
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  session.modified = True
  UID = session['USER']
  gpa = {}
  
  
  
  c.execute('select department, courseNum, title, grade, credits, transSemester, transAcademicYear from courseCatalog cc inner join courseSchedule cs on cc.catalogID=cs.catalogID inner join transcript t on t.courseID=cs.courseID where UID=%s',(UID,))

  history = c.fetchall()

  c.execute('select fname, lname from users where UID=%s', (UID,))
  profile = c.fetchone()

  profile['gpa'] = calculateGPAads(UID)

  c.execute('select school, program, major, a.yearObtained from student s inner join alumni a on s.UID=a.UID where a.UID=%s', (UID,))

  degreeInfo = c.fetchone()

  
  c.close()
  return render_template('ads_alumni_info.html', history=history, profile=profile, degreeInfo=degreeInfo)  

@app.route('/alumni_list_ads', methods=['GET', 'POST'])
def alumni_list_ads():
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('select s.UID, u.fname, u.lname, school, major, program, admissionSemester from users u inner join student s on u.UID=s.UID where s.UID in (select UID from alumni)')
  
  alumni_info = c.fetchall()
 
  alumni_list = {}
  for alumni in alumni_info:
    UID = alumni['UID']
    gpa = calculateGPAads(UID)
    alumni['gpa'] = gpa
    alumni_list[UID] = alumni
    


  return render_template('alumni_list_ads.html', alumni_list=alumni_list)
  

# @app.route('/get_application',methods=['GET', 'POST'])
def getApplications(UID):
  
  session.modified = True
  # get pending applications
  applications = {}
  status = "pending"
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('SELECT * FROM appList WHERE advisorUID=%s AND status=%s',(UID, status,))
  applicationLists = c.fetchall()


  # get formOne applications
  if not applicationLists is None:
    
    for app in applicationLists:
      
      UID = app['UID']

      c.execute('select dept, f.courseNum, title, f.credits, f.grade, semester from formOne f inner join courseCatalog cc on cc.courseNum=f.courseNum where f.UID=%s',(UID,))
      forms = c.fetchall()
      
      
      applications[app['UID']] = forms
    
    return applications
  elif applicationLists is None:
    return "No pending application found!"  
  

  mydb.commit()
  c.close()
  return render_template('ads_faculty.html')


def get_student_profile(UID):
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('select * from users where UID=%s',(UID,))
  profile = c.fetchone()

  mydb.commit()
  c.close()
  return profile


@app.route('/academicCommonsAds',methods=['GET', 'POST'])
def academicCommonsAds():

  return render_template('ads_academic_support.html')  


@app.route('/applyToGraduateAds',methods=['GET', 'POST'])
def applyToGraduateAds():
  print("/applyToGraduateAds")
  UID = session['USER']
  print(UID)  
   # check academic suspension
  if academicSuspensionAds(UID):
    message = "You are under academic probation!"
    return render_template('ads_academic_support.html', message=message)
   


  session.modified = True
  course_taken = {}
  session['student'] = {}
  UID = session['USER']
  IP = 'IP'
  session['student']['course_taken'] = {}
  session['student']['formOne'] = {}
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('select department, courseNum, title, credits, grade, semester from courseCatalog ct inner join courseSchedule cr on ct.catalogID=cr.catalogID inner join transcript t on t.courseID=cr.courseID where grade!=%s and UID=%s ORDER BY courseNum', (IP, UID,))   
  
  course_list = c.fetchall()
  
  # store in dictionary form
  count = 0
  for course in course_list:
    count +=1
   
    dept = course['department']
    courseID = course['courseNum']
    key = dept + " " + str(courseID)
    course_taken[key] = course

  
  session['student']['course_taken']  = course_taken

  
  c.close()

  return render_template('ads_formOne.html')    


@app.route('/submit_formOne',methods=['GET', 'POST'])
def submit_formOne():

  # db format: (`UID`, `dept`, `course_id`, `credits`, `grade`, `semester`) VALUES (12345678, 'MATH', 6110, '2', 'A', 'Fall 2020')
  course = request.form['dept']
  session.modified = True
  

  if request.method == 'POST':
    
    if course in session['student']['course_taken']:
     

      get_course = session['student']['course_taken'][course]
      session['student']['formOne'][course] = get_course
      session['student']['course_taken'].pop(course)


    return render_template('ads_formOne.html') 


@app.route('/getApplicantForm',methods=['GET', 'POST'])
def applicant_form():
  


  if request.method == 'POST':

    UID = request.form['UID']


    if str(UID) in session['faculty']['applications']:
      print('found')
    else:
      print('Not found') 
      return redirect(url_for('faculty')) 
    form = {}
    # only one form should be added for auditing
    session['faculty']['form'] = None
    session.modified = True
    
    form = session['faculty']['applications'][UID]
    c = None
    c = mydb.cursor(buffered=True, dictionary=True)
    c.execute('select s.UID, fname, lname, major, program from users u inner join student s on s.UID=u.UID where s.UID=%s',(UID,))
    profile = c.fetchone()



    
  
    c.close()
    return render_template('ads_faculty.html', form = form, profile=profile, UID=UID)


@app.route('/remove_course_from_formOne/<string:key>', methods=['GET', 'POST'])
def remove_course_from_formOne(key):
  session.modified = True
 
  
  if key in session['student']['formOne']:
    session.modified = True
    value = session['student']['formOne'][key]
    session['student']['course_taken'][key] = value
    
    session['student']['formOne'].pop(key)

    return render_template('ads_formOne.html')
  else:
    return "something went wrong..."  


@app.route('/see_more/<int:key>', methods=['GET', 'POST'])
def see_more(key):
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  session.modified = True
  UID = key
  
  c.execute('select s.UID, fname, lname, major, program from users u inner join student s on s.UID=u.UID where s.UID=%s',(UID,))
  profile = c.fetchone()
  
  # get alumni history
  c.execute('select dept, f.courseNum, title, f.credits, f.grade, semester from formOne f inner join courseCatalog cc on cc.courseNum=f.courseNum where f.UID=%s',(UID,))

  form = c.fetchall()
 

  mydb.commit()
  c.close()
  
  return render_template('ads_see_more.html', form=form, profile=profile)

@app.route('/success',methods=['GET', 'POST'])
def success():
  
  insert_c = None
  session.modified = True
  insert_c = mydb.cursor(buffered=True, dictionary=True)
  
  UID = session['USER']
  insert_c.execute('select advisorUID from student where UID=%s', (UID,))
  advisorUID = insert_c.fetchone()
  advisorUID = advisorUID['advisorUID']
  # advisorUID = session['student']['advisorUID']
  

  session['student']['application_status'] = "pending"
  status = session['student']['application_status']


  # overide the previous form
  insert_c.execute('DELETE FROM formOne WHERE UID=%s', (UID,))
  insert_c.execute('DELETE FROM appList WHERE UID=%s', (UID,))

  for key, value in session['student']['formOne'].items():

    
    dept = session['student']['formOne'][key]['department']
    courseNum = session['student']['formOne'][key]['courseNum']
    credits = session['student']['formOne'][key]['credits']
    grade = session['student']['formOne'][key]['grade']
    semester = session['student']['formOne'][key]['semester']

     
    insert_c.execute('INSERT IGNORE INTO formOne (UID, dept, courseNum, credits, grade, semester) VALUES (%s, %s, %s, %s, %s, %s)', (UID, dept, courseNum, credits, grade, semester))

  insert_c.execute('INSERT IGNORE INTO appList (UID, advisorUID, status) VALUES (%s, %s, %s)', (UID, advisorUID, status))

  mydb.commit()
  insert_c.close()
  return render_template('ads_formOne_submitted.html')
    

@app.route('/formOne/', methods=['GET', 'POST'])
def fill_out_form():
  return render_template('ads_formOne.html')


def getGradePoint(courseLetterGrade):
  if (courseLetterGrade == "A"):
    return 4.0
  elif (courseLetterGrade == "A-"):
    return 3.67
  elif (courseLetterGrade == "B+"):
    return 3.33
  elif (courseLetterGrade == "B"):
    return 3.0
  elif (courseLetterGrade == "B-"):
    return 2.67
  elif (courseLetterGrade == "C+"):
    return 2.33
  elif (courseLetterGrade == "C"):
    return 2.0
  elif (courseLetterGrade == "D"):
    return 1.0
  else:
    return 0.0

def calculateGPAads(UID):
  
  session.modified = True
  GPA = 0
  quality_point = 0
  total_quality_points = 0
  total_credit_hours = 0
  c = None
  # program = 'student'

  c = mydb.cursor(buffered=True, dictionary=True)
  c.execute('select credits, grade from courseCatalog ct inner join courseSchedule cr on ct.catalogID=cr.catalogID inner join transcript t on t.courseID=cr.courseID where UID=%s', (UID,))

  # students = c.fetchall()
  gradeInfo = c.fetchall()
  
  for info in gradeInfo:

  
    grade = getGradePoint(info['grade'])
    credits = info['credits']

    
    quality_point = credits * grade
    total_quality_points += quality_point
    total_credit_hours += credits

  if total_credit_hours > 0:
    GPA = total_quality_points/total_credit_hours
    GPA = Decimal(GPA)
    GPA = round(GPA, 2)
 
  mydb.commit()
  c.close()

  return GPA
  
   

@app.route('/audit/<int:key>', methods=['GET', 'POST'])
def audit(key):


  # if request.method == 'POST':  
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  studentUID = key

  form = session['faculty']['applications'][str(studentUID)]
  # role = session['faculty']['form'][0]['role']

  # get student GPA
  # session['faculty']['studentInfo']['GPA'] = calculateGPAads(studentUID)
  GPA = calculateGPAads(studentUID)

  # get the program specifier
  c.execute('SELECT program FROM student WHERE UID=%s', (studentUID,))
  program = c.fetchone()

  program = program['program']

  # get student name
  c.execute('SELECT fname FROM users WHERE UID=%s', (studentUID,))
  fname = c.fetchone()

  fname = fname['fname']
  session['faculty']['studentInfo']['studentUID'] = studentUID
  session['faculty']['studentInfo']['fname'] = fname
  session['faculty']['studentInfo']['program'] = program
  report = {}
  decision = []
  

  if program == 'Masters':
    
    report = msAuditAds(studentUID, GPA, form)
    

    if session['faculty']['studentReport']['is_redy_to_graduate'] == 'YES':
      decision.append('Accept')
   


    return render_template('ads_report.html', message = report, decision = decision)
  elif program == 'PHD':
    report = phdAuditAds(studentUID, GPA, form) 
    
    if session['faculty']['studentReport']['is_redy_to_graduate'] == 'YES':
      decision.append('Accept')
      
    return render_template('ads_report.html', message = report, decision = decision)
  else:
    
    return 'unkown program'   
 
  return render_template('ads_report.html', message = report, decision = decision)  

# auditing functions for ms
def msAuditAds(UID, GPA, form):
  
  c = None
  c = mydb.cursor(buffered=True, dictionary=True)

  dept ='CSCI'
  course_1 = 6212
  course_2 = 6221
  course_3 = 6461
  c.execute('select dept, courseNum from formOne where dept=%s and UID=%s and (courseNum=%s or courseNum=%s or courseNum=%s)',(dept, UID, course_1, course_2, course_3))

  required_cs = c.fetchall()

  
  reqCount = 0
  session.modified = True
  passGPA = 3.0
  

  session['faculty']['studentReport']['gpa'] = 'unsatisfied'
  session['faculty']['studentReport']['cs_require_courses'] = 'unsatisfied'
  session['faculty']['studentReport']['total_credit_hours'] = 'unsatisfied'
  session['faculty']['studentReport']['total_credit_hours_with_two_none_cs_course'] = 'unsatisfied'
  session['faculty']['studentReport']['grade_count_below_B'] = 'unsatisfied'
  session['faculty']['studentReport']['is_redy_to_graduate'] = 'NO'

  # check gpa requirment
  if GPA >= passGPA:
    session['faculty']['studentReport']['gpa'] = 'satisfied'
    reqCount+=1

  # check required CS course requirment
 
  
  cs_require_coursesList = []
  
  if required_cs:
    
    for l in required_cs:
      cs_require_coursesList.append(l['courseNum'])
  else:
       cs_require_coursesList = None 

  if len(required_cs) is 3:
    session['faculty']['studentReport']['cs_require_courses'] = 'satisfied'
    reqCount+=1
  session['faculty']['studentReport']['cs_require_coursesList'] = cs_require_coursesList  
  
  dept = 'CSCI'
  less_than_two_B = 0
  total_credit_hours = 0
  total_cs_credit_hours = 0
  two_none_cs_credits = [0,0]
  
  for course in form:

    grade = getGradePoint(course['grade'])
    if grade < 2.67:
      less_than_two_B += 1

    credits = course['credits']
    # quality_point = credits * grade
      
    # total_quality_points+= quality_point
    total_credit_hours+= credits

    if not course['dept'] == dept:
      if credits > two_none_cs_credits[0]:
        two_none_cs_credits[0] = credits
      elif credits > two_none_cs_credits[1]:
        two_none_cs_credits[1] = credits
      
    else: 
      total_cs_credit_hours += credits 

    
  
 
  # session['student']['total_credit_hours'] = total_credit_hours
  # check total credit hours
  minimum_course_credit_hours = 30

  c.execute('select sum(f.credits) as total from formOne f inner join courseCatalog cc on f.courseNum=cc.courseNum where UID=%s', (UID,))
  total = c.fetchone()
 
  total_credit_hours = total['total']

  if total_credit_hours >= minimum_course_credit_hours:
    session['faculty']['studentReport']['total_credit_hours'] = 'satisfied'
    reqCount+=1
    

  dept = 'CSCI'
  c.execute('select sum(credits) as total from formOne where dept!=%s and UID=%s order by credits desc limit 2', ('CSCI', UID))
  total = c.fetchone()
 
  non_cs_credit_hours = total['total']
  if non_cs_credit_hours is None:
    non_cs_credit_hours = 0


  c.execute('select sum(credits) as total from formOne where dept=%s and UID=%s', ('CSCI', UID,))
  total = c.fetchone()

  cs_credit_hours = total['total']

  if cs_credit_hours is None:
    cs_credit_hours = 0

  
  total_credit_hours_with_two_none_cs_course = cs_credit_hours + non_cs_credit_hours  
  
  if total_credit_hours_with_two_none_cs_course >= minimum_course_credit_hours:
    
    session['faculty']['studentReport']['total_credit_hours_with_two_none_cs_course'] = 'satisfied'
    reqCount+=1
    
  # session['student']['grade_count_below_B'] = less_than_two_B
  # check grade_count_below_B
  c.execute('select count(grade) as count from formOne where grade!=%s and grade!=%s and grade!=%s and grade!=%s and grade!=%s and UID=%s', ('A', 'A-', 'B+', 'B', 'B-', UID,))
  count = c.fetchone()
  count = count['count']
 
  if count <= 2:
    session['faculty']['studentReport']['grade_count_below_B'] = 'satisfied'
    reqCount+=1
      
  # check the number of requirments satisfied    
  if reqCount == 5:
    session['faculty']['studentReport']['is_redy_to_graduate'] = 'YES'  



  # prepare report
  report = {
    'gpa': {'dec': "GPA", 'req': 3.0, 'meet': GPA, 'comment': session['faculty']['studentReport']['gpa']},

    'csReq': {'dec': "CS req. courses", 'req': "[6212, 6221, 6461]", 'meet': str(session['faculty']['studentReport']['cs_require_coursesList']), 'comment': session['faculty']['studentReport']['cs_require_courses']},

    'total_credit_hours' : {'dec': "Total credit hours", 'req': minimum_course_credit_hours, 'meet': total_credit_hours, 'comment': session['faculty']['studentReport']['total_credit_hours']},

    'total_credit_hours_with_none_cs': {'dec': "Total hrs with none CS course", 'req': minimum_course_credit_hours, 'meet': total_credit_hours_with_two_none_cs_course, 'comment': session['faculty']['studentReport']['total_credit_hours_with_two_none_cs_course']},

    'grade_count_below_B' : {'dec': "Num of B earned", 'req': "max. 2", 'meet': less_than_two_B, 'comment': session['faculty']['studentReport']['grade_count_below_B']}    

  }   
  c.close()
  return report


def phdAuditAds(UID, GPA, form):

  c = None
  c = mydb.cursor(buffered=True, dictionary=True)
  reqCount = 0
  session.modified = True
  passGPA = 3.2

  session['faculty']['studentReport']['gpa'] = 'unsatisfied'
  session['faculty']['studentReport']['least_total_completed_courses'] = 'unsatisfied'
  session['faculty']['studentReport']['least_total_CS_completed_courses'] = 'unsatisfied'
  session['faculty']['studentReport']['grade_count_below_B'] = 'unsatisfied'
  session['faculty']['studentReport']['is_defense_thesis_approved'] = 'unsatisfied'
  session['faculty']['studentReport']['is_redy_to_graduate'] = 'NO'
  
  # check GPA
  if GPA >= passGPA:
    session['faculty']['studentReport']['gpa'] = 'satisfied'
    reqCount+=1
    
  total_quality_points = 0
  least_total_completed_courses = 0
  least_total_CS_completed_courses = 0
  less_than_one_B = 0
  minimum_total_credit_hours = 36
  minimum_total_cs_credit_hours = 30
  dept = 'CSCI'

  for course in form:

    grade = getGradePoint(course['grade'])
    if grade < 2.67:
      less_than_one_B += 1

    credits = course['credits']
    # quality_point = credits * grade

    # total_quality_points+= quality_point
    least_total_completed_courses+= credits

    if course['dept'] == dept:
      
      least_total_CS_completed_courses += credits 

    

  # session['student']['least_total_completed_courses'] = least_total_completed_courses
  # check least_total_completed_courses req.
  c.execute('select sum(credits) as total from formOne where UID=%s', (UID,))
  total = c.fetchone()

  cs_credit_hours = total['total']

  if cs_credit_hours is None:
    cs_credit_hours = 0
  if cs_credit_hours >= minimum_total_credit_hours:
    session['faculty']['studentReport']['least_total_completed_courses'] = 'satisfied'
    reqCount+=1
    
  # session['student']['least_total_CS_completed_courses'] = least_total_CS_completed_courses

  c.execute('select sum(credits) as total from formOne where dept=%s and UID=%s', ('CSCI', UID,))
  total = c.fetchone()

  non_cs_credit_hours = total['total']

  if non_cs_credit_hours is None:
    non_cs_credit_hours = 0
  
  # check least_total_CS_completed_courses req.
  if non_cs_credit_hours >= minimum_total_cs_credit_hours:
    session['faculty']['studentReport']['least_total_CS_completed_courses'] = 'satisfied'
    reqCount+=1
    

  # session['student']['grade_count_below_B'] = less_than_one_B
  # check grade_count_below_B req. 
  c.execute('select count(grade) as count from formOne where grade!=%s and grade!=%s and grade!=%s and grade!=%s and grade!=%s and UID=%s', ('A', 'A-', 'B+', 'B', 'B-', UID,))
  count = c.fetchone()
  count = count['count']
  if less_than_one_B <= 1:  
    session['faculty']['studentReport']['grade_count_below_B'] = 'satisfied'
    reqCount+=1
    

  session['faculty']['studentReport']['is_defense_thesis_approved'] = 'satisfied'
  reqCount+=1
  
  if reqCount == 5:
    session['faculty']['studentReport']['is_redy_to_graduate'] = 'YES'

  # prepare report
  report = {
    'gpa': {'dec': "GPA", 'req': 3.2, 'meet': GPA, 'comment': session['faculty']['studentReport']['gpa']},

    'leastTotCompCourse': {'dec': "Least course completed", 'req': minimum_total_credit_hours, 'meet': least_total_completed_courses, 'comment': session['faculty']['studentReport']['least_total_completed_courses']},

    'leastCsTotCompCourse': {'dec': "Least CS course completed", 'req': minimum_total_cs_credit_hours, 'meet': least_total_CS_completed_courses, 'comment': session['faculty']['studentReport']['least_total_CS_completed_courses']},

    'grade_count_below_B' : {'dec': "Num of B earned", 'req': "max. 1", 'meet': less_than_one_B, 'comment': session['faculty']['studentReport']['grade_count_below_B']},

    'defenseThesis' : {'dec': "Deffense thesis", 'req': 1, 'meet': 1, 'comment': session['faculty']['studentReport']['is_defense_thesis_approved']}    

  }  

  c.close()
  return report


@app.route('/accepted',methods=['GET', 'POST'])  
def decision_accepted():

  update_c = None
  update_c = mydb.cursor(buffered=True, dictionary=True)
  session.modified = True

  decision = 'accepted'
  UID = session['faculty']['studentInfo']['studentUID']
  update_c.execute('UPDATE appList SET status=%s WHERE UID=%s', (decision, UID))

  for key, values in session['faculty']['applications'].items():
 
    if int(key) == int(UID):
      session['faculty']['applications'].pop(key)
    
      break

  # session['faculty']['form'].clear()
  mydb.commit()
  update_c.close()

  return render_template('ads_faculty.html')

@app.route('/rejected',methods=['GET', 'POST'])  
def decision_rejected():

  update_c = None
  update_c = mydb.cursor(buffered=True, dictionary=True)
  session.modified = True

  decision = 'rejected'
  UID = session['faculty']['studentInfo']['studentUID']
  update_c.execute('UPDATE appList SET status=%s WHERE UID=%s', (decision, UID))  
  

  for key, values in session['faculty']['applications'].items():

    if int(key) == int(UID):
      session['faculty']['applications'].pop(key)
      
      break
      
  
  # session['faculty']['form'].clear()

  mydb.commit()
  update_c.close()

  return render_template('ads_faculty.html')


app.run(host = '0.0.0.0', port = 8080, debug = True)