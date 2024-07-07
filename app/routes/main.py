from flask import Blueprint, render_template,redirect,url_for,session,request,flash,jsonify,make_response
from app.database.models import db,Employee,Attendance,Leave,Salary,GeneralReport
from datetime import datetime,date,timedelta
from sqlalchemy import extract,func


main_bp = Blueprint('main_bp',__name__)

######### Attendance  #########

# Admin Panel route
@main_bp.route('/admin/Dashboard')
def admin():
    user_dict = session.get('user_dict')  # Retrieving the data from session
    users = Employee.query.all()  # Getting all the employee list from the employee table
    today_date = date.today()  # Today's date

    # Filtering data for today's attendance
    todays_attendance = Attendance.query.filter(db.func.date(Attendance.entry_time) == today_date).all()

    # Collecting unique employee IDs who have checked in today
    unique_present_employee_ids = set(attendance.employee_id for attendance in todays_attendance if attendance.entry_time)

    # Calculating the total present count
    total_present = len(unique_present_employee_ids)

    return render_template(
        'Admin_Dashboard.html', 
        user=user_dict, 
        todays_attendance=todays_attendance, 
        userslen=len(users), 
        selected_date=today_date, 
        total_present=total_present
    )

@main_bp.route('/admin/Employee_List')
def employeeList():
    user_dict = session.get('user_dict')
    
    employees = Employee.query.all()
    return render_template('Admin_Employee_EmployeeList.html', user=user_dict, employees=employees)

@main_bp.route('/admin/Add_Employee', methods=['GET', 'POST'])
def addEmployee():
    print("Adding Employee")
    if request.method == 'POST':
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        position = request.form['position']
        department = request.form['department']
        joining_date = datetime.utcnow().date()
        salary = request.form['salary']
        status = request.form['status']
        is_admin = request.form['isAdmin'] == '1' 
        
        existing_employee = Employee.query.filter_by(email=email).first()
        if existing_employee:
            flash('Email address already exists. Please use a different email.', 'danger')
            return redirect(url_for('main_bp.addEmployee')) 
            
        new_employee = Employee(
            name=name,
            email=email,
            password=password,
            position=position,
            department=department,
            joining_date=joining_date,
            salary=salary,
            status=status,
            is_admin=is_admin
        )
        
        db.session.add(new_employee)
        
        flash('Employee added successfully', 'success')
        
        db.session.commit()
        
        return redirect(url_for('main_bp.employeeList'))  
    
    user_dict = session.get('user_dict')
    return render_template('Admin_Employee_AddEmployee.html', user=user_dict)

@main_bp.route('/admin/update_employee/<int:id>', methods=['GET', 'POST'])
def updateEmployee(id):
    employee = Employee.query.get_or_404(id)
    user_dict = session.get('user_dict')
    
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.salary = request.form['salary']
        employee.status = request.form['status']
        employee.is_admin = request.form['isAdmin'] == '1'
        db.session.commit()
        return redirect(url_for('main_bp.employeeList', user=user_dict))
    return render_template('Admin_updateEmployee.html', employee=employee, user=user_dict)


@main_bp.route('/admin/delete_employee/<int:id>', methods=['POST'])
def deleteEmployee(id):
    employee = Employee.query.get_or_404(id)
    
    db.session.delete(employee)
    db.session.commit()
    
    return redirect(url_for('main_bp.employeeList'))

@main_bp.route('/admin/Todays_Attendance')
def todaysAttendance():
    user_dict = session.get('user_dict')
    today_date = date.today()
    
    todays_attendance = Attendance.query.filter(db.func.date(Attendance.entry_time) == today_date).all()
    
    return render_template('Admin_Attendance_TodaysAttendance.html', user=user_dict, todays_attendance=todays_attendance,selected_date=today_date)

@main_bp.route('/filter_attendance', methods=['GET'])
def filter_attendance():
    user_dict = session.get('user_dict')
    selected_date_str = request.args.get('date')
    
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        session['selected_date'] = selected_date
    else:
        selected_date = date.today()
        session['selected_date'] = selected_date

    filtered_attendance = Attendance.query.filter(
        db.func.date(Attendance.entry_time) == selected_date).all()

    return render_template('Admin_Attendance_TodaysAttendance.html',
                           user=user_dict,
                           todays_attendance=filtered_attendance,
                           selected_date=selected_date)


