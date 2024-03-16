import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QDialog
from PyQt5 import QtCore as qtc

class Register:
    def __init__(self, name, size, desc, fields, access):
        self.name = name
        self.size = size
        self.desc = desc
        self.fields = []
        self.fields.append(fields) #add widget to add fields to 32-bit reg, will be dict with {size,field_name}, add check to make sure in range
        self.access = access #available options are rw, ro, wo wrc. Any others will throw error

class AnotherWindow(QWidget):
    submitClicked = qtc.pyqtSignal(list)
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.registers = []
        self.layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        self.registers_table = QTableWidget()
        self.registers_table.setColumnCount(3)
        self.registers_table.setHorizontalHeaderLabels(["Address", "Name", "Size"])
        self.btn = QPushButton("Submit")
        self.layout.addWidget(self.btn)
        self.btn.clicked.connect(self.confirm)

        self.layout.addWidget(self.registers_table)
        self.setLayout(self.layout)
        self.create_buttons()

    def confirm(self):  # <-- Here, the signal is emitted *along with the data we want*
        print(self.registers)
        self.submitClicked.emit(self.registers)
        self.close()
        
    def get_block_regs(self):
        return self.registers

    def add_register_dialog(self):
        dialog = AddRegisterDialog()
        if dialog.exec_():
            self.registers.append(Register(dialog.name, dialog.size))
            self.update_register_table()

    def create_buttons(self):
        self.button_layout = QHBoxLayout()

        self.add_register_button = QPushButton("Add Register")
        self.add_register_button.clicked.connect(self.add_register_dialog)
        self.button_layout.addWidget(self.add_register_button)

        self.layout.addLayout(self.button_layout)

    def update_register_table(self):
        self.registers_table.setRowCount(len(self.registers))
        for i, register in enumerate(self.registers):
            self.registers_table.setItem(i, 0, QTableWidgetItem(str(i)))  # Address
            self.registers_table.setItem(i, 1, QTableWidgetItem(register.name))
            self.registers_table.setItem(i, 2, QTableWidgetItem(str(register.size)))
            self.registers_table.setItem(i, 3, QTableWidgetItem(register.desc))
            self.registers_table.setItem(i, 4, QTableWidgetItem(str(register.fields)))
            self.registers_table.setItem(i, 5, QTableWidgetItem(str(register.access)))



class RegisterMapGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FPGA Register Map Tool")
        self.setGeometry(100, 100, 800, 600)

        self.registers = []
        self.blocks = []
        self.copied_regs = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.create_register_map_widgets()
        self.create_buttons()
    
    def show_sub_window(self):  # <-- Here, we create *and connect* the sub window's signal to the main window's slot
        self.sub_window = AnotherWindow()
        self.sub_window.submitClicked.connect(self.on_sub_window_confirm)
        self.sub_window.show()
    
    def on_sub_window_confirm(self, regs):  # <-- This is the main window's slot
        self.from_subwindow = regs
        print(self.from_subwindow)
        self.registers.append(regs)
        # for reg in regs:
        #     print(reg.name)
        #     self.registers.append(Register(reg.name, reg.size))
        self.update_register_table()

    def create_register_map_widgets(self):
        self.register_map_layout = QVBoxLayout()

        self.registers_table = QTableWidget()
        self.registers_table.setColumnCount(6)
        self.registers_table.setHorizontalHeaderLabels(["Address", "Name", "Size", "Description", "Fields", "Access"])

        self.register_map_layout.addWidget(self.registers_table)

        self.layout.addLayout(self.register_map_layout)

    def create_buttons(self):
        self.button_layout = QHBoxLayout()

        self.add_register_button = QPushButton("Add Register")
        self.add_register_button.clicked.connect(self.add_register_dialog)
        self.button_layout.addWidget(self.add_register_button)

        self.add_block_button = QPushButton("Add Block")
        #self.add_block_button.clicked.connect(self.add_block_window)
        self.add_block_button.clicked.connect(self.show_sub_window)
        self.button_layout.addWidget(self.add_block_button)

        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_selected)
        self.button_layout.addWidget(self.copy_button)

        self.paste_button = QPushButton("Paste")
        self.paste_button.clicked.connect(self.paste_selected)
        self.button_layout.addWidget(self.paste_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected)
        self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

    def add_register_dialog(self):
        dialog = AddRegisterDialog()
        if dialog.exec_():
            self.registers.append(Register(dialog.name, dialog.size, dialog.desc, dialog.fields, dialog.access))
            self.update_register_table()

    def update_register_table(self):
        self.registers_table.setRowCount(len(self.registers))
        offset = 0
        for i, register in enumerate(self.registers):
            if type(register) is list:
                for j, register in enumerate(register):
                    self.registers_table.setItem(j+i, 0, QTableWidgetItem(str(j)))  # Address
                    self.registers_table.setItem(j+i, 1, QTableWidgetItem(register.name))
                    self.registers_table.setItem(j+i, 2, QTableWidgetItem(str(register.size)))
                    self.registers_table.setItem(j+i, 3, QTableWidgetItem(register.desc))
                    self.registers_table.setItem(j+i, 4, QTableWidgetItem(str(register.fields)))
                    self.registers_table.setItem(j+i, 5, QTableWidgetItem(str(register.access)))
                    offset = j
            else:
                self.registers_table.setItem(i+offset, 0, QTableWidgetItem(str(i)))  # Address
                self.registers_table.setItem(i+offset, 1, QTableWidgetItem(register.name))
                self.registers_table.setItem(i+offset, 2, QTableWidgetItem(str(register.size)))
                self.registers_table.setItem(i+offset, 3, QTableWidgetItem(register.desc))
                self.registers_table.setItem(i+offset, 4, QTableWidgetItem(str(register.fields)))
                self.registers_table.setItem(i+offset, 5, QTableWidgetItem(str(register.access)))

    def delete_selected(self):
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
            del self.registers[index.row()]
        self.update_register_table()

    def copy_selected(self):
        # for reg in self.registers:
        #     print('dumping registers')
        #     print(reg.name)
        self.copied_regs = []
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
            self.copied_regs.append(self.registers[index.row()])
            print('index.row() =  {}'.format(index.row()))
            print('Copying {} at location {}'.format(self.registers[index.row()].name, index.row())) 
            #i think this is erroring because its inserting a list from the paste
    
    def paste_selected(self):
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
            print('paste index.row() =  {}'.format(index.row()))
            row = index.row()
            break
        #print('Printing at location {}'.format(self.copied_regs.name, index.row()))
        for reg in self.copied_regs:
            self.registers.insert(row,reg)
        self.update_register_table()

class AddRegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Register")
        self.layout = QVBoxLayout()

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.size_label = QLabel("Size:")
        self.size_input = QLineEdit()
        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.size_input)

        self.desc_label = QLabel("Description:")
        self.desc_input = QLineEdit()
        self.layout.addWidget(self.desc_label)
        self.layout.addWidget(self.desc_input)

        self.fields_label = QLabel("Fields:")
        self.fields_input = QLineEdit()
        self.layout.addWidget(self.fields_label)
        self.layout.addWidget(self.fields_input)

        self.access_label = QLabel("Access:")
        self.access_input = QLineEdit()
        self.layout.addWidget(self.access_label)
        self.layout.addWidget(self.access_input)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.accept)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    @property
    def name(self):
        return self.name_input.text()

    @property
    def size(self):
        return int(self.size_input.text())
    
    @property
    def desc(self):
        return self.desc_input.text()
    
    @property
    def fields(self):
        return self.fields_input.text()

    @property
    def access(self):
        return self.access_input.text()
    

class AddBlockDialog(QDialog):
    def __init__(self, registers):
        super().__init__()
        self.setWindowTitle("Add Block")
        self.layout = QVBoxLayout()

        self.name_label = QLabel("Block Name:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.registers_label = QLabel("Registers (comma-separated):")
        self.registers_input = QLineEdit()
        self.layout.addWidget(self.registers_label)
        self.layout.addWidget(self.registers_input)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.accept)
        self.layout.addWidget(self.add_button)

        self.button = QPushButton("Push To Add Register")
        self.button.clicked.connect(self.show_new_window)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def show_new_window(self, checked):
        self.w = AnotherWindow()
        self.w.show()

    @property
    def name(self):
        return self.name_input.text()

    @property
    def registers(self):
        return [reg.strip() for reg in self.registers_input.text().split(",")]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RegisterMapGUI()
    gui.show()
    sys.exit(app.exec_())
