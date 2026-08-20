import customtkinter as ctk
from .sidebar import Sidebar
from .page_manager import PageManager
from ..logic.analyser import ResumeAnalyser
from ..logic.history_manager import HistoryManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#070B14")
        ctk.set_appearance_mode("Dark")  
        ctk.set_default_color_theme("blue")  
        self.title("AI Resume Improver Pro")
        self.geometry("1240x820")
        self.minsize(1100, 720)
        self.resizable(True, True)
        
        # Initialize managers and data storage
        self.analyser = ResumeAnalyser()
        self.history_manager = HistoryManager()
        self.analysis_results = None
        self.resume_path = None
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.page_manager = PageManager(self)
        self.page_manager.grid(row=0, column=1, sticky="nsew")

    def run(self):
        self.mainloop()
