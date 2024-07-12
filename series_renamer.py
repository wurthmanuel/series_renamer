import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
import re
from typing import List, Tuple


class SeriesRenamer:
    def __init__(self, inner_root: tk.Tk):
        self.season_vars = []
        self.root = inner_root
        self.selected_directory = ""
        self.root.title("Series Renamer")
        self.root.geometry("1000x800")

        # Main frame for the two sections
        self.main_frame = ttk.Frame(inner_root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # PanedWindow for equally sized sections
        self.paned_window = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Files frame
        self.files_frame = ttk.Frame(self.paned_window, borderwidth=2, relief="groove", width=500, height=600)
        self.files_frame.pack_propagate(False)  # Prevents automatic resizing
        self.paned_window.add(self.files_frame)

        self.import_button = ttk.Button(self.files_frame, text="Import Files", command=self.import_files)
        self.import_button.pack(pady=5)

        self.files_listbox_frame = ttk.Frame(self.files_frame)
        self.files_listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.files_listbox = tk.Listbox(self.files_listbox_frame, selectmode=tk.MULTIPLE)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.files_scrollbar = ttk.Scrollbar(self.files_listbox_frame, orient=tk.VERTICAL,
                                             command=self.files_listbox.yview)
        self.files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.files_listbox.config(yscrollcommand=self.files_scrollbar.set)

        # Horizontal frame for button and label (files)
        self.files_button_frame = ttk.Frame(self.files_frame)
        self.files_button_frame.pack(pady=5)

        self.remove_files_button = ttk.Button(self.files_button_frame, text="Remove Selected Files",
                                              command=self.remove_selected_files, state=tk.DISABLED)
        self.remove_files_button.pack(side=tk.LEFT, padx=5)

        # Button to clear files list
        self.clear_files_button = ttk.Button(self.files_button_frame, text="Clear Files List",
                                             command=self.clear_files_list, state=tk.DISABLED)
        self.clear_files_button.pack(side=tk.LEFT, padx=5)

        # Label for selected files
        self.files_selection_label = tk.Label(self.files_button_frame, text="", fg="grey")
        self.files_selection_label.pack(side=tk.LEFT, padx=5)

        # Number of items in the left list
        self.files_count_label = tk.Label(self.files_frame, text="0 items", fg="grey")
        self.files_count_label.pack(side=tk.BOTTOM, pady=5)

        # Episodes frame
        self.episodes_frame = ttk.Frame(self.paned_window, borderwidth=2, relief="groove", width=500, height=600)
        self.episodes_frame.pack_propagate(False)  # Prevents automatic resizing
        self.paned_window.add(self.episodes_frame)

        self.search_frame = ttk.Frame(self.episodes_frame)
        self.search_frame.pack(pady=5, fill=tk.X)

        self.search_label = ttk.Label(self.search_frame, text="Series Name:")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.series_name_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.series_name_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.search_series)  # Bind the Enter key to search_series

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_series)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.episodes_listbox_frame = ttk.Frame(self.episodes_frame)
        self.episodes_listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.episodes_listbox = tk.Listbox(self.episodes_listbox_frame, selectmode=tk.MULTIPLE)
        self.episodes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.episodes_scrollbar = ttk.Scrollbar(self.episodes_listbox_frame, orient=tk.VERTICAL,
                                                command=self.episodes_listbox.yview)
        self.episodes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.episodes_listbox.config(yscrollcommand=self.episodes_scrollbar.set)

        # Horizontal frame for button and label (episodes)
        self.episodes_button_frame = ttk.Frame(self.episodes_frame)
        self.episodes_button_frame.pack(pady=5)

        self.remove_episodes_button = ttk.Button(self.episodes_button_frame, text="Remove Selected Episodes",
                                                 command=self.remove_selected_episodes, state=tk.DISABLED)
        self.remove_episodes_button.pack(side=tk.LEFT, padx=5)

        # Button to clear episodes list
        self.clear_episodes_button = ttk.Button(self.episodes_button_frame, text="Clear Episodes List",
                                                command=self.clear_episodes_list, state=tk.DISABLED)
        self.clear_episodes_button.pack(side=tk.LEFT, padx=5)

        # Label for selected episodes
        self.episodes_selection_label = tk.Label(self.episodes_button_frame, text="", fg="grey")
        self.episodes_selection_label.pack(side=tk.LEFT, padx=5)

        # Number of items in the right list
        self.episodes_count_label = tk.Label(self.episodes_frame, text="0 items", fg="grey")
        self.episodes_count_label.pack(side=tk.BOTTOM, pady=5)

        # Frame for the button and the hint text
        self.bottom_frame = ttk.Frame(inner_root)
        self.bottom_frame.pack(fill=tk.X, pady=5)

        # Inner frame for button and hint text
        self.bottom_inner_frame = ttk.Frame(self.bottom_frame)
        self.bottom_inner_frame.pack(fill=tk.BOTH, expand=True)

        # Button to start renaming
        self.rename_button = ttk.Button(self.bottom_inner_frame, text="Preview renaming", command=self.preview_renaming,
                                        state=tk.DISABLED)
        self.rename_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Hint text
        self.hint_label = tk.Label(self.bottom_inner_frame, text="nothing to rename", fg="gray")
        self.hint_label.pack(side=tk.RIGHT, padx=10)

        self.files_listbox.bind("<<ListboxSelect>>", self.check_lists)
        self.episodes_listbox.bind("<<ListboxSelect>>", self.check_lists)
        self.files_listbox.bind("<<ListboxSelect>>", self.update_file_selection)
        self.episodes_listbox.bind("<<ListboxSelect>>", self.update_episode_selection)

        # Ensure both sides grow evenly
        self.paned_window.paneconfig(self.files_frame, stretch="always")
        self.paned_window.paneconfig(self.episodes_frame, stretch="always")

    def clear_files_list(self):
        self.files_listbox.delete(0, tk.END)
        self.check_lists()
        self.update_file_selection()

    def clear_episodes_list(self):
        self.episodes_listbox.delete(0, tk.END)
        self.check_lists()
        self.update_episode_selection()

    def check_lists(self, _=None):
        files_count = self.files_listbox.size()
        episodes_count = self.episodes_listbox.size()

        self.files_count_label.config(text=f"{files_count} items")
        self.episodes_count_label.config(text=f"{episodes_count} items")

        if files_count == 0 and episodes_count == 0:
            self.hint_label.config(text="nothing to rename", fg="gray")
            self.clear_files_button.config(state=tk.DISABLED)
            self.clear_episodes_button.config(state=tk.DISABLED)
        elif files_count > 0 and episodes_count == 0:
            self.hint_label.config(text="please fetch show titles", fg="gray")
            self.clear_files_button.config(state=tk.NORMAL)
            self.clear_episodes_button.config(state=tk.DISABLED)
        elif files_count == 0 and episodes_count > 0:
            self.hint_label.config(text="please add local files", fg="gray")
            self.clear_files_button.config(state=tk.DISABLED)
            self.clear_episodes_button.config(state=tk.NORMAL)
        elif files_count != episodes_count:
            self.hint_label.config(text="can't match lists", fg="red")
            self.clear_files_button.config(state=tk.NORMAL)
            self.clear_episodes_button.config(state=tk.NORMAL)
        else:
            self.hint_label.config(text="ready to rename", fg="green")
            self.rename_button.config(state=tk.NORMAL)
            self.clear_files_button.config(state=tk.NORMAL)
            self.clear_episodes_button.config(state=tk.NORMAL)

        if files_count == episodes_count and files_count > 0:
            self.hint_label.config(text="ready to rename", fg="green")
            self.rename_button.config(state=tk.NORMAL)
        else:
            self.rename_button.config(state=tk.DISABLED)

    def preview_renaming(self):
        # Ensure both lists have the same number of entries
        if self.files_listbox.size() != self.episodes_listbox.size():
            messagebox.showerror("Error", "The number of files and episodes do not match.")
            return

        log_lines = []
        old_new_names = []
        for i in range(self.files_listbox.size()):
            # Old name
            old_name = self.files_listbox.get(i).split('. ', 1)[1]

            # New name
            episode_title = self.episodes_listbox.get(i).split('. ', 1)[1]
            file_extension = os.path.splitext(old_name)[1]
            new_name = f"{episode_title}{file_extension}"

            # Log line
            log_lines.append(f"{old_name} -> {new_name}")
            old_new_names.append((old_name, new_name))

        # Show the preview window
        self.show_preview_window(old_new_names)

    def show_preview_window(self, old_new_names: List[Tuple[str, str]]):
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Renaming")
        preview_window.geometry("1000x400")

        frame = ttk.Frame(preview_window)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=("Old filename", "New filename"), show="headings")
        tree.heading("Old filename", text="Old Name")
        tree.heading("New filename", text="New Name")
        tree.column("Old filename", width=300)
        tree.column("New filename", width=300)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        for old_name, new_name in old_new_names:
            tree.insert("", tk.END, values=(old_name, new_name))

        button_frame = ttk.Frame(preview_window)
        button_frame.pack(fill=tk.X)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=preview_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

        start_button = ttk.Button(button_frame, text="Start Renaming",
                                  command=lambda: self.execute_renaming(old_new_names, preview_window))
        start_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def execute_renaming(self, old_new_names: List[Tuple[str, str]], preview_window: tk.Toplevel):
        def sanitize_filename(filename: str) -> str:
            # Remove invalid characters for Windows filenames
            return re.sub(r'[<>:"/\\|?*]', '', filename)

        directory_path = self.selected_directory
        if not directory_path:
            messagebox.showinfo("Info", "No directory selected.")
            return

        for old_name, new_name in old_new_names:
            old_file_path = os.path.join(directory_path, old_name)
            new_file_path = os.path.join(directory_path, sanitize_filename(new_name))

            # Check if the new file name already exists
            if os.path.exists(new_file_path):
                messagebox.showerror("Error", f"File {new_name} already exists. Renaming aborted.")
                return

            # Rename the file
            os.rename(old_file_path, new_file_path)

        messagebox.showinfo("Success", "Files have been renamed successfully.")
        preview_window.destroy()

    def search_series(self, _=None):
        series_name = self.series_name_var.get()
        if not series_name:
            messagebox.showerror("Error", "Please enter a series name")
            return

        # Fetch series episodes from the internet
        self.fetch_episodes(series_name)

    def fetch_episodes(self, series_name: str):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.3'}
            url = f"https://api.tvmaze.com/search/shows?q={series_name}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            series_data = response.json()
            if not series_data:
                messagebox.showerror("Error", "Series not found")
                return

            series_list = [
                {
                    "name": item["show"]["name"],
                    "language": item["show"]["language"],
                    "seasons": len(requests.get(f"https://api.tvmaze.com/shows/{item['show']['id']}/seasons").json()),
                    "episodes": len(requests.get(f"https://api.tvmaze.com/shows/{item['show']['id']}/episodes").json()),
                    "premiered": item["show"]["premiered"],
                    "id": item["show"]["id"]
                } for item in series_data
            ]
            self.select_series(series_list)
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching episodes: {str(e)}")

    def select_series(self, series_list: List[dict]):
        series_window = tk.Toplevel(self.root)
        series_window.title("Select Series")
        series_window.geometry("900x400")

        frame = ttk.Frame(series_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Define the columns to be displayed
        columns = ("Name", "Language", "Seasons", "Episodes", "Premiered", "ID")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        # Set the column headings and widths
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column("Name", width=200)
        tree.column("Premiered", width=100)
        tree.column("ID", width=50)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # Insert the data into the treeview
        for series in series_list:
            name = series["name"]
            language = series["language"]
            seasons = series["seasons"]
            episodes = series["episodes"]
            premiered = series["premiered"]
            series_id = series["id"]
            tree.insert("", tk.END, values=(name, language, seasons, episodes, premiered, str(series_id)))

        def on_select():
            selected_items = tree.selection()
            if selected_items:
                selected_item = selected_items[0]  # always use the first element
                selected_series = tree.item(selected_item)["values"]
                inner_series_id = selected_series[5]
                self.get_episode_list(inner_series_id)
                series_window.destroy()

        button_frame = ttk.Frame(series_window)
        button_frame.pack(fill=tk.X)

        select_button = ttk.Button(button_frame, text="Select", command=on_select)
        select_button.pack(side=tk.RIGHT, padx=5, pady=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=series_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Set the window as modal
        series_window.grab_set()
        series_window.focus_set()
        series_window.transient(self.root)

        def on_close():
            series_window.grab_release()
            series_window.destroy()

        series_window.protocol("WM_DELETE_WINDOW", on_close)

        # Update the window layout and set its size based on the content
        series_window.update_idletasks()
        width = series_window.winfo_width()
        height = series_window.winfo_height()
        series_window.geometry(f"{width}x{height}")

        self.root.wait_window(series_window)

    def get_episode_list(self, series_id: str):
        self.get_season_list(series_id)

    def get_season_list(self, series_id: str):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.3'}
            url = f"https://api.tvmaze.com/shows/{series_id}/seasons"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            seasons = response.json()
            if not seasons:
                messagebox.showerror("Error", "No seasons found")
                return

            seasons_window = tk.Toplevel(self.root)
            seasons_window.title("Select Seasons")

            frame = ttk.Frame(seasons_window)
            frame.pack(fill=tk.BOTH, expand=True)

            # Clear previous season variables
            self.season_vars.clear()

            for season in seasons:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(frame, text=f"Season {season['number']}", variable=var)
                chk.pack(anchor=tk.W)
                self.season_vars.append((season['id'], var))

            button_frame = ttk.Frame(seasons_window)
            button_frame.pack(fill=tk.X)

            select_button = ttk.Button(button_frame, text="Fetch Episodes",
                                       command=lambda: self.fetch_selected_seasons(seasons_window))
            select_button.pack(side=tk.RIGHT, padx=5, pady=5)

            cancel_button = ttk.Button(button_frame, text="Cancel", command=seasons_window.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

            # Set the window as modal
            seasons_window.grab_set()
            seasons_window.focus_set()
            seasons_window.transient(self.root)

            def on_close():
                seasons_window.grab_release()
                seasons_window.destroy()

            seasons_window.protocol("WM_DELETE_WINDOW", on_close)

            # Update the window layout and set its size based on the content
            seasons_window.update_idletasks()
            width = 300
            height = seasons_window.winfo_height()
            seasons_window.geometry(f"{width}x{height}")

            self.root.wait_window(seasons_window)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def fetch_selected_seasons(self, seasons_window: tk.Toplevel):
        selected_seasons = [season_id for season_id, var in self.season_vars if var.get()]
        if not selected_seasons:
            messagebox.showerror("Error", "Please select at least one season")
            return

        # Clear the episodes listbox before adding new episodes
        self.episodes_listbox.delete(0, tk.END)

        for season_id in selected_seasons:
            self.get_episodes_by_season(season_id)

        seasons_window.destroy()
        self.check_lists()

    def get_episodes_by_season(self, season_id: str):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.3'}
            url = f"https://api.tvmaze.com/seasons/{season_id}/episodes"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            episodes = response.json()
            if not episodes:
                messagebox.showerror("Error", "No episodes found for the selected season")
                return

            for index, ep in enumerate(episodes, start=self.episodes_listbox.size() + 1):
                season = ep.get('season')
                episode = ep.get('number')
                episode_name = ep.get('name')

                # Ensure season, episode, and episode_name are not None
                if season is None:
                    season = 0
                if episode is None:
                    episode = 0
                if episode_name is None:
                    episode_name = "Unknown Episode"

                self.episodes_listbox.insert(tk.END, f"{index}. S{season:02d}E{episode:02d} - {episode_name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_files(self):
        file_paths = filedialog.askopenfilenames()
        if not file_paths:
            return

        self.selected_directory = os.path.dirname(file_paths[0])
        file_names = sorted([os.path.basename(path) for path in file_paths])
        self.files_listbox.delete(0, tk.END)
        for index, file_name in enumerate(file_names, start=1):
            self.files_listbox.insert(tk.END, f"{index}. {file_name}")
        self.check_lists()  # Checks if the lists are the same size

    def remove_selected_files(self):
        # Save the current scroll position
        current_scroll_pos = self.files_listbox.yview()

        selected_files = self.files_listbox.curselection()
        for index in reversed(selected_files):
            self.files_listbox.delete(index)
        self.reindex_listbox(self.files_listbox)

        # Restore the scroll position
        self.files_listbox.yview_moveto(current_scroll_pos[0])

        self.check_lists()  # Updates the lists after removing entries
        self.update_file_selection()  # Updates buttons and labels

    def remove_selected_episodes(self):
        # Save the current scroll position
        current_scroll_pos = self.episodes_listbox.yview()

        selected_episodes = self.episodes_listbox.curselection()
        for index in reversed(selected_episodes):
            self.episodes_listbox.delete(index)
        self.reindex_listbox(self.episodes_listbox)

        # Restore the scroll position
        self.episodes_listbox.yview_moveto(current_scroll_pos[0])

        self.check_lists()  # Updates the lists after removing entries
        self.update_episode_selection()  # Updates buttons and labels

    @staticmethod
    def reindex_listbox(listbox: tk.Listbox):
        items = listbox.get(0, tk.END)
        listbox.delete(0, tk.END)
        for index, item in enumerate(items, start=1):
            # Remove the old index number and add the new one
            new_item = f"{index}. {item.split('. ', 1)[1]}"
            listbox.insert(tk.END, new_item)

    def update_file_selection(self, _=None):
        selected_files = self.files_listbox.curselection()
        count = len(selected_files)
        if count > 0:
            self.remove_files_button.config(state=tk.NORMAL)
            self.files_selection_label.config(text=f"{count} items selected")
        else:
            self.remove_files_button.config(state=tk.DISABLED)
            self.files_selection_label.config(text="")

    def update_episode_selection(self, _=None):
        selected_episodes = self.episodes_listbox.curselection()
        count = len(selected_episodes)
        if count > 0:
            self.remove_episodes_button.config(state=tk.NORMAL)
            self.episodes_selection_label.config(text=f"{count} items selected")
        else:
            self.remove_episodes_button.config(state=tk.DISABLED)
            self.episodes_selection_label.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = SeriesRenamer(root)
    root.mainloop()
