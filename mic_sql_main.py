import pyodbc
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMainWindow, QListWidget, QHBoxLayout, QComboBox, QAbstractItemView, QVBoxLayout
from PyQt5.QtCore import Qt
import datetime

def create_connection():
    server = 'ESN501D1274466\MSSQLSERVER1'
    database = 'registiration'
    username = 'SA'
    password = 'Senai@123'
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    return pyodbc.connect(connection_string)

def register_client(cpf, name, surname, email, phone, birthdate):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(""" 
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Clients' AND xtype='U')
            CREATE TABLE Clients (
                cpf VARCHAR(15) PRIMARY KEY,
                name VARCHAR(100),
                surname VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(15),
                birthdate DATE
            )
        """)
        sql = """
        INSERT INTO Clients(cpf, name, surname, email, phone, birthdate)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (cpf, name, surname, email, phone, birthdate)
        cursor.execute(sql, values)
        connection.commit()
        print("Client registered successfully.")
    except pyodbc.Error as err:
        print(f"An error occurred: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_client(cpf, name, surname, email, phone, birthdate):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = """
        UPDATE Clients
        SET name = ?, surname = ?, email = ?, phone = ?, birthdate = ?
        WHERE cpf = ?
        """
        values = (name, surname, email, phone, birthdate, cpf)
        cursor.execute(sql, values)
        connection.commit()
        print("Client updated successfully.")
    except pyodbc.Error as err:
        print(f"An error occurred: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_registered_clients():
    clients = []
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name, surname, cpf, email, phone, birthdate FROM Clients")
        results = cursor.fetchall()
        clients = [{"name": row[0], "surname": row[1], "cpf": row[2], "email": row[3], 
                    "phone": row[4], "birthdate": row[5].strftime('%Y-%m-%d') if isinstance(row[5], datetime.date) else row[5]} 
                   for row in results]
    except pyodbc.Error as err:
        print(f"Error occurred: {err}")
    finally:
        if connection:
            connection.close()
    return clients

def editClient(self, client):
    self.current_client = client
    self.cpf_input.setText(client['cpf'])
    self.name_input.setText(client['name'])
    self.surname_input.setText(client['surname'])
    self.email_input.setText(client['email'])
    self.celular_input.setText(client['phone'])
    if isinstance(client['birthdate'], datetime.date):
        self.birthdate_input.setText(client['birthdate'].strftime('%Y-%m-%d'))
    else:
        self.birthdate_input.setText(client['birthdate'])

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Registration")
        self.setGeometry(400, 150, 800, 600)
        layout = QVBoxLayout()
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("CPF")
        layout.addWidget(self.cpf_input)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome")
        layout.addWidget(self.name_input)
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Sobrenome")
        layout.addWidget(self.surname_input)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-mail")
        layout.addWidget(self.email_input)
        self.celular_input = QLineEdit()
        self.celular_input.setPlaceholderText("Numero de celular")
        layout.addWidget(self.celular_input)
        self.birthdate_input = QLineEdit()
        self.birthdate_input.setPlaceholderText("Data de nascimento (YYYY-MM-DD)")
        layout.addWidget(self.birthdate_input)
        submit_button = QPushButton("Registrar Cliente")
        submit_button.clicked.connect(self.submitData)
        layout.addWidget(submit_button)
        self.remove_button = QPushButton("Remover Cliente Selecionado")
        self.remove_button.clicked.connect(self.removeSelectedClient)
        layout.addWidget(self.remove_button)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Pesquisa clientes...")
        self.search_bar.textChanged.connect(self.searchClients)
        layout.addWidget(self.search_bar)
        self.clients_list = QListWidget()
        self.clients_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.clients_list.clicked.connect(self.clientClicked)
        layout.addWidget(self.clients_list)
        self.all_clients = []
        self.current_client = None
        self.loadClients()
        self.setLayout(layout)

    def submitData(self):
        cpf = self.cpf_input.text()
        name = self.name_input.text()
        surname = self.surname_input.text()
        email = self.email_input.text()
        celular = self.celular_input.text()
        birthdate = self.birthdate_input.text()
        if self.current_client:
            update_client(cpf, name, surname, email, celular, birthdate)
        else:
            register_client(cpf, name, surname, email, celular, birthdate)
        self.loadClients()
        self.clearInputs()

    def loadClients(self):
        self.clients_list.clear()
        self.all_clients = get_registered_clients()
        for client in self.all_clients:
            item = f"{client['name']} {client['surname']} - {client['cpf']}"
            self.clients_list.addItem(item)

    def searchClients(self, text):
        self.clients_list.clear()
        filtered_clients = [client for client in self.all_clients if text.lower() in f"{client['name']} {client['surname']}".lower()]
        for client in filtered_clients:
            item = f"{client['name']} {client['surname']} - {client['cpf']} - {client['birthdate']}"
            self.clients_list.addItem(item)

    def editClient(self, client):
        self.current_client = client
        self.cpf_input.setText(client['cpf'])
        self.name_input.setText(client['name'])
        self.surname_input.setText(client['surname'])
        self.email_input.setText(client['email'])
        self.celular_input.setText(client['phone'])
        self.birthdate_input.setText(client['birthdate'])

    def removeClient(self, client):
        print(f"Removing client {client['cpf']}")
        self.removeClientFromDB(client['cpf'])
        self.loadClients()

    def removeClientFromDB(self, cpf):
        try:
            connection = create_connection()
            cursor = connection.cursor()
            sql = "DELETE FROM Clients WHERE cpf = ?"
            cursor.execute(sql, (cpf,))
            connection.commit()
            print(f"Client with CPF {cpf} removed successfully.")
        except pyodbc.Error as err:
            print(f"Error occurred: {err}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def removeSelectedClient(self):
        item = self.clients_list.currentItem()
        if item:
            client_data = item.text().split(" - ")
            cpf = client_data[1]
            client = next((c for c in self.all_clients if c['cpf'] == cpf), None)
            if client:
                self.removeClient(client)

    def clientClicked(self):
        item = self.clients_list.currentItem()
        client_data = item.text().split(" - ")
        cpf = client_data[1]
        client = next((c for c in self.all_clients if c['cpf'] == cpf), None)
        if client:
            self.editClient(client)

    def clearInputs(self):
        self.cpf_input.clear()
        self.name_input.clear()
        self.surname_input.clear()
        self.email_input.clear()
        self.celular_input.clear()
        self.birthdate_input.clear()
        self.current_client = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
