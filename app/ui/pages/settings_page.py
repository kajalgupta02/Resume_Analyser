import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Sassy Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(self.header_frame, 
                     text="Vibe Check. ⚙️", 
                     font=("Arial", 32, "bold"),
                     text_color="#4cc9f0").pack(side="left")
        
        ctk.CTkLabel(self, 
                     text="Customize your experience. Because you're the boss.",
                     font=("Arial", 16)).pack(anchor="w", padx=40, pady=(0, 30))
        
        # Theme section
        theme_frame = ctk.CTkFrame(self, corner_radius=20, border_width=1, border_color="#4361ee")
        theme_frame.pack(pady=10, padx=40, fill="x")
        
        ctk.CTkLabel(theme_frame, text="Appearance Mode 🎨", font=("Arial", 18, "bold")).pack(pady=(20, 10), padx=30, anchor="w")
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_option = ctk.CTkOptionMenu(theme_frame, 
                                            values=["System", "Light", "Dark"],
                                            variable=self.theme_var,
                                            fg_color="#4361ee",
                                            button_color="#4361ee",
                                            command=self.change_appearance_mode)
        self.theme_option.pack(pady=(0, 30), padx=30, anchor="w")
        
        # About section
        info_frame = ctk.CTkFrame(self, corner_radius=20, border_width=1, border_color="#4361ee")
        info_frame.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkLabel(info_frame, text="The Tea on RESUME AI PRO 💎", font=("Arial", 18, "bold")).pack(pady=(20, 10), padx=30, anchor="w")
        ctk.CTkLabel(info_frame, 
                     text="Version: 1.1.0 (The Sassy Update)\nStatus: Serving looks and results.\n\nMade with ✨ and Python.", 
                     justify="left",
                     font=("Arial", 13)).pack(pady=(0, 30), padx=30, anchor="w")

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
