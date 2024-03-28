import sys
from PyQt5.Qt import QStandardItemModel, QStandardItem

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QVBoxLayout,
    QWidget, QPushButton, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
)

class AddRegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Register")
        self.form_layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.size_edit = QLineEdit()
        self.form_layout.addRow("Name:", self.name_edit)
        self.form_layout.addRow("Address:", self.address_edit)
        self.form_layout.addRow("Size:", self.size_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.form_layout.addRow(self.button_box)

    def get_register_info(self):
        return (
            self.name_edit.text(),
            self.address_edit.text(),
            self.size_edit.text()
        )

class RegisterMapGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FPGA Register Map GUI")
        self.setGeometry(100, 100, 800, 600)

        # Create a QTreeView
        self.tree_view = QTreeView()
        self.setCentralWidget(self.tree_view)

        # Create a QStandardItemModel
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Address", "Size"])
        self.tree_view.setModel(self.model)

        # Add buttons for adding and deleting registers/blocks
        self.add_register_button = QPushButton("Add Register")
        self.add_register_button.clicked.connect(self.add_register_clicked)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_clicked)

        # Layout for the buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_register_button)
        button_layout.addWidget(self.delete_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tree_view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Add example data
        self.add_register("Register1", "0x00", "4")
        self.add_register("Register2", "0x04", "2")
        self.add_register("Register3", "0x08", "1")
        self.add_register_block("Block1", [
            ("BlockReg1", "0x0C", "2"),
            ("BlockReg2", "0x10", "4"),
        ])

    def add_register_clicked(self):
        dialog = AddRegisterDialog(self)
        if dialog.exec_():
            name, address, size = dialog.get_register_info()
            self.add_register(name, address, size)

    def delete_clicked(self):
        indexes = self.tree_view.selectedIndexes()
        # for index in indexes:
        print(indexes)
        item = self.model.itemFromIndex(indexes[0])
        block_row = item.row()
        print(block_row)
        #find top block row index
        while True:
            if type(item.parent()) is type(None):
                break
            else:
                print(type(item))
                item = item.parent()

        actual_row = item.row()
        print(actual_row)

        testrow = QStandardItem('testrow')
        #self.model.insertRow(actual_row,testrow)
        item.appendRow(testrow)


        # if not indexes:
        #     return

        # # Store references to selected items
        # selected_items = []
        # for index in indexes:
        #     item = self.model.itemFromIndex(index)
        #     if item and item not in selected_items:
        #         selected_items.append(item)

        # # Delete selected items
        # for item in selected_items:
        #     parent_item = item.parent()
        #     if parent_item:
        #         parent_item.removeRow(item.row())
        #     else:
        #         self.model.removeRow(item.row())


    def add_register(self, name, address, size):
        row = [QStandardItem(field) for field in (name, address, size)]
        #print(len(row))
        self.model.appendRow(row)

    def insert_register(self, name, address, size):
        testrow = QStandardItem('testrow')
        print(len(row))
        self.model.appendRow(row)

    def add_register_block(self, name, registers):
        block_item = QStandardItem(name)
        block_addr = QStandardItem(str(registers[0][1]))
        #self.model.appendRow([block_item,block_addr])
        #block_item.setChild(0,0,block_addr)
        #block_item = self.model.findItems("Block1")
        #print(block_item)
        for register in registers:
            row = [QStandardItem(field) for field in register]
            block_item.appendRow(row)
        self.model.appendRow([block_item,block_addr])
        testrow = QStandardItem('testrow')
        self.model.insertRow(2,testrow)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = RegisterMapGUI()
    gui.show()
    sys.exit(app.exec_())



