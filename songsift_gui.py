import tkinter as tk
from tkinter import ttk, messagebox
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from time import sleep


client_id = "spotify client id"
client_secret = "client secret id"

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

console = Console()


class SongSiftApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SongSift")
        self.root.geometry("800x600")
        self.root.configure(bg='#002b36')  

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 14), background='#002b36', foreground="#7fffd4")
        style.configure("TButton", font=("Helvetica", 16, "bold"), background='#3cb371', foreground="black")
        style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background='#002b36', foreground="#00ff7f")
        style.configure("Treeview", font=("Helvetica", 12), background='#004d40', foreground="white", fieldbackground='#004d40', rowheight=30)
        style.map('TButton', background=[('active', '#32a862')])

        self.center_frame = tk.Frame(root, bg='#002b36')
        self.center_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.header_label = ttk.Label(self.center_frame, text="SongSift", font=("Helvetica", 28, "bold"))
        self.header_label.pack(pady=20)

        self.instruction_label = ttk.Label(self.center_frame, text="Enter a song to get recommendations:")
        self.instruction_label.pack(pady=5)

        self.song_entry = tk.Entry(self.center_frame, width=50, font=("Helvetica", 14), bd=2, relief="solid", fg='black')
        self.song_entry.pack(pady=10)

        self.search_button = ttk.Button(self.center_frame, text="Search", command=self.fetch_recommendations, style='TButton')
        self.search_button.pack(pady=20)

        self.result_frame = tk.Frame(root, bg='#002b36')

        self.result_tree = ttk.Treeview(self.result_frame, columns=("Track Name", "Artist"), show='headings', height=10)
        self.result_tree.heading("Track Name", text="Track Name")
        self.result_tree.heading("Artist", text="Artist")
        self.result_tree.column("Track Name", anchor=tk.W, width=400)
        self.result_tree.column("Artist", anchor=tk.W, width=300)

        self.scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.pack(fill=tk.BOTH, expand=True)

        self.result_tree.bind("<Double-1>", self.play_song)

       
        self.back_button = ttk.Button(root, text="Back", command=self.go_back, style='TButton')
        self.back_button.place(relx=0.95, rely=0.95, anchor=tk.SE, height=40, width=100)
        self.back_button.configure(style="Rounded.TButton")
        self.back_button.place_forget()

        
        style.configure('Rounded.TButton',
                        borderwidth=1,
                        relief="flat",
                        background='#3cb371',
                        foreground='black',
                        font=("Helvetica", 16, "bold"))

    def fetch_recommendations(self):
        songname = self.song_entry.get()
        self.result_tree.delete(*self.result_tree.get_children())

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("[bold green]Fetching recommendations...", start=False)
            progress.start_task(task)
            
            sleep(2)
            recommendations = self.get_recommendations(songname)
            progress.stop()

        if recommendations:
            for track in recommendations:
                self.result_tree.insert("", tk.END, values=(track['name'], track['artists'][0]['name']), tags=(track['uri'],))
            self.show_result_frame()
        else:
            messagebox.showerror("Error", f"No recommendations found for '{songname}'")

    def get_recommendations(self, track_name):
        results = sp.search(q=track_name, type='track')
        if not results['tracks']['items']:
            return []

        track_uri = results['tracks']['items'][0]['uri']
        recommendations = sp.recommendations(seed_tracks=[track_uri])['tracks']
        return recommendations

    def play_song(self, event):
        item = self.result_tree.selection()[0]
        track_uri = self.result_tree.item(item, "tags")[0]
        track_url = f"https://open.spotify.com/track/{track_uri.split(':')[-1]}"
        webbrowser.open(track_url)

    def show_result_frame(self):
        
        self.result_frame.place(relx=0.5, rely=1.1, anchor=tk.CENTER) 
        self.result_frame.update_idletasks()  

        for i in range(21):  
            self.result_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, y=600 - i*30)  
            self.root.update()
            self.root.after(10)
        

        self.back_button.place(relx=0.95, rely=0.95, anchor=tk.SE, height=40, width=100)

    def go_back(self):
        self.result_frame.place_forget()
        self.back_button.place_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = SongSiftApp(root)
    root.mainloop()
