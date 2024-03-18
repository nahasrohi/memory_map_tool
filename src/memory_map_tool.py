import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QDialog
from PyQt5 import QtCore as qtc
import ast



class Block:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.registers = [] # List of register objects

    def add_register(self, reg):
        if type(reg) is Register:
            self.registers.append(reg)
        else:
            print('item added to block is not of type Register')

    def update_block(self, name, desc):
        self.name = name
        self.desc = desc


class Register:
    def __init__(self, name, size, desc, fields, access):
        self.name = name
        self.size = size
        self.desc = desc
        self.fields = {fields} # dictionary, use syntax '31-16' : 'some field', '15-0' : 'some other field' 
        #self.fields.append(fields) #add widget to add fields to 32-bit reg, will be dict with {size,field_name}, add check to make sure in range
        self.access = access #available options are rw, ro, wo wrc. Any others will throw error
    
    def update_reg(self, name, size, desc, fields, access):
        self.name = name
        self.size = size
        self.desc = desc
        self.fields = fields
        self.access = access
    
    def print_reg(self):
        print('Register Name: {}'.format(self.name))
        print('Register Size: {}'.format(self.size))
        print('Register Description: {}'.format(self.desc))
        print('Register Fields: {}'.format(self.fields))
        print('Register Access: {}'.format(self.access))
    
    def get_reg_values(self):
        value_list = [self.name, self.size, self.desc, self.fields, self.access]
        return value_list


