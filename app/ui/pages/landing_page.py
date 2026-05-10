import customtkinter as ctk

class LandingPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Enhanced Background design
        self.bg_accent = ctk.CTkFrame(self, fg_color="#4361ee", width=900, height=900, corner_radius=450)
        self.bg_accent.place(relx=0.95, rely=-0.15, anchor="center")
        
        self.bg_accent2 = ctk.CTkFrame(self, fg_color="#4cc9f0", width=500, height=500, corner_radius=250)
        self.bg_accent2.place(relx=0.05, rely=0.95, anchor="center")
        
        # Hero Section with Glassmorphism feel
        self.hero_container = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=30, border_width=1, border_color="gray30")
        self.hero_container.place(relx=0.5, rely=0.45, anchor="center", relwidth=0.85, relheight=0.7)
        
        # Center content inside hero
        self.content_frame = ctk.CTkFrame(self.hero_container, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.title_label = ctk.CTkLabel(self.content_frame, 
                                       text="Your Career Glow-Up\nStarts Here. ✨", 
                                       font=("Arial", 68, "bold"),
                                       justify="center",
                                       text_color=("#1a1a2e", "#ffffff"))
        self.title_label.pack(pady=(0, 20), padx=20)
        
        self.desc_label = ctk.CTkLabel(self.content_frame, 
                                      text="Stop guessing. Let AI fix your resume and land that interview.\nSassy, smart, and ready to work.",
                                      font=("Arial", 24),
                                      text_color=("#4a4a4a", "#b0b0b0"))
        self.desc_label.pack(pady=10, padx=20)
        
        self.start_button = ctk.CTkButton(self.content_frame, 
                                        text="LET'S DO THIS 🚀", 
                                        height=75, 
                                        width=350,
                                        fg_color="#4cc9f0",
                                        hover_color="#4361ee",
                                        text_color="#000000",
                                        font=("Arial", 24, "bold"),
                                        corner_radius=37.5,
                                        command=lambda: parent.show_page("UploadPage"))
        self.start_button.pack(pady=60)
        
        # Bottom info section - Floating style
        self.info_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#1a1a2e"), height=90, corner_radius=20, border_width=1, border_color="gray30")
        self.info_frame.pack(side="bottom", fill="x", padx=100, pady=40)
        self.info_frame.pack_propagate(False)
        
        badges = [("ATS Optimization", "🔥"), ("Smart Insights", "💎"), ("AI Powered", "✨"), ("Impactful Results", "📈")]
        for text, icon in badges:
            container = ctk.CTkFrame(self.info_frame, fg_color="transparent")
            container.pack(side="left", expand=True)
            ctk.CTkLabel(container, text=f"{icon} {text}", font=("Arial", 16, "bold"), text_color="#4cc9f0").pack()

    def refresh(self):
        # Smoother entrance animation
        initial_y = 0.55
        target_y = 0.45
        self.hero_container.place(relx=0.5, rely=initial_y)
        
        def animate(current_y):
            if current_y > target_y:
                next_y = current_y - 0.01
                self.hero_container.place(relx=0.5, rely=next_y)
                self.after(10, lambda: animate(next_y))
        
        self.after(50, lambda: animate(initial_y))