@main_bp.route('/admin/Leave_Requests')
def leaveRequest():
    user_dict = session.get('user_dict')
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    leave_requests = Leave.query.filter(
        db.extract('month', Leave.start_date) == datetime.now().month,
        db.extract('year', Leave.start_date) == datetime.now().year
    ).order_by(Leave.id.desc()).all()
    print(f'@@@@@@@@@ {current_month} , {current_year}, {leave_requests}')  

    return render_template('Admin_Leaves_LeaveRequest.html', user=user_dict, leave_requests=leave_requests,selected_month=current_month,selected_year=current_year,current_year=current_year)
@main_bp.route('/admin/filter_leave_requests', methods=['GET'])
def filter_leave_requests():
    user_dict = session.get('user_dict')
    month_year = request.args.get('month_year')

    if month_year:
        # Split the month_year string to get the year and month as integers
        selected_year, selected_month_num = map(int, month_year.split('-'))

        # Dictionary to map month numbers to their corresponding names
        num_to_month = {index: month for index, month in enumerate([
            'January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December'
        ], start=1)}

        selected_month = num_to_month[selected_month_num]

        leave_requests = Leave.query.filter(
            extract('month', Leave.start_date) == selected_month_num,
            extract('year', Leave.start_date) == selected_year
        ).order_by(Leave.id.desc()).all()

        print(f'@@@@ {selected_month} {selected_year} {leave_requests}')
        return render_template('Admin_Leaves_LeaveRequest.html', user=user_dict, leave_requests=leave_requests, selected_month=selected_month, selected_year=selected_year, current_year=datetime.now().year)
    
    # Handle the case when month_year is not provided (optional)
    leave_requests = []
    return render_template('Admin_Leaves_LeaveRequest.html', user=user_dict, leave_requests=leave_requests, selected_month=None, selected_year=None, current_year=datetime.now().year)


@main_bp.route('/admin/Payment_Details')
def paymentDetails():
    user_dict = session.get('user_dict')
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    salary = Salary.query.filter_by(month=current_month, year=current_year).all()
    return render_template('Admin_Payroll_PaymentDetails.html', user=user_dict, salary=salary,selected_month=current_month, selected_year=current_year,current_year=current_year)

@main_bp.route('/admin/Edit_Payment_Details/<int:salary_id>', methods=['GET', 'POST'])
def editPaymentDetails(salary_id):
    user_dict = session.get('user_dict')
    salary = Salary.query.get_or_404(salary_id)

    if request.method == 'POST':
        salary.salary = request.form.get('salary', salary.salary)
        salary.bonus = request.form.get('bonus', salary.bonus)
        salary.deduction = request.form.get('deductions', salary.deduction)
        salary.payment_date = datetime.strptime(request.form.get('paymentDate'), '%Y-%m-%d').date()
        salary.payment_method = request.form.get('paymentType', salary.payment_method)
        
        try:
            db.session.commit()
            flash('Update payment successful', 'success')
        except Exception as e:
            db.session.rollback()
            print(f'Error updating salary record: {str(e)}')
        
        return redirect(url_for('main_bp.paymentDetails'))

    return render_template('Admin_Payroll_EditPaymentDetails.html', user=user_dict, salary=salary)

@main_bp.route('/filter_salary', methods=['GET'])
def filter_salary():
    user_dict = session.get('user_dict')
    month_year = request.args.get('month_year')
    current_year = datetime.now().year

    if not month_year:
        flash('Please select a month and a year.', 'warning')
        return redirect(url_for('main_bp.payment_details'))

    try:
        selected_date = datetime.strptime(month_year, '%Y-%m')
        selected_month = selected_date.strftime('%B')  # Full month name (e.g., January)
        selected_year = selected_date.year
    except ValueError:
        flash('Invalid date format. Please select a valid month and year.', 'warning')
        return redirect(url_for('main_bp.payment_details'))

    filtered_salary = Salary.query.filter_by(month=selected_month, year=selected_year).all()
    
    return render_template(
        'Admin_Payroll_PaymentDetails.html', 
        user=user_dict, 
        salary=filtered_salary, 
        selected_month=selected_month, 
        selected_year=selected_year, 
        current_year=current_year
    )

