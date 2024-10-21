import sqlite3

def create_connection():
    conn = sqlite3.connect('animal_shelter.db')
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Criar as tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            breed TEXT NOT NULL,
            vaccinated BOOLEAN,
            neutered BOOLEAN,
            description TEXT,
            status TEXT DEFAULT 'Disponível'  -- Novo campo com valor padrão 'Disponível'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adopters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            cpf TEXT,
            birth_date TEXT,
            occupation TEXT,
            income REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            cpf TEXT,
            birth_date TEXT,
            availability TEXT,
            skills TEXT,
            experience TEXT,
            motivation TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adoptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adopter_id INTEGER,
            animal_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(adopter_id) REFERENCES adopters(id),
            FOREIGN KEY(animal_id) REFERENCES animals(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_id INTEGER,
            date TEXT,
            amount REAL,
            FOREIGN KEY(volunteer_id) REFERENCES volunteers(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
