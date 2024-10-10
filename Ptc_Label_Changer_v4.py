# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 19:05:25 2023

@author: kenneyke
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import laspy
import numpy as np
import os

class PointCloudLabelChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("Point Cloud Label Changer")

        # Create a menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # Create a file menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Point Cloud", command=self.open_point_cloud)

        # Initialize variables
        self.point_cloud = None
        self.old_label_var = tk.StringVar()
        self.new_label_var = tk.StringVar()
        self.file_path = None

        # Create label selection frame
        self.label_frame = tk.Frame(root, padx=10, pady=10)
        self.label_frame.pack()

        old_label_frame_label = tk.Label(self.label_frame, text="Select old label:")
        old_label_frame_label.grid(row=0, column=0, pady=5)

        # Dropdown button for selecting old label
        self.old_label_dropdown = tk.OptionMenu(self.label_frame, self.old_label_var, *[""])
        self.old_label_dropdown.grid(row=0, column=1, pady=5)
        self.old_label_var.set("")

        new_label_frame_label = tk.Label(self.label_frame, text="Enter new label:")
        new_label_frame_label.grid(row=1, column=0, pady=5)

        self.new_label_entry = tk.Entry(self.label_frame, textvariable=self.new_label_var)
        self.new_label_entry.grid(row=1, column=1, pady=5)

        # Create button to add label change
        add_label_change_button = tk.Button(self.label_frame, text="Add Label Change", command=self.add_label_change)
        add_label_change_button.grid(row=2, column=0, columnspan=2, pady=5)

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

        # Initialize a list to store label change inputs
        self.label_changes = []

    def open_point_cloud(self):
        file_path = filedialog.askopenfilename(filetypes=[("Point Cloud Files", "*.las;*.laz")])
        if file_path:
            self.file_path = file_path
            self.point_cloud = self.read_point_cloud(file_path)
            labels = self.get_unique_labels()
            label_str = '\n'.join(map(str, labels))
            self.available_labels_var.set(label_str)

            # Update the dropdown menu with available labels
            menu = self.old_label_dropdown["menu"]
            menu.delete(0, "end")
            for label in labels:
                menu.add_command(label=label, command=lambda l=label: self.old_label_var.set(l))

            messagebox.showinfo("Available Labels", f"Available labels:\n{label_str}") 
            
    def add_label_change(self):
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
                # Iterate through the list of label changes
                for i, (old_label, new_label) in enumerate(self.label_changes, start=1):
                    # Convert labels to int
                    try:
                        old_label = int(old_label)
                        new_label = int(new_label)
                    except ValueError:
                        messagebox.showerror("Error", "Invalid label format. Please enter valid integers.")
                        return

                    # Check if the old label exists
                    if old_label not in self.get_unique_labels():
                        messagebox.showerror("Error", f"Selected label {old_label} does not exist.")
                        return

                    # Modify the Ext_Class field
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
            mask = np.isclose(original_ptcloud.Ext_Class, old_label)
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

        # Ensure that 'Ext_Class' attribute is available in 'point_cloud'
        if 'Ext_Class' in original_ptcloud.point_format.dimension_names:
            ext_class_index = list(original_ptcloud.point_format.dimension_names).index('Ext_Class')
            if ext_class_index < point_cloud.shape[1]:
                out_las.Ext_Class = point_cloud[:, ext_class_index]


if __name__ == "__main__":
    root = tk.Tk()
    app = PointCloudLabelChanger(root)
    root.mainloop()