@main_bp.route('/admin/General_Reports', methods=['GET', 'POST'])
def generalReports():
    user_dict = session.get('user_dict')
    users = Employee.query.all()
    current_year = datetime.now().year
    if request.method == 'POST':
        month = request.form['month']
        year = request.form['year']
        employee_id = request.form['employee']
        
    return render_template('Admin_Reports_GeneralReports.html', user=user_dict, users=users, current_year=current_year)


######### User Panel #########
@main_bp.route('/user/Profile')
def user():
    user_dict = session.get('user_dict')
    user_id = user_dict['id']
    
    user_salary_details = Salary.query.filter_by(employee_id=user_id).first()

    return render_template('User_Profile.html', user=user_dict, salary=user_salary_details)
    
@main_bp.route('/user/Attendance')
def userAttendance():
    user_dict = session.get('user_dict')
    user_attendances = Attendance.query.filter_by(employee_id=user_dict['id']).order_by(Attendance.entry_time.desc()).limit(24).all()
    
    return render_template('User_Attendance.html', user=user_dict, attendances=user_attendances)

@main_bp.route('/user/Leaves')
def userLeaves():
    user_dict = session.get('user_dict')
    user_leaves = Leave.query.filter_by(employee_id=user_dict['id']).order_by(Leave.id.desc()).all()

    return render_template('User_LeaveList.html', user=user_dict, leaves=user_leaves)

# Route
@main_bp.route('/leave_request', methods=['POST', 'GET'])
def leave_request():
    user_dict = session.get('user_dict')
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        reason = request.form.get('reason')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        # Check if start_date_str or end_date_str is None (empty form field)
        if start_date_str is None or end_date_str is None:
            flash('Please fill out all fields!', 'error')
            return redirect(url_for('main_bp.leave_request'))
        
        

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date > end_date:
                flash('Cannot take leave backward!','success')
                return redirect(url_for('main_bp.leave_request'))
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('main_bp.leave_request'))

        leave = Leave(
            employee_id=user_dict['id'],
            leave_type=leave_type,
            reason=reason,
            start_date=start_date,
            end_date=end_date,
            available_leaves=20
        )

        db.session.add(leave)
        db.session.commit()

        flash('Leave request submitted successfully!', 'success')
        return redirect(url_for('main_bp.userLeaves'))
    return render_template('User_LeaveRequest.html', user=user_dict)



@main_bp.route('/admin/leave_request/approve', methods=['POST'])
def approve_leave_request():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        leave_request = Leave.query.filter_by(employee_id=user_id, status='Pending').first()
        if leave_request:
            start_date = leave_request.start_date
            end_date = leave_request.end_date
            leave_days = (end_date - start_date).days + 1
            leave_request.available_leaves -= leave_days
            if leave_request.available_leaves <= 0:
                flash('Leave is not available','warning')
                return redirect(url_for('main_bp.leaveRequest'))
            leave_request.status = 'Approved'
            db.session.commit()
            flash('Leave request approved successfully!', 'success')
        else:
            flash('No pending leave request found for the selected user!', 'error')
        return redirect(url_for('main_bp.leaveRequest'))

@main_bp.route('/admin/leave_request/reject', methods=['POST'])
def reject_leave_request():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        leave_request = Leave.query.filter_by(employee_id=user_id, status='Pending').first()
        if leave_request:
            leave_request.status = 'Rejected'
            db.session.commit()
            flash('Leave request rejected successfully!', 'success')
        else:
            flash('No pending leave request found for the selected user!', 'error')
        return redirect(url_for('main_bp.leaveRequest'))



@main_bp.route('/user/Monthly_Reports')
def userMonthlyReports():
    user_dict = session.get('user_dict')
    return render_template('User_MonthlyReports.html',user=user_dict)

@main_bp.route('/user/Salary')
def userSalary():
    user_dict = session.get('user_dict')
    user_salary = Salary.query.filter_by(employee_id=user_dict['id']).order_by(Salary.month.desc()).all()
    return render_template('User_Salary.html',user=user_dict,user_salary=user_salary)

@main_bp.route('/admin/paid',methods=['POST'])
def makePayment():
    if request.method == 'POST':
        sal_id = request.form.get('sal_id')
        salary = Salary.query.get(sal_id)
        if salary.payment_method == 'Paid':
            flash('Payment already completed!','success')
            return redirect(url_for('main_bp.paymentDetails'))
        salary.payment_method = 'Paid'
        salary.payment_date = datetime.now()
        db.session.commit()
        flash('Payment Successful!','success')
        return redirect(url_for('main_bp.paymentDetails'))



