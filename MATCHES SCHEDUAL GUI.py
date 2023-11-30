import tkinter as tk
from tkinter import ttk
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import messagebox
from tkinter import *
from tkinter import PhotoImage
import os
from PIL import Image, ImageTk
import pytz
from datetime import datetime, timedelta
from tkcalendar import Calendar

class MatchScheduleGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Match Schedule")
        self.root.geometry("800x600")
        self.root.configure(bg="#241244")
        self.style = ttk.Style() # create the style object here

        # Load logo image
        self.logo_image = self.load_logo("logo2023.png")
        if self.logo_image:
            # Set the width and height of the logo
            self.logo_image = self.logo_image.subsample(2)
            self.logo_label = ttk.Label(self.root, image=self.logo_image, background=self.root.cget("background"))
            # Set the background of the label to match the background of the parent frame
            self.logo_label.place(anchor="nw")
        
        
        self.selected_date = tk.StringVar()
        self.selected_date.set(pd.Timestamp.today().strftime("%Y-%m-%d"))
        # Add delete button
        img_delete = Image.open("delete.png")
        img_delete = img_delete.resize((100, 40))
        icon_delete = ImageTk.PhotoImage(img_delete)
        
        # Define functions to handle the hover events for the search button
        def on_enter(e):
            self.delete_button.config(bg='red')

        def on_leave(e):
            self.delete_button.config(bg='white')
            
        def on_enter_search(e):
            self.pick_button.config(bg='yellow')

        def on_leave_search(e):
            self.pick_button.config(bg='white')

        def on_enter_export(e):
            self.export_button.config(bg='blue')

        def on_leave_export(e):
            self.export_button.config(bg='white')

        img_pick = Image.open("pickdate.png")
        img_pick = img_pick.resize((100, 40))  # resize the image as needed
        icon_pick = ImageTk.PhotoImage(img_pick)
        
        # Create the search button with an icon and a command, and place it on the GUI
        self.pick_button = tk.Button(self.root, image=icon_pick, command=self.search_matches, relief=FLAT)
        self.pick_button.image = icon_pick
        self.pick_button.place(relx=0.4, rely=0.15, anchor=tk.CENTER)
        # Bind the hover events to the search button
        self.pick_button.bind("<Enter>", on_enter_search)
        self.pick_button.bind("<Leave>", on_leave_search)
        
        # Create the delete button with an icon and a command, and place it on the GUI
        self.delete_button = tk.Button(self.root, image=icon_delete, command=self.delete_matches, relief=FLAT)
        self.delete_button.image = icon_delete
        self.delete_button.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
        # Bind the hover events to the export button
        self.delete_button.bind("<Enter>", on_enter)
        self.delete_button.bind("<Leave>", on_leave)
        
        img_export = Image.open("export.png")
        img_export = img_export.resize((100, 40))
        icon_export = ImageTk.PhotoImage(img_export)
        # Create the export button with an icon and a command, and place it on the GUI
        self.export_button = tk.Button(self.root, image=icon_export, command=self.export_data, relief=FLAT)
        self.export_button.image = icon_export
        self.export_button.place(relx=0.6, rely=0.15, anchor=tk.CENTER)
        # Bind the hover events to the export button
        self.export_button.bind("<Enter>", on_enter_export)
        self.export_button.bind("<Leave>", on_leave_export)

        self.matches_frame = ttk.Treeview(self.root, columns=("Championship", "Host", "Guest", "Match Time", "Score", "Status", "Channel", "Round"), show="headings")
        self.matches_frame.pack_propagate(False)

        
        # Sets the font of the text in the Treeview widget to "Cairo" with a size of 10.
        self.style.configure("Treeview", font=("Cairo", 10))

        # Sets the foreground (text) color of selected rows in the Treeview widget to white.
        self.style.map("Treeview", foreground=[("selected", "white")])

        # Sets the font of the headings in the Treeview widget to "Cairo" with a size of 12 and a bold weight.
        self.style.configure("Treeview.Heading", font=("Times", 12, "bold"))

        # Sets the background color of even rows in the Treeview widget to a light gray color.
        self.style.configure("Treeview.EvenRow", background="#F0F0F0")

        # Sets the background color of odd rows in the Treeview widget to white.
        self.style.configure("Treeview.OddRow", background="white")

        # Sets the overall background color of the Treeview widget to a blue color.
        self.style.configure("Treeview", background="#0078d7")

        # Sets the overall foreground (text) color of the Treeview widget to white.
        self.style.configure("Treeview", foreground="white")

        # Sets the overall theme of the style to "clam", which is a pre-defined theme in the ttk module of Python's standard library.
        self.style.theme_use("xpnative")


        # Add icons to represent different elements in the headings
        self.matches_frame.heading("Championship", text="\U0001F3C6 Championship", anchor="center")
        self.matches_frame.heading("Host", text="\U0001F464 Host", anchor="center")
        self.matches_frame.heading("Guest", text="\U0001F465 Guest", anchor="center")
        #Sorting by match time 
        self.matches_frame.heading("Match Time", text="\U000023F0 Match Time", anchor="center", command=lambda: treeview_sort_column(self.matches_frame, "Match Time", False))
        self.matches_frame.heading("Score", text="\U0001F4C8 Score", anchor="center")
        self.matches_frame.heading("Status", text="\U0001F3C3 Status", anchor="center")
        self.matches_frame.heading("Channel", text="\U0001F4FA Channel", anchor="center")
        self.matches_frame.heading("Round", text="\U0001F555 Round", anchor="center")


        # Resize the columns to fit the content
        self.matches_frame.column("Championship", width=150, anchor="center")
        self.matches_frame.column("Host", width=100, anchor="center")
        self.matches_frame.column("Guest", width=100, anchor="center")
        self.matches_frame.column("Match Time", width=100, anchor="center")
        self.matches_frame.column("Score", width=50, anchor="center")
        self.matches_frame.column("Status", width=80, anchor="center")
        self.matches_frame.column("Channel", width=80, anchor="center")
        self.matches_frame.column("Round", width=120, anchor="center")

        # Add borders to the widget
        self.style.configure("Treeview", borderwidth=2, relief="solid")

        self.matches_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.matches_frame.yview)
        self.matches_scrollbar.pack(side="right", fill=tk.Y)
        self.matches_frame.pack(side="left", fill="both", expand=True, padx=20, pady=(200, 20))
        self.matches_frame.config(yscrollcommand=self.matches_scrollbar.set)
        
        details=LabelFrame(self.root,text="Web Scraping",font=("Merriweather",12),bg="#241244",fg="white",relief=GROOVE,bd=10)
        details.place(x=0,y=0,relwidth=1)
        cust_name=Label(details,text="2023",font=(" Merriweather",14),bg="#241244",fg="white").grid(row=0,column=1,padx=50)     
    
        #SORTING DATA 
        def treeview_sort_column(tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)

            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

    def delete_matches(self):
        # Get the selected rows
        selected = self.matches_frame.selection()
        if not selected:
            tk.messagebox.showerror("Error", "No matches selected")
        else:
            # Ask the user to confirm the deletion
            confirmed = tk.messagebox.askyesno("Confirm deletion", "Are you sure you want to delete the selected matches?")
            if confirmed:
                for item in selected:
                    self.matches_frame.delete(item)
            
    def search_matches(self):
        # Define a function to print the selected date and display matches
        def print_selected_date():
            # Get the selected date from the calendar and format it as a string
            selected_date = cal.selection_get().strftime('%Y-%m-%d')
            # Fetch the matches for the selected date
            matches = self.fetch_data(selected_date)
            # Display the matches
            self.display_matches(matches)

        # Create a new Toplevel widget to contain the calendar and search button
        top = tk.Toplevel(self.root)

        # Create a Calendar widget and pack it in the Toplevel
        cal = Calendar(top, selectmode='day', year=int(pd.Timestamp.today().strftime("%Y")), month=int(pd.Timestamp.today().strftime("%m")), day=int(pd.Timestamp.today().strftime("%d")), date_pattern='yyyy-mm-dd')
        cal.pack(fill="both", expand=True)

        # Load the image file for the search button, resize it, and create a PhotoImage object
        search_image = Image.open("search.png")
        search_image = search_image.resize((100, 40))
        search_photo = ImageTk.PhotoImage(search_image)

        # Create a Button widget for the search button, set its image, and pack it in the Toplevel
        search_button = tk.Button(top, image=search_photo, command=print_selected_date, bg='#8956F1', fg='#fff', activebackground='#8956F1', activeforeground='#fff')
        search_button.image = search_photo
        search_button.pack()

        # Define a function to change the search button's background color when the cursor enters the calendar widget
        def on_enter_calendar(e):
            search_button.config(bg='green')

        # Define a function to change the search button's background color back to white when the cursor leaves the calendar widget
        def on_leave_calendar(e):
            search_button.config(bg='white')

        # Bind the on_enter_calendar function to the Enter event of the calendar widget
        cal.bind("<Enter>", on_enter_calendar)

        # Bind the on_leave_calendar function to the Leave event of the calendar widget
        cal.bind("<Leave>", on_leave_calendar)

    def load_logo(self, file):
        if os.path.exists(file):
            logo = tk.PhotoImage(file=file)
            return logo
        else:
            print(f"Error: {file} not found")
            return None
        
    def export_data(self):
        # Check if any matches have been searched for
        if self.matches_frame.get_children() == ():
            tk.messagebox.showerror("Error", "Please search for matches before exporting data.")
            return

        # Retrieve data from the treeview widget
        data = []
        for child in self.matches_frame.get_children():
            values = [self.matches_frame.item(child)["values"]]
            data.extend(values)

        # Create a Pandas DataFrame with the data
        df = pd.DataFrame(data, columns=["Championship", "Host", "Guest", "Match Time", "Score", "Status", "Channel", "Round"])

        # Export the DataFrame to a CSV file
        try:
            filename = f"match_schedule_{self.selected_date.get()}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            tk.messagebox.showinfo("Success", f"Match schedule data has been exported to {filename}.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while exporting data: {str(e)}")
    
    def display_matches(self, matches):
        # Clear the treeview before displaying new data
        for row in self.matches_frame.get_children():
            self.matches_frame.delete(row)

        # Insert new data into the treeview
        for row in matches:
            self.matches_frame.insert("", "end", values=(row["Championship"], row["Host"], row["Guest"], row["Match Time"], row["Score"], row["Status"], row["Channel"], row["Round"]))

    def fetch_data(self, date):
        # Send a GET request to the yallakora website with the formatted date
        page = requests.get(f"https://www.yallakora.com/match-center?date={date}")

        src = page.content
        soup = BeautifulSoup(src, "lxml")

        matches_details = []
        championships = soup.find_all("div", {"class": "matchCard"})

        def get_match_info(championship):
            champ_title = championship.find("h2").text.strip()
            all_matches = championship.find_all("li")

            for match in all_matches:
                status = match.find("div", {"class": "matchStatus"}).text.strip()
                channel_elem = match.contents[1].find("div", {"class": "channel icon-channel"})
                channel_match = channel_elem.text if channel_elem else "غير معروف"
                round_match = match.find("div", {"class": "date"}).text.strip()

                # Get teams names and logos
                team_A_elem = match.find("div", {"class" : "teamA"})
                team_A = team_A_elem.text.strip()

                team_B_elem = match.find("div", {"class" : "teamB"})
                team_B = team_B_elem.text.strip()

                # Get score of the match
                match_result = match.find("div", {"class" : "MResult"}).find_all("span", {"class" : "score"})
                score = f"{match_result[0].text.strip()}-{match_result[1].text.strip()}"

                # Get the time of the match
                match_time = match.find("div", {"class" : "MResult"}).find("span", {"class" : "time"}).text.strip()
                match_time_obj = datetime.strptime(match_time, "%H:%M")
                timezone = pytz.timezone("Africa/Cairo")
                match_time_obj = timezone.localize(match_time_obj)
                match_time = match_time_obj.astimezone(pytz.utc)

                match_details = {
                    "Championship": champ_title,
                    "Host": team_A,
                    "Guest": team_B,
                    "Match Time": match_time.strftime("%H:%M:%S"),
                    "Score": score,
                    "Status": status,
                    "Channel": channel_match,
                    "Round": round_match,
                }

                matches_details.append(match_details)

        for championship in championships:
            get_match_info(championship)

        return matches_details

if __name__ == "__main__":
    match_schedule_gui = MatchScheduleGUI()
    match_schedule_gui.root.mainloop()