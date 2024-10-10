import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import csv
from tkinter import filedialog


class DatabaseManager:
    def __init__(self, db_name="inventory.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            date_added TEXT NOT NULL
        )
        ''')
        self.connection.commit()

    def add_item(self, item_name, description, quantity, unit_price, date_added):
        cursor = self.connection.cursor()
        total_price = quantity * unit_price
        cursor.execute('''
        INSERT INTO inventory (item_name, description, quantity, unit_price, total_price, date_added)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (item_name, description, quantity, unit_price, total_price, date_added))
        self.connection.commit()

    def get_inventory(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM inventory")
        return cursor.fetchall()

    def update_item(self, item_id, item_name, description, quantity, unit_price, date_added):
        cursor = self.connection.cursor()
        total_price = quantity * unit_price  # Calculate total price
                # Update the item based on ID
        cursor.execute('''
            UPDATE inventory
            SET item_name = ?, description = ?, quantity = ?, unit_price = ?, total_price = ?, date_added = ?
            WHERE id = ?
        ''', (item_name, description, quantity, unit_price, total_price, date_added, item_id))
        self.connection.commit()


    def delete_item(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        self.connection.commit()
        
    def search_inventory(self, search_term, search_field):
        cursor = self.connection.cursor()
        # Dynamically build the query based on the search field
        if search_field == "Item Name":
            query = "SELECT * FROM inventory WHERE LOWER(name) LIKE ?"
        elif search_field == "Description":
            query = "SELECT * FROM inventory WHERE LOWER(description) LIKE ?"
        elif search_field == "Quantity":
            query = "SELECT * FROM inventory WHERE quantity = ?"
        elif search_field == "Unit Price":
            query = "SELECT * FROM inventory WHERE unit_price = ?"
        # Execute the query
        cursor.execute(query, ('%' + search_term + '%',) if search_field in ["Item Name", "Description"] else (search_term,))
        return cursor.fetchall()

    def get_paginated_inventory(self, page, items_per_page):
        offset = (page - 1) * items_per_page
        cursor = self.connection.cursor()
        query = "SELECT * FROM inventory LIMIT ? OFFSET ?"
        cursor.execute(query, (items_per_page, offset))
        return cursor.fetchall()

    def get_inventory_count(self):
        cursor = self.connection.cursor()
        query = "SELECT COUNT(*) FROM inventory"
        cursor.execute(query)
        return cursor.fetchone()[0]
    def sort_inventory(self, field, reverse):
        cursor = self.connection.cursor()
        query = f"SELECT * FROM inventory ORDER BY {field} {'DESC' if reverse else 'ASC'}"
        cursor.execute(query)
        return cursor.fetchall()


class InventoryApp:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.root.title("Inventory System")
        self.current_page = 1
        self.items_per_page = 10  # Number of items per page
        self.total_pages = 1

        # Set up the UI elements (entry fields, labels, buttons)
        self.setup_ui()

    def setup_ui(self):
    # Item Name
        self.item_name_label = tk.Label(self.root, text="Item Name:")
        self.item_name_label.grid(row=0, column=0)
        self.item_name_entry = tk.Entry(self.root)
        self.item_name_entry.grid(row=0, column=1)

            # Description
        self.description_label = tk.Label(self.root, text="Description:")
        self.description_label.grid(row=1, column=0)
        self.description_entry = tk.Entry(self.root)
        self.description_entry.grid(row=1, column=1)

            # Quantity
        self.quantity_label = tk.Label(self.root, text="Quantity:")
        self.quantity_label.grid(row=2, column=0)
        self.quantity_entry = tk.Entry(self.root)
        self.quantity_entry.grid(row=2, column=1)

            # Unit Price
        self.unit_price_label = tk.Label(self.root, text="Unit Price:")
        self.unit_price_label.grid(row=3, column=0)
        self.unit_price_entry = tk.Entry(self.root)
        self.unit_price_entry.grid(row=3, column=1)

            # Add Button
        self.add_button = tk.Button(self.root, text="Add Item", command=self.add_item)
        self.add_button.grid(row=4, column=0, columnspan=2)

            # Update and Delete Buttons
        self.update_button = tk.Button(self.root, text="Update Item", command=self.update_item)
        self.update_button.grid(row=5, column=0, columnspan=2)

        self.delete_button = tk.Button(self.root, text="Delete Item", command=self.delete_item)
        self.delete_button.grid(row=6, column=0, columnspan=2)
        
        # Reset Button
        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_inventory)
        self.reset_button.grid(row=6, column=3)
        # Search Field
       # Search criteria dropdown
        self.search_label = tk.Label(self.root, text="Search By:")
        self.search_label.grid(row=7, column=0)
        self.search_criteria = tk.StringVar()
        self.search_criteria.set("Item Name")  # Default search by item name
        self.search_dropdown = ttk.Combobox(self.root, textvariable=self.search_criteria)
        self.search_dropdown['values'] = ("Item Name", "Description", "Quantity", "Unit Price")
        self.search_dropdown.grid(row=7, column=1)

        # Search field
        self.search_label = tk.Label(self.root, text="Search:")
        self.search_label.grid(row=8, column=0)
        self.search_entry = tk.Entry(self.root)
        self.search_entry.grid(row=8, column=1)
        self.search_button = tk.Button(self.root, text="Search", command=self.search_inventory)
        self.search_button.grid(row=8, column=2)

        
        
        
        
        # Export to CSV Button
        self.export_button = tk.Button(self.root, text="Export to CSV", command=self.export_to_csv)
        self.export_button.grid(row=10, column=3, columnspan=2)
        
        # Pagination Controls
        self.prev_button = tk.Button(self.root, text="Previous", command=self.prev_page)
        self.prev_button.grid(row=10, column=0)
        self.pagination_label = tk.Label(self.root, text=f"Page {self.current_page} of {self.total_pages}")
        self.pagination_label.grid(row=10, column=1)
        self.next_button = tk.Button(self.root, text="Next", command=self.next_page)
        self.next_button.grid(row=10, column=2)
        
        # Backup Button
        self.backup_button = tk.Button(self.root, text="Backup", command=self.backup_inventory)
        self.backup_button.grid(row=11, column=0)

        # Restore Button
        self.restore_button = tk.Button(self.root, text="Restore", command=self.restore_inventory)
        self.restore_button.grid(row=11, column=1)


        # Inventory Display
        self.inventory_tree = ttk.Treeview(self.root, columns=("ID", "Name", "Description", "Quantity", "Unit Price", "Total Price", "Date Added"), show="headings")
        self.inventory_tree.grid(row=9, column=0, columnspan=4)

        # Correctly reference the Treeview column names when setting up the headings
        self.inventory_tree.heading("ID", text="ID", command=lambda: self.sort_inventory("ID", False))
        self.inventory_tree.heading("Name", text="Item Name", command=lambda: self.sort_inventory("Name", False))
        self.inventory_tree.heading("Description", text="Description", command=lambda: self.sort_inventory("Description", False))
        self.inventory_tree.heading("Quantity", text="Quantity", command=lambda: self.sort_inventory("Quantity", False))
        self.inventory_tree.heading("Unit Price", text="Unit Price", command=lambda: self.sort_inventory("Unit Price", False))
        self.inventory_tree.heading("Total Price", text="Total Price")  # No sorting for total price
        self.inventory_tree.heading("Date Added", text="Date Added", command=lambda: self.sort_inventory("Date Added", False))


        self.inventory_tree.bind("<ButtonRelease-1>", self.select_item)
        self.load_inventory()

    def search_inventory(self):
        search_term = self.search_entry.get().lower()
        search_field = self.search_criteria.get()

        if not search_term:
            messagebox.showerror("Invalid Search", "Please enter a search term.")
            return

        # Clear the treeview before showing search results
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        # Get search results based on the selected field
        results = self.db_manager.search_inventory(search_term, search_field)

        for row in results:
            self.inventory_tree.insert("", tk.END, values=row)


    def load_search_results(self, results):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        for row in results:
            self.inventory_tree.insert("", tk.END, values=row)


    def add_item(self):
        item_name = self.item_name_entry.get()
        description = self.description_entry.get()

        try:
            quantity = int(self.quantity_entry.get())
            unit_price = float(self.unit_price_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity and Unit Price must be numeric values.")
            return

        if not item_name or not description:
            messagebox.showerror("Invalid Input", "Item Name and Description cannot be empty.")
            return

        date_added = datetime.now().strftime("%Y-%m-%d")
        self.db_manager.add_item(item_name, description, quantity, unit_price, date_added)
        messagebox.showinfo("Success", "Item added successfully!")
        self.clear_fields()
        self.load_inventory()


    def update_item(self):
        selected_item = self.inventory_tree.focus()
        if selected_item:
            item_data = self.inventory_tree.item(selected_item)['values']
            item_id = item_data[0]

            item_name = self.item_name_entry.get()
            description = self.description_entry.get()
            quantity = int(self.quantity_entry.get())
            unit_price = float(self.unit_price_entry.get())
            date_added = datetime.now().strftime("%Y-%m-%d")

            if item_name and description and quantity and unit_price:
                self.db_manager.update_item(item_id, item_name, description, quantity, unit_price, date_added)
                messagebox.showinfo("Success", "Item updated successfully!")
                self.clear_fields()
                self.load_inventory()
            else:
                messagebox.showerror("Error", "All fields are required for updating an item.")

    def delete_item(self):
        selected_item = self.inventory_tree.focus()
        if selected_item:
            item_data = self.inventory_tree.item(selected_item)['values']
            item_id = item_data[0]

            confirmation = messagebox.askyesno("Confirm", "Are you sure you want to delete this item?")
            if confirmation:
                self.db_manager.delete_item(item_id)
                messagebox.showinfo("Success", "Item deleted successfully!")
                self.clear_fields()
                self.load_inventory()

    def select_item(self, event):
        selected_item = self.inventory_tree.focus()
        if selected_item:
            item_data = self.inventory_tree.item(selected_item)['values']
            self.item_name_entry.delete(0, tk.END)
            self.item_name_entry.insert(0, item_data[1])
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, item_data[2])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, item_data[3])
            self.unit_price_entry.delete(0, tk.END)
            self.unit_price_entry.insert(0, item_data[4])

    def clear_fields(self):
        self.item_name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.unit_price_entry.delete(0, tk.END)

    def load_inventory(self):
        # Clear current treeview data
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        # Get paginated data
        inventory_data = self.db_manager.get_paginated_inventory(self.current_page, self.items_per_page)

        # Insert data into the treeview
        for row in inventory_data:
            self.inventory_tree.insert("", tk.END, values=row)

        # Calculate and update the total pages
        total_items = self.db_manager.get_inventory_count()
        self.total_pages = (total_items // self.items_per_page) + (1 if total_items % self.items_per_page != 0 else 0)

        # Update pagination label
        self.update_pagination_label()


    def sort_inventory(self, field, reverse):
        # Mapping Treeview column names to actual database field names
        field_mapping = {
            "ID": "id",
            "Name": "item_name",
            "Description": "description",
            "Quantity": "quantity",
            "Unit Price": "unit_price",
            "Total Price": "total_price",
            "Date Added": "date_added"
        }
        
        # Map the Treeview field to the corresponding database field
        db_field = field_mapping.get(field)
    
        # Clear current Treeview data
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
    
        # Get sorted data from database using the mapped field
        sorted_data = self.db_manager.sort_inventory(db_field, reverse)
    
        # Insert sorted data back into the Treeview
        for row in sorted_data:
            self.inventory_tree.insert("", tk.END, values=row)
    
        # Reverse the sort order for the next click
        self.inventory_tree.heading(field, command=lambda: self.sort_inventory(field, not reverse))


    def clear_fields(self):
        self.item_name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.unit_price_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
    def reset_inventory(self):
        self.search_entry.delete(0, tk.END)
        self.load_inventory()  # Reload all items from the database
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Item Name", "Description", "Quantity", "Unit Price", "Total Price", "Date Added"])
                for row in self.db_manager.get_inventory():
                    writer.writerow(row)
            messagebox.showinfo("Success", "Inventory exported successfully!")
    def update_pagination_label(self):
        self.pagination_label.config(text=f"Page {self.current_page} of {self.total_pages}")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_inventory()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_inventory()

    def backup_inventory(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if file_path:
            with open(self.db_manager.db_name, 'rb') as db_file:
                with open(file_path, 'wb') as backup_file:
                    backup_file.write(db_file.read())
            messagebox.showinfo("Success", "Backup created successfully!")
            
    def restore_inventory(self):
        file_path = filedialog.askopenfilename(filetypes=[("Database files", "*.db")])
        if file_path:
            confirm = messagebox.askyesno("Confirm Restore", "Restoring from a backup will overwrite the current database. Continue?")
            if confirm:
                with open(file_path, 'rb') as backup_file:
                    with open(self.db_manager.db_name, 'wb') as db_file:
                        db_file.write(backup_file.read())
                messagebox.showinfo("Success", "Database restored successfully!")
                self.load_inventory()




# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager()
    app = InventoryApp(root, db_manager)
    root.mainloop()