class add_block_window(QWidget):
    submitClicked = qtc.pyqtSignal(Block)
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
        self.registers_table.setColumnCount(6)
        self.registers_table.setHorizontalHeaderLabels(["Address", "Name", "Size", "Description", "Fields", "Access"])
        self.btn = QPushButton("Submit")
        self.layout.addWidget(self.btn)
        self.btn.clicked.connect(self.confirm)

        self.layout.addWidget(self.registers_table)
        self.setLayout(self.layout)
        self.create_buttons()

    def confirm(self):  # <-- Here, the signal is emitted *along with the data we want*
        print(self.registers)
        new_block = Block(self.block_name_entry.text(), self.block_desc_entry.text())
        for item in self.registers:
            new_block.add_register(item)
        self.submitClicked.emit(new_block)
        self.close()
        
    def get_block_regs(self):
        return self.registers

    def add_register_dialog(self):
        dialog = AddRegisterDialog()
        if dialog.exec_():
            self.registers.append(Register(dialog.name, dialog.size, dialog.desc, dialog.fields, dialog.access))
            self.update_register_table()

    def create_buttons(self):
        self.button_layout = QHBoxLayout()
        self.add_register_button = QPushButton("Add Register")
        self.add_register_button.clicked.connect(self.add_register_dialog)
        self.button_layout.addWidget(self.add_register_button)
        self.block_name_label = QLabel("Block Name:")
        self.button_layout.addWidget(self.block_name_label)
        self.block_name_entry = QLineEdit()
        self.button_layout.addWidget(self.block_name_entry)
        self.desc_label = QLabel("Block Description:")
        self.button_layout.addWidget(self.desc_label)
        self.block_desc_entry = QLineEdit()
        self.button_layout.addWidget(self.block_desc_entry)
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

        self.registers = [] #list of register and block objects
        self.blocks = []
        self.copied_regs = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.create_register_map_widgets()
        self.create_buttons()

    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "Project Files (*.proj)")
        if filename:
            with open(filename, "w") as file:
                for item in self.registers:
                    if type(item) == Block:
                        blk_list = []
                        for blk_item in item.registers:
                            blk_list.append(blk_item.get_reg_values())
                        file.write(f"{'block'}:{item.name}:{item.desc}:{blk_list}\n")
                    else:
                        file.write(f"{'register'}:{item.name}:{item.size}:{item.desc}:{item.fields}:{item.access}\n")
            self.output_label.setText(f"Project saved to '{filename}'")

    def load_project(self):
            filename, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "Project Files (*.proj)")
            if filename:
                self.registers = []
                with open(filename, "r") as file:
                    for line in file:
                        parts = line.strip().split(":")
                        if parts[0] == 'block':
                            reg_list = []
                            name = parts[1]
                            desc = parts[2]
                            new_block = Block(name, desc)
                            reg_arr = []
                            reg_arr.append(ast.literal_eval(parts[3]))
                            for item in reg_arr:
                                for reg_values in item:
                                    reg_list.append(Register(reg_values[0], reg_values[1], reg_values[2], str(reg_values[3]), reg_values[4]))
                            for reg in reg_list:
                                new_block.add_register(reg)
                            self.registers.append(new_block)
                        else:
                            name = parts[1]
                            size = parts[2]
                            desc = parts[3]
                            fields = parts[4]
                            access = parts[5]
                            self.registers.append(Register(name, size, desc, fields, access))
                #self.registers_table.clear()
                self.update_register_table()
                self.output_label.setText(f"Project loaded from '{filename}'")
    
    def show_add_block(self):  # <-- Here, we create *and connect* the sub window's signal to the main window's slot
        self.sub_window = add_block_window()
        self.sub_window.submitClicked.connect(self.on_add_block_confirm)
        self.sub_window.show()
    
    def on_add_block_confirm(self, block):  # <-- This is the main window's slot
        self.from_subwindow = block
        print(self.from_subwindow)
        self.registers.append(block)
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
        self.add_block_button.clicked.connect(self.show_add_block)
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

        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.move_up)
        self.button_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.move_down)
        self.button_layout.addWidget(self.move_down_btn)

        self.btn_save_project = QPushButton("Save Project")
        self.btn_save_project.clicked.connect(self.save_project)
        self.button_layout.addWidget(self.btn_save_project)
        
        self.btn_load_project = QPushButton("Load Project")
        self.btn_load_project.clicked.connect(self.load_project)
        self.button_layout.addWidget(self.btn_load_project)

        self.output_label = QLabel("")
        self.button_layout.addWidget(self.output_label)

        self.layout.addLayout(self.button_layout)

    def add_register_dialog(self):
        dialog = AddRegisterDialog()
        if dialog.exec_():
            self.registers.append(Register(dialog.name, dialog.size, dialog.desc, dialog.fields, dialog.access))
            self.output_label.setText(f"Added register {dialog.name}")
            self.update_register_table()
            
    def update_register_table(self):
        # Iterate through 'nested' list to find length
        reg_list_length = 0
        for item in self.registers:
            if type(item) is Block:
                for reg in item.registers:
                    reg_list_length = reg_list_length + 1
            else:
                reg_list_length = reg_list_length + 1

        self.registers_table.setRowCount(reg_list_length)

        line = 0
        for item in self.registers:
            if type(item) is Block:
                for reg in item.registers:
                    #reg.print_reg()
                    self.registers_table.setItem(line, 0, QTableWidgetItem(str(line)))  # Address
                    self.registers_table.setItem(line, 1, QTableWidgetItem(reg.name))
                    self.registers_table.setItem(line, 2, QTableWidgetItem(str(reg.size)))
                    self.registers_table.setItem(line, 3, QTableWidgetItem(reg.desc))
                    self.registers_table.setItem(line, 4, QTableWidgetItem(str(reg.fields)))
                    self.registers_table.setItem(line, 5, QTableWidgetItem(str(reg.access)))
                    line = line + 1
            else:
                self.registers_table.setItem(line, 0, QTableWidgetItem(str(line)))  # Address
                self.registers_table.setItem(line, 1, QTableWidgetItem(item.name))
                self.registers_table.setItem(line, 2, QTableWidgetItem(str(item.size)))
                self.registers_table.setItem(line, 3, QTableWidgetItem(item.desc))
                self.registers_table.setItem(line, 4, QTableWidgetItem(str(item.fields)))
                self.registers_table.setItem(line, 5, QTableWidgetItem(str(item.access)))
                line = line + 1

    def delete_selected(self):
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
            del self.registers[index.row()]
        self.update_register_table()

    def copy_selected(self):
        self.copied_regs = []
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
            self.copied_regs.append(self.registers[index.row()])
            print('index.row() =  {}'.format(index.row()))
            print('Copying {} at location {}'.format(self.registers[index.row()].name, index.row())) 
    
    def paste_selected(self):
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
            print('paste index.row() =  {}'.format(index.row()))
            row = index.row()
            break #TODO: Can't figure out how to just get the first index.row() so just breaking for now
        for reg in self.copied_regs:
            self.registers.insert(row,reg)
        self.update_register_table()

    def move_up_old(self):
        row_idxs = []
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=False):
            row_idxs.append(index.row())
        print('# Rows Selected: {}'.format(len(row_idxs)))
        if len(row_idxs) > 1:
            #print('row_idxs: {}'.format(row_idxs))
            #row_idxs.reverse()
            print('row_idxs: {}'.format(row_idxs))
            first_idx = row_idxs[0]
            last_idx = first_idx + len(row_idxs) - 1
            print("first_idx = {} last_idx = {}".format(first_idx,last_idx))
            item_copy = self.registers[first_idx-1]
            print('Printing Original Order')
            for item in self.registers:
                print(item.name)
            for i in range(first_idx-1,last_idx):
                print(i)
                self.registers[i] = self.registers[i+1]
            self.registers[last_idx] = item_copy
            print('Printing New Order')
            for item in self.registers:
                print(item.name)
        else:
            self.registers[row_idxs[0]], self.registers[row_idxs[0]-1] = self.registers[row_idxs[0]-1] , self.registers[row_idxs[0]]
        
        self.update_register_table()

    def move_up(self):
        row_idxs = []
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=False):
            row_idxs.append(index.row())
        print('# Rows Selected: {}'.format(len(row_idxs)))
        print('row_idxs: {}'.format(row_idxs))
        if len(row_idxs) > 1: # multi-row
            first_idx = row_idxs[0]
            last_idx = first_idx + len(row_idxs) - 1
            print("first_idx = {} last_idx = {}".format(first_idx,last_idx))
            item_copy = self.registers[first_idx-1]
            del self.registers[first_idx-1]
            self.registers.insert(last_idx,item_copy)
        else: # single row
            self.registers[row_idxs[0]], self.registers[row_idxs[0]-1] = self.registers[row_idxs[0]-1] , self.registers[row_idxs[0]]
        
        self.update_register_table()

    def move_down(self):
        row_idxs = []
        selected_indexes = self.registers_table.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=False):
            row_idxs.append(index.row())
        print('# Rows Selected: {}'.format(len(row_idxs)))
        print('row_idxs: {}'.format(row_idxs))
        if len(row_idxs) > 1: # multi-row
            first_idx = row_idxs[0]
            last_idx = first_idx + len(row_idxs) - 1
            print("first_idx = {} last_idx = {}".format(first_idx,last_idx))
            item_copy = self.registers[last_idx+1]
            del self.registers[last_idx+1]
            self.registers.insert(first_idx,item_copy)
        else: # single row
            self.registers[row_idxs[0]], self.registers[row_idxs[0]+1] = self.registers[row_idxs[0]+1] , self.registers[row_idxs[0]]
        
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
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RegisterMapGUI()
    gui.show()
    sys.exit(app.exec_())