######## Attendance ##################
@main_bp.route('/give_attendance', methods=['POST'])
def give_attendance():
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        print(f'user id is: {user_id}')
        user = Employee.query.get(user_id)
        if user.is_admin:
            dest_route = 'main_bp.admin'
        else:
            dest_route = 'main_bp.user'

        last_attendance = Attendance.query.filter_by(employee_id=user_id).order_by(Attendance.entry_time.desc()).first()
        print(f'last attendance: {last_attendance}')
        if last_attendance and last_attendance.entry_time and last_attendance.exit_time:
            entry_time = datetime.utcnow()
            attendance = Attendance(employee_id=user_id, entry_time=entry_time)
            db.session.add(attendance)
            db.session.commit()
            flash('Check In successfully!', 'success')
        else:
            if last_attendance and (not last_attendance.entry_time or not last_attendance.exit_time):
                flash('You have already checked in.', 'warning')
            else:
                entry_time = datetime.utcnow()
                attendance = Attendance(employee_id=user_id, entry_time=entry_time)
                db.session.add(attendance)
                db.session.commit()
                flash('Check In successfully!', 'success')
                
        return redirect(url_for(dest_route))

@main_bp.route('/user/change_password',methods=['GET', 'POST'])
def change_password():
    user_dict = session.get('user_dict')
    if request.method == 'POST':
        old_pass = request.form['current_password']
        new_pass = request.form['new_password']
        conf_pass = request.form['confirm_new_password']
        user = Employee.query.get(user_dict['id'])
        if user.password != old_pass:
            flash('Current password is incorrect','warning')
            return render_template('ChangePassword.html',user=user_dict)
        if new_pass!= conf_pass:
            flash('New password and confirm password do not match','warning')
            return render_template('ChangePassword.html',user=user_dict)
        else:
            user.password = new_pass
            db.session.commit()
            flash('Password changed successfully!','success')
            return redirect(url_for('main_bp.user',user=user_dict))
    return render_template('ChangePassword.html',user=user_dict)


@main_bp.route('/admin/change_password',methods=['GET', 'POST'])
def change_password_admin():
    user_dict = session.get('user_dict')
    if request.method == 'POST':
        old_pass = request.form['current_password']
        new_pass = request.form['new_password']
        conf_pass = request.form['confirm_new_password']
        user = Employee.query.get(user_dict['id'])
        if user.password != old_pass:
            flash('Current password is incorrect','warning')
            return render_template('ChangePassword.html',user=user_dict)
        if new_pass!= conf_pass:
            flash('New password and confirm password do not match','warning')
            return render_template('ChangePassword.html',user=user_dict)
        else:
            user.password = new_pass
            db.session.commit()
            flash('Password changed successfully!','success')
            return redirect(url_for('main_bp.user',user=user_dict))
    return render_template('ChangePasswordAdmin.html',user=user_dict)

