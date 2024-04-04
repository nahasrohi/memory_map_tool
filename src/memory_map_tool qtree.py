import sys
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5 import QtCore

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QTableView, QVBoxLayout, QSplitter, QTableWidget,QListView,
    QWidget, QPushButton, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QHBoxLayout
)

#### Parking Lot ####
#Set Data
#item.setData('test_data', QtCore.Qt.EditRole)
#tem_child.setData(str(hex(addr)), QtCore.Qt.EditRole)
#Get Data
#print(item_child.data(QtCore.Qt.EditRole))

#self.tree_view.sortByColumn(1, QtCore.Qt.AscendingOrder)

# def iterItems(self, root):
#     def recurse(parent):
#         for row in range(parent.rowCount()):
#             for column in range(parent.columnCount()):
#                 child = parent.child(row, column)
#                 yield child
#                 if child.hasChildren():
#                     yield from recurse(child)
#     if root is not None:
#         yield from recurse(root)

#######################

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

        self.splitter =  QSplitter()
        # Create a QTreeView
        self.tree_view = QTreeView()
        #self.setCentralWidget(self.tree_view)

        # Create a QTableView
        self.field_view = QTableView()
        self.field_view.hideColumn(0)
        #self.setCentralWidget(self.field_view)

        self.field_table = QTableWidget()
        self.field_table.setColumnCount(32)
        #self.field_table.setHorizontalHeaderLabels(["F31","F30","F29","F28","F27"])

        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.field_view)
        self.splitter.setOrientation(QtCore.Qt.Vertical)

        # Create a QStandardItemModel
        self.model = QStandardItemModel()
        header_list = ["Name", "Address", "Type", "Description"]
        for i in reversed(range(32)):
            header_list.append('F' + str(i))
        self.model.setHorizontalHeaderLabels(header_list)
        self.tree_view.setModel(self.model)
        self.field_view.setModel(self.model)
        

        # Add buttons for adding and deleting registers/blocks
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
        self.set_field_btn = QPushButton("Set Field")
        self.set_field_btn.clicked.connect(self.set_field)
        self.print_map_btn = QPushButton("Print Map")
        self.print_map_btn.clicked.connect(self.print_map)

        # Layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.insert_reg_button)
        button_layout.addWidget(self.insert_block_button)
        button_layout.addWidget(self.update_addr_button)
        button_layout.addWidget(self.move_up_button)
        button_layout.addWidget(self.move_down_button)
        button_layout.addWidget(self.set_field_btn)
        button_layout.addWidget(self.print_map_btn)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.splitter)
        #main_layout.addWidget(self.field_view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.tree_view.setDragDropMode(4)
        #self.tree_view.setDragEnabled(True)
        #self.tree_view.setAcceptDrops(True)

        #self.field_view.hideColumn(0)
        self.field_view.hideColumn(1)
        self.field_view.hideColumn(2)
        self.field_view.hideColumn(3)
        for i in range(4, 32+4):
            self.tree_view.hideColumn(i)
            self.field_view.setColumnWidth(i, 30)

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
                item_child_addr = item.child(row,1) #need names and addrs here TODO
                item_child = item.child(row,0) #need names and addrs here TODO
                if item_child.hasChildren():
                    self.loop_children(item_child, row_idx, addr)
                    #print(item_child.data(QtCore.Qt.EditRole))
                else:
                    item_child_addr.setData(str(hex(addr)), QtCore.Qt.EditRole)
                    #print("setting addr of child {} to {}".format(item_child.data(QtCore.Qt.EditRole), hex(addr)))
                    #print(item_child.data(QtCore.Qt.EditRole))
                    addr = addr + 32
        row_idx = row_idx + 1
        return addr, row_idx
        
    def set_field(self):
        indexes = self.field_view.selectedIndexes()
        print("table indexes len = {}".format(len(indexes)))
        item = self.model.itemFromIndex(indexes[0])
        actual_row = item.row()
        start_col = item.column()

        self.field_view.setSpan(actual_row, start_col, 1, len(indexes))
        print("col span = {}".format(self.field_view.columnSpan(actual_row, 5)))
    
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
                    #print(hex(addr))
                    #print(row_idx)
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
        if len(indexes) != 0:
            item = self.model.itemFromIndex(indexes[0])
            actual_row = item.row()
            while True:
                if type(item.parent()) is type(None):
                    break
                else:
                    print(type(item))
                    item = item.parent()
        else:
            actual_row = 0

        new_block = ['newblock', '0', 'Block', 'New Block']
        blockrow = [QStandardItem(field) for field in (new_block)]
        # for item in testrow:
        #     item.setDropEnabled(False)
        
        #insert initial template reg into block
        new_reg = ['newreg', '0', 'Register', 'New Register']
        regrow = [QStandardItem(field) for field in (new_reg)]
        for item in regrow:
            item.setDropEnabled(False)
            #item.setDragEnabled(False)
        blockrow[0].appendRow(regrow)
        self.model.insertRow(actual_row,blockrow)
        self.update_addr()

    def insert_reg_clicked(self):
        indexes = self.tree_view.selectedIndexes()
        item_type = 'Register'
        if len(indexes) != 0:
            item = self.model.itemFromIndex(indexes[0])
            item_type = self.model.itemFromIndex(indexes[2]).data(QtCore.Qt.EditRole)
            selected_row = item.row()
        else:
            selected_row = 0

        new_reg = ['newreg', '0', 'Register', 'New Register', 'reserved']
        regrow = [QStandardItem(field) for field in (new_reg)]

        # Commenting this out allows adding reg into block with button TODO: Fix this
        for item in regrow:
            item.setDropEnabled(False)

        if item_type == 'Block':
            item.appendRow(regrow)
        else:
            self.model.insertRow(selected_row,regrow)

        self.update_addr()        

    def delete_clicked(self):
        indexes = self.tree_view.selectedIndexes()
        if len(indexes) != 0:
            item = self.model.itemFromIndex(indexes[0])
            item_type = self.model.itemFromIndex(indexes[2]).data(QtCore.Qt.EditRole)
            selected_row = item.row()
            self.model.removeRow(selected_row)

    def print_map2(self):
        print("Printing Register Map")
        row_idx = 0
        addr = 0
        while True:
            item = self.model.item(row_idx,0)
            item_addr = self.model.item(row_idx,1)
            if type(item) is not type(None):
                print(item.data(QtCore.Qt.EditRole))  
                parent = item
                while item.hasChildren():
                    print('child')
                    item = item.child(row_idx+1,0)
                    row_idx = row_idx + 1
                    
                    # addr, row_idx = self.loop_children(item, row_idx, addr)
                    # print(hex(addr))
                    # print(row_idx)
                    # for row in range(item.rowCount()):
                    #     item_child = item.child(row,1)
                    #     item_child.setData(str(hex(addr)), QtCore.Qt.EditRole)
                    #     addr = addr + 32
                    
                else:
                    row_idx = row_idx + 1
            else:
                #print("No more items")
                break

    def print_map(self):
        root = self.model.invisibleRootItem()
        for item in self.iterItems(root):
            print("iter")
            pass
            #print(item.text())

    def iterItems(self, root):
        def recurse(parent, addr):
            for row in range(parent.rowCount()):
                #for column in range(parent.columnCount()):
                child = parent.child(row, 0)
                child_addr = parent.child(row, 1)
                child_br = parent.child(row, 2)
                yield child
                if child_br.text() != "Block":
                    child_addr.setData(str(hex(addr)), QtCore.Qt.EditRole)
                    addr = addr + 32
                    print(child.text()) #Added by IS
                if child.hasChildren():
                    yield from recurse(child,addr)
        if root is not None:
            addr = 0
            yield from recurse(root, addr)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = RegisterMapGUI()
    gui.show()
    sys.exit(app.exec_())



