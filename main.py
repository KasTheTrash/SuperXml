import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QFileDialog, QCompleter, QStatusBar, QMessageBox)
from PyQt6.QtGui import QAction, QTextCursor, QStandardItemModel, QStandardItem, QKeySequence
from PyQt6.QtCore import Qt

class XMLEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Delphi-Compatible XML Editor")
        self.setGeometry(100, 100, 900, 700)
        
        self.current_file_path = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.editor = QTextEdit()
        # Template που ακολουθεί τα στάνταρ της βιομηχανίας
        self.editor.setPlainText('<?xml version="1.0" encoding="UTF-8"?>\n<root>\n    <item>Content</item>\n</root>')
        self.layout.addWidget(self.editor)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.setup_autocomplete()
        self.create_menu()

    def setup_autocomplete(self):
        tags = ["<root>", "</root>", "<item>", "</item>", "<name>", "</name>", "<id>", "</id>"]
        self.model = QStandardItemModel()
        for tag in tags:
            self.model.appendRow(QStandardItem(tag))
        self.completer = QCompleter(self.model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWidget(self.editor)
        self.completer.activated.connect(self.insert_completion)
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
        file_menu = menubar.addMenu("Αρχείο")

        open_act = QAction("Άνοιγμα (Ctrl+O)", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self.open_file)
        
        save_act = QAction("Αποθήκευση (Ctrl+S)", self)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(self.save_file)

        file_menu.addActions([open_act, save_act])

    def is_xml_valid(self, text):
        try:
            ET.fromstring(text)
            return True, ""
        except ET.ParseError as e:
            return False, str(e)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Άνοιγμα", "", "XML Files (*.xml)")
        if file_path:
            try:
                # Δοκιμάζουμε να διαβάσουμε με utf-8-sig αν υπάρχει BOM
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    self.editor.setPlainText(f.read())
                self.current_file_path = file_path
                self.status_bar.showMessage(f"Αρχείο: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Σφάλμα", f"Αδυναμία ανάγνωσης: {e}")

    def save_file(self):
        raw_text = self.editor.toPlainText().strip()
        
        # 1. Validation
        valid, error_msg = self.is_xml_valid(raw_text)
        if not valid:
            QMessageBox.critical(self, "Σφάλμα XML", f"Το XML δεν είναι έγκυρο:\n{error_msg}")
            return

        if not self.current_file_path:
            self.current_file_path, _ = QFileDialog.getSaveFileName(self, "Αποθήκευση", "", "XML Files (*.xml)")
        
        if self.current_file_path:
            if not self.current_file_path.endswith('.xml'):
                self.current_file_path += '.xml'
            
            try:
                # 2. Καθαρισμός και Pretty Print χωρίς να προσθέτουμε έξτρα κενές γραμμές
                dom = xml.dom.minidom.parseString(raw_text)
                # Χρησιμοποιούμε μια τεχνική για να αφαιρέσουμε τις κενές γραμμές που προσθέτει το minidom
                pretty_xml = "\n".join([line for line in dom.toprettyxml(indent="    ").splitlines() if line.strip()])
                
                # 3. Αποθήκευση - Χρησιμοποιούμε newline='' για να ελέγχει η Python σωστά τις αλλαγές γραμμής
                with open(self.current_file_path, "w", encoding="utf-8-sig", newline='') as f:
                    f.write(pretty_xml)
                
                self.status_bar.showMessage("Αποθηκεύτηκε επιτυχώς χωρίς κενές γραμμές", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα Αποθήκευσης", f"Κάτι πήγε στραβά: {e}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XMLEditor()
    window.show()
    sys.exit(app.exec())