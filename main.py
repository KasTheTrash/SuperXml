import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QFileDialog, QMenuBar, QCompleter)
from PyQt6.QtGui import QAction, QTextCursor, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class XMLEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pro XML Editor (PyQt6)")
        self.setGeometry(100, 100, 800, 600)

        # Κεντρικό Widget και Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Ο Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Ξεκινήστε να γράφετε το XML σας εδώ...")
        self.layout.addWidget(self.editor)

        # Ρύθμιση Autocomplete
        self.setup_autocomplete()

        # Δημιουργία Menu
        self.create_menu()

    def setup_autocomplete(self):
        # Λίστα με βασικά XML tags για το autocomplete
        tags = ["<?xml version='1.0' encoding='UTF-8'?>", "<root>", "</root>", 
                "<item>", "</item>", "<name>", "</name>", "<id>", "</id>"]
        
        self.model = QStandardItemModel()
        for tag in tags:
            self.model.appendRow(QStandardItem(tag))

        self.completer = QCompleter(self.model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWidget(self.editor)
        
        # Σύνδεση της επιλογής από το autocomplete με τον editor
        self.completer.activated.connect(self.insert_completion)
        
        # Παρακολούθηση του πληκτρολογίου
        self.editor.textChanged.connect(self.check_completion)

    def insert_completion(self, completion):
        tc = self.editor.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.MoveOperation.Left)
        tc.movePosition(QTextCursor.MoveOperation.EndOfWord)
        tc.insertText(completion[-extra:])
        self.editor.setTextCursor(tc)

    def check_completion(self):
        tc = self.editor.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        prefix = tc.selectedText()
        
        if len(prefix) > 0:
            self.completer.setCompletionPrefix(prefix)
            cr = self.editor.cursorRect()
            self.completer.complete(cr)

    def create_menu(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("Αρχείο")

        open_action = QAction("Άνοιγμα (Αναζήτηση)", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Αποθήκευση (UTF-8)", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

    def open_file(self):
        # Αναζήτηση αρχείου στον υπολογιστή
        file_path, _ = QFileDialog.getOpenFileName(self, "Άνοιγμα XML", "", "XML Files (*.xml);;All Files (*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.editor.setPlainText(file.read())

    def save_file(self):
        # Αποθήκευση αρχείου με UTF-8 encoding
        file_path, _ = QFileDialog.getSaveFileName(self, "Αποθήκευση XML", "", "XML Files (*.xml);;All Files (*)")
        if file_path:
            if not file_path.endswith('.xml'):
                file_path += '.xml'
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.editor.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XMLEditor()
    window.show()
    sys.exit(app.exec())