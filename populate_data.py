import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

def create_connection(db_file='animal_shelter.db'):
    """Cria uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(db_file)
    return conn

def generate_unique_cpfs(fake, total_cpfs):
    """
    Gera um conjunto de CPFs únicos usando a biblioteca Faker.
    
    Args:
        fake (Faker): Instância do Faker.
        total_cpfs (int): Número total de CPFs a serem gerados.
        
    Returns:
        set: Conjunto de CPFs únicos.
    """
    cpfs = set()
    while len(cpfs) < total_cpfs:
        cpf = fake.unique.cpf()
        cpfs.add(cpf)
    return cpfs

def generate_persons(conn, fake, total_persons):
    """
    Gera e insere pessoas na tabela 'persons'.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados.
        fake (Faker): Instância do Faker.
        total_persons (int): Número total de pessoas a serem geradas.
        
    Returns:
        list: Lista de IDs das pessoas inseridas.
    """
    cursor = conn.cursor()
    cpfs = generate_unique_cpfs(fake, total_persons)
    person_ids = []
    
    for cpf in cpfs:
        name = fake.name()
        address = fake.address().replace('\n', ', ')
        phone = fake.phone_number()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d")
        is_adopter = random.choice([0, 1])
        is_volunteer = random.choice([0, 1])
        created_at = fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO persons (name, address, phone, cpf, birth_date, isAdopter, isVolunteer, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, phone, cpf, birth_date, is_adopter, is_volunteer, created_at))
        
        person_ids.append(cursor.lastrowid)
    
    conn.commit()
    return person_ids

def generate_adopters(conn, person_ids, fake):
    """
    Gera e insere adotantes na tabela 'adopters' para pessoas marcadas como adotantes.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados.
        person_ids (list): Lista de IDs das pessoas.
        fake (Faker): Instância do Faker.
        
    Returns:
        list: Lista de IDs dos adotantes inseridos.
    """
    cursor = conn.cursor()
    adopter_ids = []
    
    for person_id in person_ids:
        # Verificar se a pessoa é um adotante
        cursor.execute('SELECT isAdopter FROM persons WHERE id = ?', (person_id,))
        is_adopter = cursor.fetchone()[0]
        if is_adopter:
            occupation = fake.job()
            income = round(random.uniform(1500, 15000), 2)
            created_at = fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO adopters (person_id, occupation, income, created_at)
                VALUES (?, ?, ?, ?)
            ''', (person_id, occupation, income, created_at))
            
            adopter_ids.append(cursor.lastrowid)
    
    conn.commit()
    return adopter_ids

def generate_volunteers(conn, person_ids, fake):
    """
    Gera e insere voluntários na tabela 'volunteers' para pessoas marcadas como voluntárias.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados.
        person_ids (list): Lista de IDs das pessoas.
        fake (Faker): Instância do Faker.
        
    Returns:
        list: Lista de IDs dos voluntários inseridos.
    """
    cursor = conn.cursor()
    volunteer_ids = []
    
    for person_id in person_ids:
        # Verificar se a pessoa é um voluntário
        cursor.execute('SELECT isVolunteer FROM persons WHERE id = ?', (person_id,))
        is_volunteer = cursor.fetchone()[0]
        if is_volunteer:
            availability = random.choice(['Manhã', 'Tarde', 'Noite', 'Integral'])
            skills = ", ".join(fake.words(nb=random.randint(1, 5)))
            experience = fake.text(max_nb_chars=100)
            motivation = fake.text(max_nb_chars=200)
            created_at = fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO volunteers (person_id, availability, skills, experience, motivation, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (person_id, availability, skills, experience, motivation, created_at))
            
            volunteer_ids.append(cursor.lastrowid)
    
    conn.commit()
    return volunteer_ids

def generate_animals(conn, fake, total_animals):
    """
    Gera e insere animais na tabela 'animals'.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados.
        fake (Faker): Instância do Faker.
        total_animals (int): Número total de animais a serem gerados.
        
    Returns:
        list: Lista de IDs dos animais inseridos.
    """
    cursor = conn.cursor()
    animal_ids = []
    types = ['Cachorro', 'Gato']
    breeds = {
        'Cachorro': ['Labrador', 'Bulldog', 'Poodle', 'Beagle', 'Pastor Alemão'],
        'Gato': ['Persa', 'Siamês', 'Maine Coon', 'Sphynx', 'Ragdoll']
    }
    
    for _ in range(total_animals):
        name = fake.first_name()
        animal_type = random.choice(types)
        breed = random.choice(breeds[animal_type])
        vaccinated = random.choice([True, False])
        neutered = random.choice([True, False])
        description = fake.text(max_nb_chars=100)
        status = random.choices(['Disponível', 'Adotado'], weights=[0.8, 0.2])[0]
        created_at = fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO animals (name, type, breed, vaccinated, neutered, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, animal_type, breed, vaccinated, neutered, description, status, created_at))
        
        animal_ids.append(cursor.lastrowid)
    
    conn.commit()
    return animal_ids

def generate_adoptions(conn, adopter_ids, animal_ids, fake):
    """
    Gera e insere adoções na tabela 'adoptions' para animais adotados.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados.
        adopter_ids (list): Lista de IDs dos adotantes.
        animal_ids (list): Lista de IDs dos animais.
        fake (Faker): Instância do Faker.
        
    Returns:
        list: Lista de IDs das adoções inseridas.
    """
    cursor = conn.cursor()
    adoption_ids = []
    
    # Selecionar apenas animais com status 'Adotado'
    cursor.execute('SELECT id FROM animals WHERE status = "Adotado"')
    adopted_animal_ids = [row[0] for row in cursor.fetchall()]
    
    for animal_id in adopted_animal_ids:
        adopter_id = random.choice(adopter_ids) if adopter_ids else None
        if adopter_id:
            # Gerar uma data de adoção dentro do período
            adoption_date = fake.date_between(start_date='-2y', end_date='today').strftime("%Y-%m-%d")
            created_at = fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
            status = 'Concluída'  # Pode ajustar conforme necessidade
            
            cursor.execute('''
                INSERT INTO adoptions (adopter_id, animal_id, date, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (adopter_id, animal_id, adoption_date, status, created_at))
            
            adoption_ids.append(cursor.lastrowid)
    
    conn.commit()
    return adoption_ids

def generate_donations(conn, volunteer_ids, fake, max_donations_per_volunteer=5):
    """
    Gera e insere doações na tabela 'donations' para voluntários.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados.
        volunteer_ids (list): Lista de IDs dos voluntários.
        fake (Faker): Instância do Faker.
        max_donations_per_volunteer (int): Número máximo de doações por voluntário.
        
    Returns:
        list: Lista de IDs das doações inseridas.
    """
    cursor = conn.cursor()
    donation_ids = []
    
    for volunteer_id in volunteer_ids:
        # Decidir aleatoriamente quantas doações cada voluntário fará
        num_donations = random.randint(1, max_donations_per_volunteer)
        for _ in range(num_donations):
            donation_date = fake.date_between(start_date='-2y', end_date='today').strftime("%Y-%m-%d")
            amount = round(random.uniform(10, 1000), 2)
            created_at = fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO donations (volunteer_id, date, amount, created_at)
                VALUES (?, ?, ?, ?)
            ''', (volunteer_id, donation_date, amount, created_at))
            
            donation_ids.append(cursor.lastrowid)
    
    conn.commit()
    return donation_ids

def main():
    fake = Faker('pt_BR')
    Faker.seed(0)
    random.seed(0)
    
    conn = create_connection()
    
    total_persons = 500
    total_animals = 300
    
    print("Gerando e inserindo pessoas...")
    person_ids = generate_persons(conn, fake, total_persons)
    
    print("Gerando e inserindo adotantes...")
    adopter_ids = generate_adopters(conn, person_ids, fake)
    
    print("Gerando e inserindo voluntários...")
    volunteer_ids = generate_volunteers(conn, person_ids, fake)
    
    print("Gerando e inserindo animais...")
    animal_ids = generate_animals(conn, fake, total_animals)
    
    print("Gerando e inserindo adoções...")
    adoption_ids = generate_adoptions(conn, adopter_ids, animal_ids, fake)
    
    print("Gerando e inserindo doações...")
    donation_ids = generate_donations(conn, volunteer_ids, fake)
    
    conn.close()
    
    print("Geração de dados concluída com sucesso!")
    print(f"Total de Pessoas: {total_persons}")
    print(f"Total de Adotantes: {len(adopter_ids)}")
    print(f"Total de Voluntários: {len(volunteer_ids)}")
    print(f"Total de Animais: {total_animals}")
    print(f"Total de Adoções: {len(adoption_ids)}")
    print(f"Total de Doações: {len(donation_ids)}")

if __name__ == "__main__":
    main()
