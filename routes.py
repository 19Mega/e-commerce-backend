from main import app, db

# -----

@app.route('/create_table')
def create_table():
    db.create_all()
    return "Tabla creada!"

@app.route('/insert_user')
def insert_user():
    
    new_user = User(name="Juan")
    db.session.add(new_user)
    db.session.commit()
    return "Usuario insertado!"

@app.route('/delete_table')
def delete_table():
    db.drop_all()
    return "Tabla eliminada!"

# -----

