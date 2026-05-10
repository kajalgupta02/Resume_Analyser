import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, width=220, corner_radius=0)
        self.parent = parent
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(self, text="RESUME\nAI PRO", font=("Arial", 24, "bold"), text_color="#4cc9f0")
        self.logo_label.pack(pady=(30, 40), padx=20)
        
        self.buttons = {}
        
        self.add_button("🏠 Home", "LandingPage")
        self.add_button("🔍 Analyze", "UploadPage")
        self.add_button("📊 Results", "ResultsPage")
        self.add_button("⚙️ Settings", "SettingsPage")

    def add_button(self, name, page_name):
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=5, padx=10, fill="x")
        
        # Active indicator (hidden by default)
        indicator = ctk.CTkFrame(btn_container, width=4, height=30, fg_color="transparent", corner_radius=2)
        indicator.pack(side="left", padx=(0, 5))
        
        button = ctk.CTkButton(btn_container, 
                              text=name, 
                              height=50,
                              fg_color="transparent",
                              text_color=("gray10", "gray90"),
                              hover_color=("#4361ee", "#4361ee"),
                              anchor="w",
                              corner_radius=12,
                              font=("Arial", 15, "bold"),
                              command=lambda: self.parent.page_manager.show_page(page_name))
        button.pack(side="left", fill="x", expand=True)
        
        # Store both for active state updates
        self.buttons[page_name] = {"button": button, "indicator": indicator}

    def set_active(self, page_name):
        for name, components in self.buttons.items():
            btn = components["button"]
            ind = components["indicator"]
            if name == page_name:
                btn.configure(fg_color=("#4361ee", "#4361ee"), text_color="white")
                ind.configure(fg_color="#4cc9f0") # Bright glow
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
                ind.configure(fg_color="transparent")
