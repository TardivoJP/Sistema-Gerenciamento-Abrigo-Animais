import random
import sqlite3
from datetime import datetime, timedelta
from database import create_connection, create_tables

def random_date(start_year=2020, end_year=2023):
    # Gera uma data aleatória entre start_year e end_year
    start_dt = datetime(start_year, 1, 1)
    end_dt = datetime(end_year, 12, 31)
    delta = end_dt - start_dt
    random_days = random.randint(0, delta.days)
    return (start_dt + timedelta(days=random_days)).strftime("%Y-%m-%d")

def main():
    create_tables()  # Garante que as tabelas existem
    conn = create_connection()
    cursor = conn.cursor()

    # Listas auxiliares
    first_names = ["Ana", "Bruno", "Carla", "Daniel", "Eduardo", "Fernanda", "Gabriel", "Heloisa", "Igor", "Julia", "Karen", "Leonardo", "Marina", "Nathalia", "Oscar", "Paula", "Renato", "Silvia", "Tiago", "Vanessa"]
    last_names = ["Almeida", "Barbosa", "Cardoso", "Dias", "Esteves", "Fernandes", "Gomes", "Henriques", "Ibarra", "Jorge", "Klein", "Lima", "Mendes", "Neves", "Oliveira", "Pereira", "Quintas", "Ramos", "Santos", "Teixeira"]
    addresses = ["Rua A", "Rua B", "Av. Central", "Travessa X", "Alameda Y", "Estrada Velha", "Rodovia Z", "Rua do Limoeiro", "Av. Paulista", "Rua das Flores"]
    occupations = ["Engenheiro", "Professor", "Médico", "Advogado", "Analista", "Designer", "Motorista", "Enfermeiro", "Cozinheiro", "Programador"]
    breeds = ["Vira-lata", "Labrador", "Bulldog", "Persa", "Siamês", "Pincher", "Shiba", "Poodle", "Ragdoll", "Beagle"]
    animal_types = ["Cachorro", "Gato"]

    # Popula Adopters
    num_adopters = 300
    for _ in range(num_adopters):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        address = random.choice(addresses) + f", nº {random.randint(1,1000)}"
        phone = f"({random.randint(10,99)})9{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        cpf = "".join([str(random.randint(0,9)) for _ in range(11)])
        birth_date = random_date(1960,2002)
        occupation = random.choice(occupations)
        income = round(random.uniform(1000,10000),2)

        cursor.execute('''
            INSERT INTO adopters (name, address, phone, cpf, birth_date, occupation, income)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, phone, cpf, birth_date, occupation, income))

    # Popula Volunteers
    num_volunteers = 200
    for _ in range(num_volunteers):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        address = random.choice(addresses) + f", nº {random.randint(1,1000)}"
        phone = f"({random.randint(10,99)})9{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        cpf = "".join([str(random.randint(0,9)) for _ in range(11)])
        birth_date = random_date(1960,2000)
        availability = "Manhã" if random.choice([True,False]) else "Tarde"
        skills = " ".join(random.sample(["Cuidado", "Banho", "Adestramento", "Limpeza", "Transporte"], k=2))
        experience = "Experiente" if random.randint(1,10) > 3 else "Iniciante"
        motivation = "Ajudar os animais" if random.randint(1,10) > 5 else "Aprender"

        cursor.execute('''
            INSERT INTO volunteers (name, address, phone, cpf, birth_date, availability, skills, experience, motivation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, phone, cpf, birth_date, availability, skills, experience, motivation))

    # Popula Animals
    num_animals = 500
    for _ in range(num_animals):
        name = f"Animal_{random.randint(1,100000)}"
        type_ = random.choice(animal_types)
        breed = random.choice(breeds)
        vaccinated = random.choice([0,1])
        neutered = random.choice([0,1])
        description = "Animal resgatado"
        status = "Disponível"
        cursor.execute('''
            INSERT INTO animals (name, type, breed, vaccinated, neutered, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, type_, breed, vaccinated, neutered, description, status))

    # Cria Adoções
    # Precisamos de adotantes existentes, animais disponíveis
    # Primeiro pega lists
    cursor.execute('SELECT id FROM adopters')
    adopter_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT id FROM animals WHERE status = "Disponível"')
    available_animal_ids = [row[0] for row in cursor.fetchall()]

    num_adoptions = 200
    # Cada adoção: escolhe um adotante e um animal disponível, marca data e status
    for _ in range(num_adoptions):
        if not available_animal_ids:
            break  # Se acabaram os animais disponíveis, não podemos mais adotar
        adopter_id = random.choice(adopter_ids)
        animal_id = random.choice(available_animal_ids)
        available_animal_ids.remove(animal_id) # Esse animal agora será adotado

        date = random_date(2020,2023)
        status = random.choice(["Pendente","Concluída","Cancelada"])
        # Se cancelada, animal continua disponível? Aqui assumiremos não, mas idealmente se Cancelada, não adotou
        # Para simplificar, se status for Concluída, muda status do animal para Adotado
        # Se Cancelada ou Pendente, não muda.
        cursor.execute('''
            INSERT INTO adoptions (adopter_id, animal_id, date, status)
            VALUES (?, ?, ?, ?)
        ''', (adopter_id, animal_id, date, status))

        if status == "Concluída":
            cursor.execute('UPDATE animals SET status = "Adotado" WHERE id = ?', (animal_id,))

    # Doações
    # Precisamos de voluntários
    cursor.execute('SELECT id FROM volunteers')
    volunteer_ids = [row[0] for row in cursor.fetchall()]

    num_donations = 300
    for _ in range(num_donations):
        volunteer_id = random.choice(volunteer_ids)
        date = random_date(2020,2023)
        amount = round(random.uniform(10, 5000),2)
        cursor.execute('''
            INSERT INTO donations (volunteer_id, date, amount)
            VALUES (?, ?, ?)
        ''', (volunteer_id, date, amount))

    conn.commit()
    conn.close()
    print("População do banco concluída com sucesso!")

if __name__ == '__main__':
    main()
