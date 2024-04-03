import sys
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5 import QtCore

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QVBoxLayout,
    QWidget, QPushButton, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QHBoxLayout
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
        self.model.setHorizontalHeaderLabels(["Name", "Address", "Type", "Description"])
        self.tree_view.setModel(self.model)

        # Add buttons for adding and deleting registers/blocks
        self.add_register_button = QPushButton("Add Register")
        self.add_register_button.clicked.connect(self.add_register_clicked)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_clicked)
        self.insert_reg_button = QPushButton("Insert Reg")
        self.insert_reg_button.clicked.connect(self.insert_reg_clicked)
        self.insert_block_button = QPushButton("Insert Block")
        self.insert_block_button.clicked.connect(self.insert_block_clicked)
        self.update_addr_button = QPushButton("Update Addr")
        self.update_addr_button.clicked.connect(self.update_addr)
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self.move_up)
        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self.move_down)

        # Layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_register_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.insert_reg_button)
        button_layout.addWidget(self.insert_block_button)
        button_layout.addWidget(self.update_addr_button)
        button_layout.addWidget(self.move_up_button)
        button_layout.addWidget(self.move_down_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tree_view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.tree_view.setDragDropMode(4)
        #self.tree_view.setDragEnabled(True)
        #self.tree_view.setAcceptDrops(True)

        # Add example data
        self.add_register("Register1", "1", "Register")
        # self.add_register("Register2", "4", "Register")
        # self.add_register("Register3", "3", "Register")
        # self.add_register_block("Block1", [
        #     ("BlockReg1", "9", "2"),
        #     ("BlockReg2", "0", "4"),
        # ])

    def add_register_clicked(self):
        dialog = AddRegisterDialog(self)
        if dialog.exec_():
            name, address, size = dialog.get_register_info()
            self.add_register(name, address, size)

    def move_up(self):
        indexes = self.tree_view.selectedIndexes()
        item = self.model.itemFromIndex(indexes[0])
        row_idx = item.row()
        if row_idx != 0:
            row = self.model.takeRow(row_idx)
            self.model.insertRow(row_idx-1, row)
            self.tree_view.setCurrentIndex(self.model.index(row_idx-1, 0))
            self.update_addr()

    def move_down(self):
        indexes = self.tree_view.selectedIndexes()
        item = self.model.itemFromIndex(indexes[0])
        row_idx = item.row()
        row = self.model.takeRow(row_idx)
        self.model.insertRow(row_idx+1, row)
        self.tree_view.setCurrentIndex(self.model.index(row_idx+1, 0))
        self.update_addr()
        
    def loop_children(self, item, row_idx, addr):
        if item.hasChildren():
            for row in range(item.rowCount()):
                item_child = item.child(row,1)
                self.loop_children(item_child, row_idx, addr)
                item_child.setData(str(hex(addr)), QtCore.Qt.EditRole)
                print("setting addr of child")
                addr = addr + 32
            row_idx = row_idx + 1
            return addr, row_idx
        
    
    def update_addr(self):
        row_idx = 0
        addr = 0
        while True:
            item = self.model.item(row_idx,0)
            item_addr = self.model.item(row_idx,1)
            if type(item) is not type(None):
                #print(item.data(QtCore.Qt.EditRole))
                item_addr.setData(str(hex(addr)), QtCore.Qt.EditRole)
                
                if item.hasChildren():
                    #print('child')
                    addr, row_idx = self.loop_children(item, row_idx, addr)
                    print(addr)
                    print(row_idx)
                    # for row in range(item.rowCount()):
                    #     item_child = item.child(row,1)
                    #     item_child.setData(str(hex(addr)), QtCore.Qt.EditRole)
                    #     addr = addr + 32
                    # row_idx = row_idx + 1
                else:
                    row_idx = row_idx + 1
                    addr = addr + 32
            else:
                #print("No more items")
                break


    def insert_block_clicked(self):
        indexes = self.tree_view.selectedIndexes()
        # for index in indexes:
        print(indexes)
        item = self.model.itemFromIndex(indexes[0])
        print(item.data(QtCore.Qt.EditRole))
        block_row = item.row()
        #print(block_row)
        #find top block row index
        while True:
            if type(item.parent()) is type(None):
                break
            else:
                print(type(item))
                item = item.parent()

        actual_row = item.row()
        #print(actual_row)
        new_block = ['newblock', '0', 'Block', 'New Block']
        testrow = [QStandardItem(field) for field in (new_block)]
        # for item in testrow:
        #     item.setDropEnabled(False)
        # for item in testrow:
        #     item.setData('test_data', QtCore.Qt.EditRole)
        
        #insert initial template reg into block
        new_reg = ['newreg', '0', 'Register', 'New Register']
        regrow = [QStandardItem(field) for field in (new_reg)]
        for item in regrow:
            item.setDropEnabled(False)
            #item.setDragEnabled(False)
        testrow[0].appendRow(regrow)
        self.model.insertRow(actual_row,testrow)
        #self.tree_view.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.update_addr()

    def insert_reg_clicked(self):
        indexes = self.tree_view.selectedIndexes()
        # for index in indexes:
        print(indexes)
        item = self.model.itemFromIndex(indexes[0])
        item_type = self.model.itemFromIndex(indexes[2]).data(QtCore.Qt.EditRole)
        block_row = item.row()
        print(block_row)

        actual_row = item.row()
        print(actual_row)

        new_reg = ['newreg', '0', 'Register', 'New Register']
        testrow = [QStandardItem(field) for field in (new_reg)]
        for item in testrow:
            item.setDropEnabled(False)

        if item_type == 'Block':
            item.appendRow(testrow)
        else:
            self.model.insertRow(actual_row,testrow)

        self.update_addr()
            

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
        for item in row:
            item.setDropEnabled(False)
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
        #testrow = QStandardItem('testrow')
        #self.model.insertRow(2,testrow)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = RegisterMapGUI()
    gui.show()
    sys.exit(app.exec_())



