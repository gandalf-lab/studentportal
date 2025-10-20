from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
import bcrypt
import os

app = Flask(__name__)

# Security: Use environment variables
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Database configuration from environment variables
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'student_portal_db')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Routes
@app.route('/')
def home():
    if 'student_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        major = request.form['major']
        enrollment_year = request.form['enrollment_year']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        hashed_password = hash_password(password)
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO students (student_id, first_name, last_name, email, password, major, enrollment_year) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (student_id, first_name, last_name, email, hashed_password, major, enrollment_year)
                )
                connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except Error as e:
                flash('Error: Student ID or Email already exists!', 'error')
            finally:
                connection.close()
        else:
            flash('Database connection error!', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
                student = cursor.fetchone()
                
                if student and check_password(password, student['password']):
                    session['student_id'] = student['id']
                    session['student_name'] = f"{student['first_name']} {student['last_name']}"
                    flash(f'Welcome back, {student["first_name"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid email or password!', 'error')
            except Error as e:
                flash('Login error!', 'error')
            finally:
                connection.close()
        else:
            flash('Database connection error!', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', student_name=session['student_name'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students WHERE id = %s", (session['student_id'],))
            student = cursor.fetchone()
            return render_template('profile.html', student=student)
        except Error as e:
            flash('Error loading profile!', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('dashboard'))

@app.route('/profile/update', methods=['POST'])
def update_profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    major = request.form['major']
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE students SET first_name = %s, last_name = %s, major = %s WHERE id = %s",
                (first_name, last_name, major, session['student_id'])
            )
            connection.commit()
            session['student_name'] = f"{first_name} {last_name}"
            flash('Profile updated successfully!', 'success')
        except Error as e:
            flash('Error updating profile!', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('profile'))

@app.route('/courses')
def courses():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM courses")
            all_courses = cursor.fetchall()
            cursor.execute("SELECT c.* FROM courses c JOIN registrations r ON c.id = r.course_id WHERE r.student_id = %s", (session['student_id'],))
            my_courses = cursor.fetchall()
            return render_template('courses.html', all_courses=all_courses, my_courses=my_courses)
        except Error as e:
            flash('Error loading courses!', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('dashboard'))

@app.route('/register_course/<int:course_id>')
def register_course(course_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM registrations WHERE student_id = %s AND course_id = %s", (session['student_id'], course_id))
            if cursor.fetchone():
                flash('You are already registered for this course!', 'error')
                return redirect(url_for('courses'))
            
            cursor.execute("INSERT INTO registrations (student_id, course_id, semester) VALUES (%s, %s, %s)", (session['student_id'], course_id, 'Fall 2024'))
            cursor.execute("UPDATE courses SET current_enrollment = current_enrollment + 1 WHERE id = %s", (course_id,))
            connection.commit()
            flash('Course registration successful!', 'success')
        except Error as e:
            flash('Registration failed! Course might be full.', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('courses'))

@app.route('/drop_course/<int:course_id>')
def drop_course(course_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM registrations WHERE student_id = %s AND course_id = %s", (session['student_id'], course_id))
            cursor.execute("UPDATE courses SET current_enrollment = current_enrollment - 1 WHERE id = %s", (course_id,))
            connection.commit()
            flash('Course dropped successfully!', 'success')
        except Error as e:
            flash('Error dropping course!', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('courses'))

@app.route('/grades')
def grades():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.course_code, c.course_name, c.credits, g.grade, g.semester, g.academic_year
                FROM grades g JOIN courses c ON g.course_id = c.id 
                WHERE g.student_id = %s ORDER BY g.academic_year DESC, g.semester DESC
            """, (session['student_id'],))
            grades = cursor.fetchall()
            return render_template('grades.html', grades=grades)
        except Error as e:
            flash('Error loading grades!', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('dashboard'))

@app.route('/announcements')
def announcements():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM announcements ORDER BY created_at DESC")
            announcements = cursor.fetchall()
            return render_template('announcements.html', announcements=announcements)
        except Error as e:
            flash('Error loading announcements!', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
