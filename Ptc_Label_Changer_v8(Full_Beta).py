# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 16:18:47 2024

@author: kenneyke
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import laspy
import numpy as np
import pandas as pd
import os
import glob

class PointCloudLabelChanger:
    def __init__(self, root):
        self.processing_method = "Single"  # Default to Single processing method
        self.root = root
        self.root.title("Point Cloud Label Changer")

        # Create a menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # Create a file menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Point Cloud", command=self.open_point_cloud)
        file_menu.add_command(label="Load Excel Sheet", command=self.load_excel_sheet)  # Added for Excel loading
        
        # Create a processing method menu
        processing_method_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Processing Method", menu=processing_method_menu)
        processing_method_menu.add_command(label="Single", command=self.set_single_process)
        processing_method_menu.add_command(label="Batch", command=self.set_batch_process)
        
        # Initialize variables
        self.point_cloud = None
        self.old_label_var = tk.StringVar()
        self.new_label_var = tk.StringVar()
        self.excel_file_path_var = tk.StringVar()  # Add this line to initialize the variable
        self.file_path = None
       
        
        # Create frame for process selection
        process_selection_frame = tk.Frame(root, padx=10, pady=10)
        process_selection_frame.pack()
                
        # Create label selection frame
        self.label_frame = tk.Frame(root, padx=10, pady=10)
        self.label_frame.pack()

        # Radio buttons for label change method
        self.label_change_method_var = tk.StringVar()
        self.label_change_method_var.set("Manual Entry")  # Default to manual entry
        manual_entry_radio = tk.Radiobutton(self.label_frame, text="Manual Entry", variable=self.label_change_method_var, value="Manual Entry", command=self.update_label_entry_method)
        manual_entry_radio.grid(row=0, column=0, pady=5)

        excel_entry_radio = tk.Radiobutton(self.label_frame, text="Excel Entry", variable=self.label_change_method_var, value="Excel Entry", command=self.update_label_entry_method)
        excel_entry_radio.grid(row=0, column=1, pady=5)

        old_label_frame_label = tk.Label(self.label_frame, text="Select old label:")
        old_label_frame_label.grid(row=1, column=0, pady=5)

        # Dropdown button for selecting old label
        self.old_label_dropdown = tk.OptionMenu(self.label_frame, self.old_label_var, *[""])
        self.old_label_dropdown.grid(row=1, column=1, pady=5)
        self.old_label_var.set("")

        new_label_frame_label = tk.Label(self.label_frame, text="Enter new label:")
        new_label_frame_label.grid(row=2, column=0, pady=5)

        self.new_label_entry = tk.Entry(self.label_frame, textvariable=self.new_label_var)
        self.new_label_entry.grid(row=2, column=1, pady=5)

        # Create button to add label change
        add_label_change_button = tk.Button(self.label_frame, text="Add Label Change", command=self.add_label_change)
        add_label_change_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Create label display frame
        label_display_frame = tk.Frame(root, padx=10, pady=10)
        label_display_frame.pack()

        label_display_frame_label = tk.Label(label_display_frame, text="Available Labels:")
        label_display_frame_label.grid(row=0, column=0, pady=5)

        self.available_labels_var = tk.StringVar()
        label_display_frame_data = tk.Label(label_display_frame, textvariable=self.available_labels_var, justify=tk.LEFT)
        label_display_frame_data.grid(row=0, column=1, pady=5)

        # Create frame to display label changes
        label_changes_frame = tk.Frame(root, padx=10, pady=10)
        label_changes_frame.pack()

        label_changes_frame_label = tk.Label(label_changes_frame, text="Label Changes:")
        label_changes_frame_label.grid(row=0, column=0, pady=5)

        self.label_changes_var = tk.StringVar()
        label_changes_frame_data = tk.Label(label_changes_frame, textvariable=self.label_changes_var, justify=tk.LEFT)
        label_changes_frame_data.grid(row=0, column=1, pady=5)

        # Button to change labels
        change_labels_button = tk.Button(root, text="Change Labels", command=self.change_label)
        change_labels_button.pack()
        
        # Create a button to switch between Manual and Excel Entry methods
        switch_method_button = tk.Button(self.label_frame, text="Switch Entry Method", command=self.switch_label_entry_method)
        switch_method_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Create a button to reset the application
        reset_button = tk.Button(root, text="Reset", command=self.reset)
        reset_button.pack()
        
        # Initialize a list to store label change inputs
        self.label_changes = []
        
    # Add a method to update the selected processing method
    def update_processing_method(self, method):
        self.processing_method = method
        messagebox.showinfo("Processing Method", f"Processing method set to: {method}")
    
    def set_single_process(self):
        self.update_processing_method("Single")
        # Add your logic for the "Single" processing method here
        print("Single processing method selected")

    def set_batch_process(self):
        self.update_processing_method("Batch")
        # Add your logic for the "Batch" processing method here
        print("Batch processing method selected")
    
    def reset(self):
        # Reset all variables and clear GUI components
        self.point_cloud = None
        self.old_label_var.set("")
        self.new_label_var.set("")
        self.excel_file_path_var.set("")
        self.file_path = None
        self.label_changes = []

        # Reset the label selection frame
        self.old_label_var.set("")
        self.new_label_var.set("")
        self.old_label_dropdown.config(state="normal")
        self.new_label_entry.config(state="normal")
        
        # Reset the label display frame
        self.available_labels_var.set("")
        
        # Reset the label changes frame
        self.label_changes_var.set("")

        # Update the dropdown menu with available labels
        labels = self.get_unique_labels()
        menu = self.old_label_dropdown["menu"]
        menu.delete(0, "end")
        for label in labels:
            menu.add_command(label=label, command=lambda l=label: self.old_label_var.set(l))
    
    def switch_label_entry_method(self):
        # Method to switch between Manual and Excel Entry methods
        current_method = self.label_change_method_var.get()
        if current_method == "Manual Entry":
            self.label_change_method_var.set("Excel Entry")
            self.update_label_entry_method()
        elif current_method == "Excel Entry":
            # Reload the original labels when switching back to Manual Entry
            self.label_change_method_var.set("Manual Entry")
            self.update_label_entry_method()
            labels = self.get_unique_labels()
            # Update the dropdown menu with available labels
            menu = self.old_label_dropdown["menu"]
            menu.delete(0, "end")
            for label in labels:
                menu.add_command(label=label, command=lambda l=label: self.old_label_var.set(l))

    
    def update_label_entry_method(self):
        method = self.label_change_method_var.get()
        if method == "Manual Entry":
            self.old_label_dropdown.config(state="normal")
            self.old_label_var.set("")
            self.new_label_entry.config(state="normal")
            self.new_label_var.set("")
        elif method == "Excel Entry":
            self.old_label_dropdown.config(state="disabled")
            self.old_label_var.set("")
            self.new_label_entry.config(state="disabled")
            self.new_label_var.set("")
            # Prompt the user about the Excel format
            messagebox.showinfo("Excel Format", "Please ensure that the Excel sheet has *old labels* in the first column and *new labels* in the second column with their associated headings. Only available labels will be applied.")

    
    def load_excel_sheet(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if file_path:
            self.excel_file_path_var.set(file_path)
            messagebox.showinfo("Excel Sheet Loaded", f"Excel sheet loaded:\n{file_path}")
            messagebox.showinfo("Loading Label Changes", "Please wait for label changes mapping to show")
    
            try:
                excel_data = pd.read_excel(file_path)
                old_labels = excel_data.iloc[:, 0].astype(int)
                new_labels = excel_data.iloc[:, 1].astype(int)
    
                # Get cumulative unique labels across all loaded point clouds
                cumulative_available_labels = self.get_unique_labels_cumulative()
    
                # Filter label changes to include only those that match cumulative available labels
                valid_label_changes = [(old, new) for old, new in zip(old_labels, new_labels) if old in cumulative_available_labels]
    
                # Display only valid label changes in the GUI
                changes_str = "\n".join([f"Change {i+1}: Old Label {old} to New Label {new}"
                                        for i, (old, new) in enumerate(valid_label_changes)])
                self.label_changes_var.set(changes_str)
    
                # Update the label_changes list with valid label changes
                self.label_changes = valid_label_changes
    
                # Update the dropdown menu with available old labels
                menu = self.old_label_dropdown["menu"]
                menu.delete(0, "end")
                for label in cumulative_available_labels:
                    menu.add_command(label=label, command=lambda l=label: self.old_label_var.set(l))
    
            except Exception as e:
                messagebox.showerror("Error", f"Error reading Excel file: {e}")

    
    def open_point_cloud(self):
        file_path = filedialog.askopenfilename(filetypes=[("Point Cloud Files", "*.las;*.laz")])
        if file_path:
            self.file_path = file_path
            self.point_cloud = self.read_point_cloud(file_path)

            # Check the selected processing method
            if self.processing_method == "Single":
                # Show available labels for the single selected file
                messagebox.showinfo("Loading Available Labels", "Please wait for the Availabel Labels to be loaded")
                labels = self.get_unique_labels_single_file()
            elif self.processing_method == "Batch":
                # Show the cumulative available labels for all files
                messagebox.showinfo("Loading Available Labels", "Please wait for the Availabel Labels across all files to be loaded")
                labels = self.get_unique_labels_cumulative()

            label_str = '\n'.join(map(str, labels))
            self.available_labels_var.set(label_str)

            # Update the dropdown menu with available labels
            menu = self.old_label_dropdown["menu"]
            menu.delete(0, "end")
            for label in labels:
                menu.add_command(label=label, command=lambda l=label: self.old_label_var.set(l))

            messagebox.showinfo("Available Labels", f"Available labels:\n{label_str}") 
            
    def get_unique_labels_single_file(self):
            if self.point_cloud is not None:
                return np.unique(self.point_cloud[:, -1]).astype(int)
            else:
                return []
            
    def get_unique_labels_cumulative(self):
            # Get unique labels across all loaded point clouds
            unique_labels_set = set()
            for original_ptcloud_path in self.get_loaded_files():
                original_ptcloud = laspy.read(original_ptcloud_path)
                current_labels = np.unique(original_ptcloud.Ext_Class).astype(int)
                unique_labels_set.update(current_labels)
            return sorted(list(unique_labels_set))

    def get_loaded_files(self):
            # Returns the list of loaded point cloud files (used for batch processing)
            return [self.file_path] if self.processing_method == "Single" else glob.glob(os.path.join(os.path.dirname(self.file_path), '*.laz'))

    def update_available_labels(self):
        if self.processing_method == "Single":
            labels = self.get_unique_labels_single_file()
        elif self.processing_method == "Batch":
            labels = self.get_unique_labels_cumulative()
        else:
            labels = []
    
        label_str = '\n'.join(map(str, labels))
        self.available_labels_var.set(label_str)
    
        # Update the dropdown menu with available labels
        menu = self.old_label_dropdown["menu"]
        menu.delete(0, "end")
        for label in labels:
            menu.add_command(label=label, command=lambda l=label: self.old_label_var.set(l))

    def add_label_change(self):
        method = self.label_change_method_var.get()
        if method == "Manual Entry":
            # Manual entry logic
            old_label = self.old_label_var.get()
            new_label = self.new_label_var.get()
        elif method == "Excel Entry":
            # Excel entry logic
            file_path = self.excel_file_path_var.get()
            if not file_path:
                messagebox.showerror("Error", "Please provide an Excel file.")
                return
    
            # Read the Excel file and extract label changes
            try:
                excel_data = pd.read_excel(file_path)
                old_labels = excel_data.iloc[:, 0].astype(int)
                new_labels = excel_data.iloc[:, 1].astype(int)
    
                # Filter label changes to include only available labels
                available_labels = self.get_unique_labels()
                valid_label_changes = [(old, new) for old, new in zip(old_labels, new_labels) if old in available_labels]
    
                # Display label changes in the GUI
                changes_str = "\n".join([f"Change {i+1}: Old Label {old} to New Label {new}"
                                        for i, (old, new) in enumerate(valid_label_changes)])
                self.label_changes_var.set(changes_str)
    
                # Update the label_changes list with valid label changes
                self.label_changes = valid_label_changes
    
            except Exception as e:
                messagebox.showerror("Error", f"Error reading Excel file: {e}")
                return
    
        # Add new label change mapping to the list
        old_label = self.old_label_var.get()
        new_label = self.new_label_var.get()
    
        if old_label and new_label:
            self.label_changes.append((old_label, new_label))
    
            # Update the label_changes_var to display the entered mappings
            changes_str = "\n".join([f"Change {i + 1}: Old Label {old} to New Label {new}"
                                    for i, (old, new) in enumerate(self.label_changes)])
            self.label_changes_var.set(changes_str)
    
            # Clear the entry fields for the next mapping
            self.old_label_var.set("")
            self.new_label_var.set("")
    
    def read_point_cloud(self, file_path):
        return self.readPtcloud(file_path)

    def readPtcloud(self, file_path):
        L = laspy.read(file_path)
        # Extracting X, Y, Z, Intensity, and Ext_Class
        ptcloud = np.array((L.x, L.y, L.z, L.intensity, L.Ext_Class)).transpose()
        return ptcloud

    def read_Original_Ptcloud(self, file_path):
        LL = laspy.read(file_path)
        originalptcloud = np.array((LL.x, LL.y, LL.z, LL.intensity, LL.return_number, LL.number_of_returns, LL.scan_direction_flag, LL.edge_of_flight_line, LL.classification, LL.user_data, LL.point_source_id, LL.gps_time, LL.red, LL.green, LL.blue)).transpose()
        return originalptcloud

    def get_unique_labels(self):
        if self.point_cloud is not None:
            return np.unique(self.point_cloud[:, -1]).astype(int)
        else:
            return []
        
    def change_label(self):
        if self.point_cloud is not None:
            try:
                if self.label_changes:
                    if self.processing_method == "Single":
                        self.process_single_method()
                    elif self.processing_method == "Batch":
                        self.process_batch_method()
                        messagebox.showinfo("Label Change", f"{len(self.label_changes)} label changes applied to all files. Point cloud saved.")
                        return  # Stop further execution after processing batch method
                    else:
                        print("Processing method not selected")
    
                    for i, (old_label, new_label) in enumerate(self.label_changes, start=1):
                        try:
                            old_label = int(old_label)
                            new_label = int(new_label)
                        except ValueError:
                            messagebox.showerror("Error", "Invalid label format. Please enter valid integers.")
                            return
    
                        if old_label not in self.get_unique_labels():
                            messagebox.showerror("Error", f"Selected label {old_label} does not exist.")
                            return
    
                        mask = self.point_cloud[:, -1] == old_label
                        self.point_cloud[mask, -1] = new_label
    
                
                # Save the updated point cloud
                file_path, _ = os.path.splitext(self.file_path)  # Get the file path without extension
                save_path = filedialog.asksaveasfilename(defaultextension=".laz",
                                                            filetypes=[("LAS Files", "*.laz")],
                                                            initialfile=f"{file_path}_updated.laz")
                if save_path:
                    self.write_las(save_path, self.point_cloud)
                    messagebox.showinfo("Label Change", f"{len(self.label_changes)} label changes applied. Point cloud saved.")
                else:
                    messagebox.showwarning("Warning", "Save operation canceled. Point cloud reverted.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid labels.")
    
                # Update available labels after saving the point cloud
                self.update_available_labels()
    
        elif self.label_changes:
            for i, (old_label, new_label) in enumerate(self.label_changes, start=1):
                try:
                    old_label = int(old_label)
                    new_label = int(new_label)
                except ValueError:
                    messagebox.showerror("Error", "Invalid label format. Please enter valid integers.")
                    return
    
                if old_label not in self.get_unique_labels():
                    messagebox.showerror("Error", f"Selected label {old_label} does not exist.")
                    return
    
                mask = self.point_cloud[:, -1] == old_label
                self.point_cloud[mask, -1] = new_label
    
            # Update available labels after label changes
            self.update_available_labels()
    
        # except ValueError:
        #     messagebox.showerror("Error", "Invalid input. Please enter valid labels.")


    def write_las(self, file_path, point_cloud):
        # Read the original LAS file
        original_ptcloud_path = self.file_path  
        original_ptcloud = laspy.read(original_ptcloud_path)
    
        # Iterate through the list of label changes
        for old_label, new_label in self.label_changes:
            print(f"Attempting to change label: {old_label} to {new_label}")
    
            try:
                old_label = int(old_label)
                new_label = int(new_label)
            except ValueError:
                print("Invalid label format.")
                messagebox.showerror("Error", "Invalid label format. Please enter valid labels.")
                return
    
            print(f"Converted labels to int: {old_label} to {new_label}")
    
            # Check if the old label exists
            available_labels = self.get_unique_labels()
            print(f"Available labels: {available_labels}")
    
            # Modify the Ext_Class field
            mask = original_ptcloud.Ext_Class == old_label  
            original_ptcloud.Ext_Class[mask] = new_label
            
            
        # Save the updated point cloud with new labels
        file_path, _ = os.path.splitext(self.file_path)
        updated_file_path = f"{file_path}_updated.laz"
        original_ptcloud.write(updated_file_path)
    
        # Writing out the new point cloud
        out_las = laspy.create(file_version="1.4", point_format=7)
        out_las.header.offset = [original_ptcloud.x.min(), original_ptcloud.y.min(), original_ptcloud.z.min()]
        out_las.header.scale = [0.1, 0.1, 0.1]
        out_las.x = original_ptcloud.x
        out_las.y = original_ptcloud.y
        out_las.z = original_ptcloud.z
        out_las.intensity = original_ptcloud.intensity
        out_las.red = original_ptcloud.red
        out_las.green = original_ptcloud.green
        out_las.blue = original_ptcloud.blue
        out_las.gps_time = original_ptcloud.gps_time
        out_las.classification = original_ptcloud.classification
        out_las.Ext_Class = original_ptcloud.Ext_Class  
        
    
        # Ensure that 'Ext_Class' attribute is available in 'point_cloud'
        if 'Ext_Class' in original_ptcloud.point_format.dimension_names:
            ext_class_index = list(original_ptcloud.point_format.dimension_names).index('Ext_Class')
            if ext_class_index < point_cloud.shape[1]:
                out_las.Ext_Class = point_cloud[:, ext_class_index]
#%% Function for Single / Batch Process
    #Single Processing
    def process_single_method(self):
        print("Processing Single method")
        # Logic for the "Single" processing method
    
    ########Batch Processing #######
    def process_batch_method(self):
       print("Processing Batch method")
       # Logic for the "Batch" processing method
       directory = os.path.dirname(self.file_path)
       file_pattern = os.path.join(directory, '*.laz')
       files = glob.glob(file_pattern)
       
       # # Initialize a set to store unique labels across all files
       # unique_labels_set = set()

       for original_ptcloud_path in files:
           #Read each point cloud file
           original_ptcloud = laspy.read(original_ptcloud_path)
           # # Get unique labels in the current point cloud file
           # current_labels = np.unique(original_ptcloud.Ext_Class).astype(int)
           
           # # Add unique labels to the set
           # unique_labels_set.update(current_labels)

           # Apply label changes to each point cloud
           self.batch_label_change_save(original_ptcloud, original_ptcloud_path)

       # # Convert the set of unique labels to a sorted list
       # unique_labels_list = sorted(list(unique_labels_set))

       # # Update the available labels in the GUI
       # self.available_labels_var.set("\n".join(map(str, unique_labels_list)))           
                
    def batch_label_change_save(self, original_ptcloud, file_path):            
        # Iterate through the list of label changes
        
        for old_label, new_label in self.label_changes:
            print(f"Attempting to change label: {old_label} to {new_label}")
    
            try:
                old_label = int(old_label)
                new_label = int(new_label)
            except ValueError:
                print("Invalid label format.")
                messagebox.showerror("Error", "Invalid label format. Please enter valid labels.")
                return
    
            print(f"Converted labels to int: {old_label} to {new_label}")
    
            # Check if the old label exists
            available_labels = self.get_unique_labels()
            print(f"Available labels: {available_labels}")
    
            # Modify the Ext_Class field
            mask = original_ptcloud.Ext_Class == old_label  
            original_ptcloud.Ext_Class[mask] = new_label
    
        # Save the updated point cloud with new labels
        file_path, _ = os.path.splitext(file_path)
        updated_file_path = f"{file_path}_updated.laz"
        original_ptcloud.write(updated_file_path)
    
        # Writing out the new point cloud
        out_las = laspy.create(file_version="1.4", point_format=7)
        out_las.header.offset = [original_ptcloud.x.min(), original_ptcloud.y.min(), original_ptcloud.z.min()]
        out_las.header.scale = [0.1, 0.1, 0.1]
        out_las.x = original_ptcloud.x
        out_las.y = original_ptcloud.y
        out_las.z = original_ptcloud.z
        out_las.intensity = original_ptcloud.intensity
        out_las.red = original_ptcloud.red
        out_las.green = original_ptcloud.green
        out_las.blue = original_ptcloud.blue
        out_las.gps_time = original_ptcloud.gps_time
        out_las.classification = original_ptcloud.classification
        out_las.Ext_Class = original_ptcloud.Ext_Class
        
        
        
#%% 

if __name__ == "__main__":
    root = tk.Tk()
    app = PointCloudLabelChanger(root)
    root.mainloop()