@main_bp.route('/check_out', methods=['POST'])
def check_out():
    if request.method == 'POST':
        overtime_earning = 0
        user_id = request.form.get('user_id')
        user = Employee.query.get(user_id)
        if user.is_admin:
            dest_route = 'main_bp.admin'
        else:
            dest_route = 'main_bp.user'

        exit_time = datetime.utcnow()
        latest_attendance = Attendance.query.filter_by(employee_id=user_id).order_by(Attendance.entry_time.desc()).first()
        if latest_attendance and latest_attendance.exit_time:
            flash('You have already checked out.', 'warning')
        else:
            if latest_attendance:
                entry_time = latest_attendance.entry_time
                working_hour_seconds = (exit_time - entry_time).total_seconds()
                latest_attendance.exit_time = exit_time
                if working_hour_seconds < 4 * 3600:  
                    flash('Warning: Working hours are not complete. Cannot check out.', 'warning')
                    return redirect(url_for(dest_route))
                elif working_hour_seconds > 16 * 3600:
                    working_hour_seconds = 8 * 3600  
                    latest_attendance.working_hour = working_hour_seconds
                    db.session.commit()
                    flash('Check Out In Late! Working hour capped at 8 hours.', 'success')
                else:
                    latest_attendance.working_hour = working_hour_seconds
                    db.session.commit()
                    flash('Check Out successfully!', 'success')

                basic_salary_per_hour = user.salary / (24 * 8)
                salary_earned_today = 0

                working_hour = working_hour_seconds / (60 * 60)

                if working_hour > 8:
                    salary_earned_today += 8 * basic_salary_per_hour 
                    extra_hours = working_hour - 8
                    if extra_hours > 8:
                        extra_hours = 8
                    extra_salary_per_hour = 1.5 * basic_salary_per_hour
                    overtime_earning = extra_hours * extra_salary_per_hour
                else:
                    salary_earned_today = working_hour * basic_salary_per_hour

                current_month = datetime.utcnow().strftime('%B')
                current_year = datetime.utcnow().year

                existing_salary = Salary.query.filter(
                                        Salary.employee_id == user_id,
                                        Salary.month == current_month,
                                        Salary.year == current_year
                                    ).order_by(Salary.year.desc(), Salary.month.desc()).first()

                if existing_salary:
                    existing_salary.salary += salary_earned_today
                    existing_salary.bonus += overtime_earning
                    existing_salary.payment_type = 'Not Paid'
                    db.session.commit()
                    flash(f'Today\'s earnings added to the existing salary for {current_month}.', 'info')
                else:
                    salary_entry = Salary(
                        employee_id=user_id,
                        salary=salary_earned_today,
                        bonus=salary_earned_today * 0.08,
                        deduction=0,
                        payment_date=date.today(),
                        payment_method='Not Paid',
                        month=current_month,
                        year=current_year
                    )
                    db.session.add(salary_entry)
                    db.session.commit()
                    flash(f'New salary record created for {current_month}.', 'info')

                if current_year != latest_attendance.entry_time.year:
                    Leave.query.update({'available_leaves': 20})
                    flash('Happy New Year! Available leave value updated to 20.', 'success')
            
        return redirect(url_for(dest_route))


################ Report ##################
@main_bp.route('/admin/submit_report', methods=['POST'])
def admin_submit_report():
    if request.method == 'POST':
        employee_id = request.form['employee']
        month = request.form['month']
        year = request.form['year']

        month_number = datetime.strptime(month, '%B').month

        attendances = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            extract('month', Attendance.entry_time) == month_number,
            extract('year', Attendance.entry_time) == year
        ).all()

        salary = Salary.query.filter_by(
            employee_id=employee_id,
            month=month,
            year=year
        ).first()

        user = Employee.query.get(employee_id)

        return render_template('MonthlyReport.html', employee=user, attendances=attendances, salary=salary, report_month=month, report_year=year, generated_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    return "Invalid request method."

@main_bp.route('/admin/attendanceReport', methods=['POST'])
def attendanceReport():
    if request.method == 'POST':
        selected_date_str = request.form["date"]
        year, month, day = map(int, selected_date_str.split('-'))
        selected_date = datetime(year, month, day).date()
        next_day = selected_date + timedelta(days=1)
        
        filtered_attendance = Attendance.query.filter(Attendance.entry_time >= selected_date, Attendance.entry_time < next_day).all()

        enumerated_attendance = [(idx + 1, attendance) for idx, attendance in enumerate(filtered_attendance)]

        return render_template('Admin_Attendance_Report.html',
                               todays_attendance=enumerated_attendance,
                               selected_date=selected_date)

@main_bp.route('/admin/leaveRequestReport',methods=['POST'])
def leaveRequestReport():
    if request.method == 'POST':
        month = request.form['month']
        year = request.form['year']
        month_to_num = {month: index for index, month in enumerate([
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
        ], start=1)}
        selected_month_num = month_to_num[month]
        selected_year = int(year)
        leave_requests = Leave.query.filter(
        db.extract('month', Leave.start_date) == selected_month_num,
        db.extract('year', Leave.start_date) == selected_year
        ).all()
    
        return render_template('leaveRequestReport.html',leave_requests=leave_requests,selected_month=month,selected_year=year)
        
@main_bp.route('/paymentReport',methods=['POST'])
def paymentReport():
    if request.method == 'POST':
        sal_id = request.form.get('sal_id')
        salary = Salary.query.get(sal_id)
        return render_template('PaymentReport.html',salary=salary)