import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox, QDialog, QFormLayout, QLineEdit
import sqlite3
from db import create_database

DATABASE_NAME = 'bookstore.db'
BOOKS_TABLE_NAME = 'books'

class BookstoreApp(QMainWindow):
    def __init__(self):
        super().__init__()

        create_database()

        self.setWindowTitle("Bookstore Admin")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.books_list = QListWidget()
        self.layout.addWidget(self.books_list)

        self.load_books()

        self.addButton = QPushButton("Добавить книгу")
        self.deleteButton = QPushButton("Удалить книгу")

        self.addButton.clicked.connect(self.show_add_book_dialog)
        self.deleteButton.clicked.connect(self.delete_book)

        self.layout.addWidget(self.addButton)
        self.layout.addWidget(self.deleteButton)

    def load_books(self):
        try:
            with sqlite3.connect(DATABASE_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT * FROM {BOOKS_TABLE_NAME}')
                books = cursor.fetchall()

            self.books_list.clear()
            for book in books:
                self.books_list.addItem(f"{book[1]} - {book[3]} in stock - ${book[4]}")
        except Exception as e:
            self.handle_error(f"Error loading books: {str(e)}")

    def show_add_book_dialog(self):
        dialog = AddBookDialog(parent=self)
        if dialog.exec() == QDialog.accepted:
            self.load_books()

    def delete_book(self):
        selected_item = self.books_list.currentItem()
        if selected_item:
            book_title = selected_item.text().split(" - ")[0]
            try:
                with sqlite3.connect(DATABASE_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f'DELETE FROM {BOOKS_TABLE_NAME} WHERE title = ?', (book_title,))
                self.load_books()
            except Exception as e:
                self.handle_error(f"Error deleting book: {str(e)}")
        else:
            self.handle_error("Select a book to delete.")

    def handle_error(self, message):
        QMessageBox.critical(self, "Error", message, QMessageBox.StandardButton.Ok)


class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Добавить книгу")

        layout = QFormLayout(self)

        self.title_input = QLineEdit()
        self.description_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()

        layout.addRow("Название:", self.title_input)
        layout.addRow("Описание:", self.description_input)
        layout.addRow("Количество:", self.quantity_input)
        layout.addRow("Цена:", self.price_input)

        addButton = QPushButton("Добавить")
        addButton.clicked.connect(self.add_book)
        layout.addWidget(addButton)

    def add_book(self):
        title = self.title_input.text()
        description = self.description_input.text()
        quantity = self.quantity_input.text()
        price = self.price_input.text()

        if not title or not description or not quantity or not price:
            QMessageBox.critical(self, "Error", "Please fill in all fields", QMessageBox.StandardButton.Ok)
            return

        try:
            quantity = int(quantity)  # Преобразование строки в целое число
            with sqlite3.connect(DATABASE_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(f'INSERT INTO {BOOKS_TABLE_NAME} (title, description, quantity, price) VALUES (?, ?, ?, ?)',
                               (title, description, quantity, price))
            self.accept()
        except ValueError:
            QMessageBox.critical(self, "Error", "Quantity must be a whole number", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding book: {str(e)}", QMessageBox.StandardButton.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    bookstore_app = BookstoreApp()
    bookstore_app.show()
    sys.exit(app.exec())