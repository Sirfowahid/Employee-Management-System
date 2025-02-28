from app import create_app
from app.database.models import db,Employee
from datetime import datetime

app = create_app()

with app.app_context():
    db.create_all()
    '''
    admin = Employee(
        name='Mehedi',
        email='mehedii2912@gmail.com',
        password='1223',
        position='Owner',
        department='Administrator',
        salary=1200000,
        status='Active',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    #'''
if __name__ == '__main__':
    app.run(debug=True)