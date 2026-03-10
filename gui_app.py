import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import copy
import csv
import os

# Import core scheduling functions from the existing script
from powergrid_visit_scheduler import generate_schedule, DEFAULT_INCHARGES, DEFAULT_PROJECTS

class SchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PowerGrid Visit Scheduler")
        self.geometry("950x700")
        
        # Apply a modern styling via ttk
        self.style = ttk.Style(self)
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
            
        # Configure common fonts & styles
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("TButton", padding=5, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))

        # Application state
        # Use deepcopy so we don't accidentally mutate the module defaults
        self.incharges = copy.deepcopy(DEFAULT_INCHARGES)
        self.projects = copy.deepcopy(DEFAULT_PROJECTS)
        self.current_project_idx = None
        self.last_schedule = None  # Store last generated schedule for export
        
        self.create_widgets()
        
        # Bind tab change event to update schedule dates automatically
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Initial calculation
        self.auto_fill_schedule_dates()

    def on_tab_changed(self, event):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 2:  # Schedule Tab
            self.auto_fill_schedule_dates()

    def auto_fill_schedule_dates(self, force=False):
        if not self.projects:
            return
            
        valid_starts = [p["start"] for p in self.projects if p.get("start")]
        valid_ends = [p["end"] for p in self.projects if p.get("end")]
        
        if valid_starts and valid_ends:
            calc_start = min(valid_starts)
            calc_end = max(valid_ends)
            
            # Auto fill if empty OR if force is True
            if force or not self.entry_sch_start.get().strip():
                self.entry_sch_start.delete(0, tk.END)
                self.entry_sch_start.insert(0, calc_start.strftime("%Y-%m-%d"))
                
            if force or not self.entry_sch_end.get().strip():
                self.entry_sch_end.delete(0, tk.END)
                self.entry_sch_end.insert(0, calc_end.strftime("%Y-%m-%d"))

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Tabs
        self.tab_supervisors = ttk.Frame(self.notebook)
        self.tab_projects = ttk.Frame(self.notebook)
        self.tab_schedule = ttk.Frame(self.notebook)
        self.tab_export = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_supervisors, text="Supervisors")
        self.notebook.add(self.tab_projects, text="Projects")
        self.notebook.add(self.tab_schedule, text="Generate Schedule")
        self.notebook.add(self.tab_export, text="Export")

        self.build_supervisors_tab()
        self.build_projects_tab()
        self.build_schedule_tab()
        self.build_export_tab()

    # --- Supervisors Tab ---
    def build_supervisors_tab(self):
        # Use a LabelFrame for better sectioning
        outer_frame = ttk.Frame(self.tab_supervisors, padding=20)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        frame = ttk.LabelFrame(outer_frame, text="Manage Supervisors", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        list_container = ttk.Frame(frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Add a scrollbar to the listbox
        self.list_supervisors = tk.Listbox(list_container, width=40, font=("Segoe UI", 10), selectbackground="#0078D7")
        self.list_supervisors.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.list_supervisors.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_supervisors.configure(yscrollcommand=scrollbar.set)

        for i in self.incharges:
            self.list_supervisors.insert(tk.END, i)

        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, pady=10)
        
        # Grid layout for controls for better alignment
        ttk.Label(controls, text="New Supervisor:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        self.entry_sup_name = ttk.Entry(controls, width=30)
        self.entry_sup_name.grid(row=0, column=1, padx=(0, 10), pady=5, sticky=tk.W)

        ttk.Button(controls, text="Add", command=self.add_supervisor, width=10).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(controls, text="Remove Selected", command=self.remove_supervisor).grid(row=0, column=3, padx=5, pady=5)

    def add_supervisor(self):
        name = self.entry_sup_name.get().strip()
        if name and name not in self.incharges:
            self.incharges.append(name)
            self.list_supervisors.insert(tk.END, name)
            self.entry_sup_name.delete(0, tk.END)

    def remove_supervisor(self):
        selection = self.list_supervisors.curselection()
        if selection:
            idx = selection[0]
            name = self.list_supervisors.get(idx)
            self.incharges.remove(name)
            self.list_supervisors.delete(idx)

    # --- Projects Tab ---
    def build_projects_tab(self):
        paned = ttk.PanedWindow(self.tab_projects, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left: Projects list
        left_frame = ttk.LabelFrame(paned, text="Projects Roster", padding=10)
        paned.add(left_frame, weight=1)

        list_container = ttk.Frame(left_frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.list_projects = tk.Listbox(list_container, exportselection=False, font=("Segoe UI", 10), selectbackground="#0078D7")
        self.list_projects.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.list_projects.bind('<<ListboxSelect>>', self.on_project_select)

        p_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.list_projects.yview)
        p_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_projects.configure(yscrollcommand=p_scrollbar.set)

        proj_controls = ttk.Frame(left_frame)
        proj_controls.pack(fill=tk.X)
        ttk.Button(proj_controls, text="New Project", command=self.new_project).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(proj_controls, text="Delete Selected", command=self.delete_project).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Right: Project details
        right_frame = ttk.LabelFrame(paned, text="Project Details", padding=15)
        paned.add(right_frame, weight=3)

        # Detail form
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(fill=tk.X, pady=(0, 15))

        # Use grid spacing
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_proj_name = ttk.Entry(form_frame)
        self.entry_proj_name.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        self.entry_proj_name.bind('<KeyRelease>', lambda e: self.save_current_project_basic())

        ttk.Label(form_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_proj_start = ttk.Entry(form_frame)
        self.entry_proj_start.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        self.entry_proj_start.bind('<FocusOut>', lambda e: self.save_current_project_basic())

        ttk.Label(form_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_proj_end = ttk.Entry(form_frame)
        self.entry_proj_end.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        self.entry_proj_end.bind('<FocusOut>', lambda e: self.save_current_project_basic())

        # Sub-list: Locations separator
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(right_frame, text="Locations associated with project:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        loc_list_container = ttk.Frame(right_frame)
        loc_list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.list_locations = tk.Listbox(loc_list_container, height=6, font=("Segoe UI", 10), selectbackground="#0078D7")
        self.list_locations.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        l_scrollbar = ttk.Scrollbar(loc_list_container, orient="vertical", command=self.list_locations.yview)
        l_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_locations.configure(yscrollcommand=l_scrollbar.set)

        loc_controls = ttk.Frame(right_frame)
        loc_controls.pack(fill=tk.X)
        
        ttk.Label(loc_controls, text="New Loc Name:").grid(row=0, column=0, padx=(0, 5), pady=5)
        self.entry_loc_name = ttk.Entry(loc_controls, width=20)
        self.entry_loc_name.grid(row=0, column=1, padx=(0, 15), pady=5)
        
        ttk.Label(loc_controls, text="Dist (km):").grid(row=0, column=2, padx=(0, 5), pady=5)
        self.entry_loc_dist = ttk.Entry(loc_controls, width=10)
        self.entry_loc_dist.grid(row=0, column=3, padx=(0, 15), pady=5)
        
        ttk.Button(loc_controls, text="Add Location", command=self.add_location).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(loc_controls, text="Remove Selected", command=self.remove_location).grid(row=0, column=5, padx=5, pady=5)

        self.refresh_projects_list()

    def refresh_projects_list(self):
        self.list_projects.delete(0, tk.END)
        for i, p in enumerate(self.projects):
            name = p.get("name", f"Project {i+1}")
            self.list_projects.insert(tk.END, name)

    def on_project_select(self, event):
        selection = self.list_projects.curselection()
        if not selection:
            return
        idx = selection[0]
        self.current_project_idx = idx
        p = self.projects[idx]
        
        self.entry_proj_name.delete(0, tk.END)
        self.entry_proj_name.insert(0, p.get("name", ""))
        
        self.entry_proj_start.delete(0, tk.END)
        start_dt = p.get("start")
        if start_dt:
            self.entry_proj_start.insert(0, start_dt.strftime("%Y-%m-%d"))
            
        self.entry_proj_end.delete(0, tk.END)
        end_dt = p.get("end")
        if end_dt:
            self.entry_proj_end.insert(0, end_dt.strftime("%Y-%m-%d"))

        self.refresh_locations_list()

    def refresh_locations_list(self):
        self.list_locations.delete(0, tk.END)
        if self.current_project_idx is None:
            return
        p = self.projects[self.current_project_idx]
        for loc in p.get("locations", []):
            name = loc.get("name", "")
            dist = loc.get("distance", 0)
            self.list_locations.insert(tk.END, f"{name} (Dist: {dist})")

    def save_current_project_basic(self):
        if self.current_project_idx is None:
            return
        p = self.projects[self.current_project_idx]
        new_name = self.entry_proj_name.get()
        p["name"] = new_name
        
        start_str = self.entry_proj_start.get()
        try:
            if start_str:
                p["start"] = datetime.strptime(start_str, "%Y-%m-%d")
        except ValueError:
            pass # ignore invalid
            
        end_str = self.entry_proj_end.get()
        try:
            if end_str:
                p["end"] = datetime.strptime(end_str, "%Y-%m-%d")
        except ValueError:
            pass
            
        # Update name in listbox without triggering selection event
        self.list_projects.delete(self.current_project_idx)
        self.list_projects.insert(self.current_project_idx, new_name)
        self.list_projects.selection_set(self.current_project_idx)

    def new_project(self):
        new_p = {
            "name": "New Project",
            "start": datetime(2026, 1, 1),
            "end": datetime(2026, 12, 31),
            "locations": []
        }
        self.projects.append(new_p)
        self.refresh_projects_list()
        self.list_projects.selection_set(tk.END)
        self.on_project_select(None)

    def delete_project(self):
        selection = self.list_projects.curselection()
        if not selection:
            return
        idx = selection[0]
        del self.projects[idx]
        self.current_project_idx = None
        
        # clear fields
        self.entry_proj_name.delete(0, tk.END)
        self.entry_proj_start.delete(0, tk.END)
        self.entry_proj_end.delete(0, tk.END)
        self.list_locations.delete(0, tk.END)
        
        self.refresh_projects_list()

    def add_location(self):
        if self.current_project_idx is None:
            return
        name = self.entry_loc_name.get().strip()
        dist_str = self.entry_loc_dist.get().strip()
        
        if not name:
            return
            
        try:
            dist = int(dist_str)
        except ValueError:
            messagebox.showerror("Error", "Distance must be an integer.")
            return
            
        p = self.projects[self.current_project_idx]
        if "locations" not in p:
            p["locations"] = []
            
        p["locations"].append({"name": name, "distance": dist})
        self.entry_loc_name.delete(0, tk.END)
        self.entry_loc_dist.delete(0, tk.END)
        self.refresh_locations_list()

    def remove_location(self):
        if self.current_project_idx is None:
            return
        selection = self.list_locations.curselection()
        if not selection:
            return
        idx = selection[0]
        p = self.projects[self.current_project_idx]
        del p["locations"][idx]
        self.refresh_locations_list()

    # --- Schedule Tab ---
    def build_schedule_tab(self):
        main_frame = ttk.Frame(self.tab_schedule, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top = ttk.LabelFrame(main_frame, text="Generation Parameters", padding=15)
        top.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(top, text="Schedule Start (YYYY-MM-DD):").grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        self.entry_sch_start = ttk.Entry(top, width=15)
        self.entry_sch_start.grid(row=0, column=1, padx=(0, 20), pady=5, sticky=tk.W)
        
        ttk.Label(top, text="Schedule End (YYYY-MM-DD):").grid(row=0, column=2, padx=(0, 10), pady=5, sticky=tk.W)
        self.entry_sch_end = ttk.Entry(top, width=15)
        self.entry_sch_end.grid(row=0, column=3, padx=(0, 20), pady=5, sticky=tk.W)
        
        ttk.Button(top, text="Auto-Calculate Dates", command=lambda: self.auto_fill_schedule_dates(force=True)).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(top, text="Generate Schedule", command=self.do_generate, style="Accent.TButton").grid(row=0, column=5, padx=10, pady=5)

        paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Top area of pane: Treeview for schedule
        tree_frame = ttk.LabelFrame(paned, text="Generated Assignments", padding=10)
        paned.add(tree_frame, weight=3)

        columns = ("Month", "Supervisor", "Location", "Distance (km)", "Week")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=100, width=150, anchor=tk.W)
        self.tree.column("Distance (km)", anchor=tk.E)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        # Bottom area of pane: Treeview for summary statistics
        stat_frame = ttk.LabelFrame(paned, text="Cumulative Distance Summary", padding=10)
        paned.add(stat_frame, weight=1)

        stat_columns = ("Supervisor", "Total Distance (km)")
        self.stat_tree = ttk.Treeview(stat_frame, columns=stat_columns, show="headings", height=5)
        
        for col in stat_columns:
            self.stat_tree.heading(col, text=col)
            self.stat_tree.column(col, minwidth=150, width=200, anchor=tk.W)
        self.stat_tree.column("Total Distance (km)", anchor=tk.E)

        stat_scroll = ttk.Scrollbar(stat_frame, orient="vertical", command=self.stat_tree.yview)
        stat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.stat_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stat_tree.configure(yscrollcommand=stat_scroll.set)

    def do_generate(self):
        # Clear existing trees
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.stat_tree.get_children():
            self.stat_tree.delete(item)
            
        if not self.incharges:
            messagebox.showerror("Error", "No supervisors defined.")
            return

        if not self.projects:
            messagebox.showerror("Error", "No projects defined. Cannot generate a schedule without projects.")
            return
            
        # Ensure dates are populated
        if not self.entry_sch_start.get().strip() or not self.entry_sch_end.get().strip():
            self.auto_fill_schedule_dates(force=True)
            
        try:
            start_dt = datetime.strptime(self.entry_sch_start.get().strip(), "%Y-%m-%d")
            end_dt = datetime.strptime(self.entry_sch_end.get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid schedule date formats. Use YYYY-MM-DD.")
            return
            
        try:
            schedule = generate_schedule(self.incharges, self.projects, start_dt, end_dt)
            self.last_schedule = schedule  # Store for export
            
            # Populate Schedule Treeview
            for month, data in schedule.items():
                if not data:
                    self.tree.insert("", tk.END, values=(month, "No locations", "-", "-", "-"))
                    continue
                
                # Alternate row colors
                for i, a in enumerate(data):
                    tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
                    self.tree.insert("", tk.END, values=(
                        month, 
                        a['incharge'], 
                        a['location'], 
                        a['distance'], 
                        a['week']
                    ), tags=tags)
                    
            self.tree.tag_configure('oddrow', background="#f0f0f0")
            
            # Populate Summary Details
            cum_distances = {i: 0 for i in self.incharges}
            for month, data in schedule.items():
                for a in data:
                    cum_distances[a['incharge']] += a['distance']
                    
            for inc in sorted(self.incharges):
                self.stat_tree.insert("", tk.END, values=(inc, cum_distances[inc]))
                
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            messagebox.showerror("Scheduling Error", f"An error occurred while generating the schedule:\n\n{err}")

    # --- Export Tab ---
    def build_export_tab(self):
        main_frame = ttk.Frame(self.tab_export, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        export_frame = ttk.LabelFrame(main_frame, text="Export Schedule to CSV", padding=20)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_text = (
            "Export the last generated schedule as a CSV file.\n"
            "The CSV is saved to the 'exports' folder in the application root directory.\n"
            "The file is UTF-8 encoded with BOM for seamless import into Microsoft Excel."
        )
        ttk.Label(export_frame, text=info_text, wraplength=700, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))

        # Filename entry
        name_frame = ttk.Frame(export_frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(name_frame, text="File name:").pack(side=tk.LEFT, padx=(0, 10))
        self.entry_export_name = ttk.Entry(name_frame, width=40)
        self.entry_export_name.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_export_name.insert(0, "schedule_export")
        ttk.Label(name_frame, text=".csv").pack(side=tk.LEFT)

        ttk.Button(export_frame, text="Export CSV", command=self.do_export_csv).pack(anchor=tk.W, pady=(0, 10))

        # Status label
        self.export_status = ttk.Label(export_frame, text="", foreground="green")
        self.export_status.pack(anchor=tk.W, pady=(5, 0))

    def do_export_csv(self):
        if not self.last_schedule:
            messagebox.showwarning("No Schedule", "Please generate a schedule first (in the 'Generate Schedule' tab) before exporting.")
            return

        filename = self.entry_export_name.get().strip()
        if not filename:
            filename = "schedule_export"
        if not filename.endswith(".csv"):
            filename += ".csv"

        # Determine exports directory relative to the script location
        app_dir = os.path.dirname(os.path.abspath(__file__))
        exports_dir = os.path.join(app_dir, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        filepath = os.path.join(exports_dir, filename)

        try:
            # Write with UTF-8 BOM so Excel auto-detects encoding
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)

                # Schedule assignments sheet
                writer.writerow(["Month", "Supervisor", "Location", "Distance (km)", "Week"])
                for month, data in self.last_schedule.items():
                    if not data:
                        writer.writerow([month, "No locations", "-", "-", "-"])
                        continue
                    for a in data:
                        writer.writerow([month, a["incharge"], a["location"], a["distance"], a["week"]])

                # Blank separator row
                writer.writerow([])

                # Cumulative distance summary
                writer.writerow(["Cumulative Distance Summary"])
                writer.writerow(["Supervisor", "Total Distance (km)"])
                cum_distances = {i: 0 for i in self.incharges}
                for data in self.last_schedule.values():
                    for a in data:
                        cum_distances[a["incharge"]] += a["distance"]
                for inc in sorted(self.incharges):
                    writer.writerow([inc, cum_distances[inc]])

            self.export_status.config(text=f"✔ Exported successfully to: {filepath}", foreground="green")
        except Exception as e:
            self.export_status.config(text=f"✘ Export failed: {e}", foreground="red")

if __name__ == "__main__":
    app = SchedulerApp()
    app.mainloop()
