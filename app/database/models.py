from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
db = SQLAlchemy()

# Define Employee model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    joining_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    salary = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    # Define relationships
    attendance = db.relationship('Attendance', backref='employee', lazy=True)
    leaves = db.relationship('Leave', backref='employee', lazy=True)
    salary_details = db.relationship('Salary', backref='employee', lazy=True)

    def __repr__(self):
        return f"Employee(id={self.id}, name='{self.name}', position='{self.position}')"

# Define Attendance model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime,default=None)
    working_hour = db.Column(db.Integer,default=None) 
    # Define relationships
    def __repr__(self):
        return f"Attendance(id={self.id}, employee_id={self.employee_id}, entry_time='{self.entry_time}', exit_time='{self.exit_time}')"
        
# Define Leave model
class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    available_leaves = db.Column(db.Integer, nullable=False,default=20)
    status = db.Column(db.String(20),default='Pending')
    # Define relationships
    def __repr__(self):
        return f"Leave(id={self.id}, employee_id={self.employee_id}, leave_type='{self.leave_type}', start_date='{self.start_date}', end_date='{self.end_date}')"

# Define Salary model
class Salary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    bonus = db.Column(db.Float)
    deduction = db.Column(db.Float)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50), nullable=False)
    month = db.Column(db.String(12), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    # Define relationships
    def __repr__(self):
        return f"Salary(id={self.id}, employee_id={self.employee_id}, salary={self.salary}, payment_date='{self.payment_date}')"

# Define General Report model
class GeneralReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(12), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    total_working_hours = db.Column(db.Integer, nullable=False, default=0)
    total_salary = db.Column(db.Float, nullable=False, default=0)
    # Define relationships
    def __repr__(self):
        return f"Report(id={self.id}, month='{self.month}', year='{self.year}', generated_at='{self.generated_at}', employee_id={self.employee_id}, total_working_hours={self.total_working_hours}, total_salary={self.total_salary})"






        