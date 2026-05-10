import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox as messagebox

class ResultsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._last_results_id = None
        
        # Main Layout: Sidebar-like result navigation and main content
        self.grid_columnconfigure(0, weight=0) # Navigation
        self.grid_columnconfigure(1, weight=1) # Content
        self.grid_rowconfigure(0, weight=1)

        # Result Navigation (Mini Sidebar)
        self.nav_frame = ctk.CTkFrame(self, width=180, corner_radius=0, fg_color=("gray90", "gray10"))
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        
        self.nav_label = ctk.CTkLabel(self.nav_frame, text="REPORT CARD", font=("Arial", 16, "bold"), text_color="#4cc9f0")
        self.nav_label.pack(pady=30, padx=20)

        self.nav_btns = {}
        self.create_nav_btn("📊 Dashboard", "overview")
        self.create_nav_btn("🔥 The Roast", "roast")
        self.create_nav_btn("🧠 Skills Map", "skills")
        self.create_nav_btn("📈 Metrics", "metrics")
        self.create_nav_btn("🚀 Action Plan", "action")

        # Main Content Area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
        # Header in Content Area
        self.header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="The Verdict is In. 💅", font=("Arial", 32, "bold"), text_color="#4cc9f0")
        self.title_label.pack(side="left")
        
        self.export_btn = ctk.CTkButton(self.header_frame, text="Download PDF Report 📥", 
                                       fg_color="#4361ee", hover_color="#3a0ca3",
                                       font=("Arial", 12, "bold"), command=self.export_report)
        self.export_btn.pack(side="right")

        # Container for different views
        self.views = {}
        self.current_view = None
        
        self.setup_overview_view()
        self.setup_roast_view()
        self.setup_skills_view()
        self.setup_metrics_view()
        self.setup_action_view()

        self.show_view("overview")

    def create_nav_btn(self, text, view_name):
        btn = ctk.CTkButton(self.nav_frame, text=text, height=50, fg_color="transparent", 
                           text_color=("gray10", "gray90"), hover_color=("#4361ee", "#4361ee"),
                           anchor="w", font=("Arial", 14, "bold"), corner_radius=12,
                           command=lambda v=view_name: self.show_view(v))
        btn.pack(pady=8, padx=15, fill="x")
        self.nav_btns[view_name] = btn

    def show_view(self, view_name):
        if self.current_view:
            self.views[self.current_view].pack_forget()
            self.nav_btns[self.current_view].configure(fg_color="transparent")
            
        self.current_view = view_name
        self.views[view_name].pack(fill="both", expand=True)
        self.nav_btns[view_name].configure(fg_color=("#4361ee", "#4361ee"), text_color="white")
        
        # Sassy title update based on view
        titles = {
            "overview": "The Verdict is In. 💅",
            "roast": "The Honest Truth. 🔥",
            "skills": "Brain Mapping. 🧠",
            "metrics": "Data Deep Dive. 📉",
            "action": "Your Battle Plan. 🚀"
        }
        self.title_label.configure(text=titles.get(view_name, "The Verdict is In. 💅"))

    def setup_overview_view(self):
        view = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["overview"] = view
        
        # Impactful Score Hero
        self.hero_frame = ctk.CTkFrame(view, corner_radius=25, border_width=2, border_color="#4cc9f0", height=250)
        self.hero_frame.pack(fill="x", pady=(0, 20))
        self.hero_frame.pack_propagate(False)
        
        self.score_circle = ctk.CTkLabel(self.hero_frame, text="0%", font=("Arial", 80, "bold"), text_color="#4cc9f0")
        self.score_circle.place(relx=0.5, rely=0.4, anchor="center")
        
        self.score_status = ctk.CTkLabel(self.hero_frame, text="SCANNING...", font=("Arial", 20, "bold"))
        self.score_status.place(relx=0.5, rely=0.75, anchor="center")

        self.persona_msg = ctk.CTkLabel(self.hero_frame, text="", font=("Arial", 14, "italic"), text_color="gray")
        self.persona_msg.place(relx=0.5, rely=0.88, anchor="center")

        # Section Grid
        self.sec_grid = ctk.CTkFrame(view, fg_color="transparent")
        self.sec_grid.pack(fill="both", expand=True)
        self.sec_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.sec_widgets = {}
        sections = ["Contact Info", "Education", "Experience", "Skills"]
        for i, sec in enumerate(sections):
            card = ctk.CTkFrame(self.sec_grid, corner_radius=15)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            ctk.CTkLabel(card, text=sec, font=("Arial", 12, "bold")).pack(pady=(10, 5))
            status_lbl = ctk.CTkLabel(card, text="❓", font=("Arial", 24))
            status_lbl.pack(pady=(0, 10))
            self.sec_widgets[sec] = status_lbl

    def setup_roast_view(self):
        view = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["roast"] = view
        
        ctk.CTkLabel(view, text="The Honest Truth. 💅", font=("Arial", 24, "bold"), text_color="#f72585").pack(pady=(0, 20), anchor="w")
        
        self.roast_box = ctk.CTkTextbox(view, font=("Arial", 18, "italic"), corner_radius=20, border_width=1, border_color="#f72585")
        self.roast_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.roast_box.insert("0.0", "Let's see if your resume is a masterpiece or a disaster...")

    def setup_skills_view(self):
        view = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["skills"] = view
        
        self.skills_split = ctk.CTkFrame(view, fg_color="transparent")
        self.skills_split.pack(fill="both", expand=True)
        
        # Matched
        self.m_frame = ctk.CTkFrame(self.skills_split, corner_radius=20)
        self.m_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.m_frame, text="Killed It ✨", font=("Arial", 16, "bold"), text_color="#4cc9f0").pack(pady=10)
        self.m_list = ctk.CTkTextbox(self.m_frame, font=("Arial", 13))
        self.m_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Missing
        self.miss_frame = ctk.CTkFrame(self.skills_split, corner_radius=20)
        self.miss_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.miss_frame, text="Ghosting These 🚩", font=("Arial", 16, "bold"), text_color="#f72585").pack(pady=10)
        self.miss_list = ctk.CTkTextbox(self.miss_frame, font=("Arial", 13))
        self.miss_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def setup_metrics_view(self):
        view = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["metrics"] = view
        
        # Upper Section: Detailed Cards
        self.met_grid = ctk.CTkFrame(view, fg_color="transparent")
        self.met_grid.pack(fill="x", pady=(0, 20))
        self.met_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.met_widgets = {}
        metrics = [
            ("Readability", "🧠", "How easy it is to read your profile."),
            ("Word Count", "📝", "The length of your professional story."),
            ("Complexity", "🌀", "Sophistication of your vocabulary.")
        ]
        for i, (name, icon, desc) in enumerate(metrics):
            card = ctk.CTkFrame(self.met_grid, corner_radius=15, border_width=1, border_color="#4361ee")
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            ctk.CTkLabel(card, text=f"{icon} {name}", font=("Arial", 14, "bold"), text_color="#4cc9f0").pack(pady=(15, 5))
            val_lbl = ctk.CTkLabel(card, text="--", font=("Arial", 32, "bold"))
            val_lbl.pack(pady=5)
            ctk.CTkLabel(card, text=desc, font=("Arial", 10), text_color="gray", wraplength=150).pack(pady=(0, 15))
            self.met_widgets[name] = val_lbl

        # Lower Section: Chart with Header
        chart_container = ctk.CTkFrame(view, corner_radius=20, border_width=1, border_color="gray30")
        chart_container.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(chart_container, text="Performance Visualization", font=("Arial", 16, "bold")).pack(pady=10)
        self.chart_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.canvas = None

    def setup_action_view(self):
        view = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["action"] = view
        
        ctk.CTkLabel(view, text="Your Road to the Dream Job 🚀", font=("Arial", 24, "bold"), text_color="#4cc9f0").pack(pady=(0, 20), anchor="w")
        
        self.action_box = ctk.CTkTextbox(view, font=("Arial", 15), corner_radius=20)
        self.action_box.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh(self):
        if not self.app.analysis_results:
            return
            
        current_results_id = id(self.app.analysis_results)
        if self._last_results_id == current_results_id:
            return
            
        self._last_results_id = current_results_id
        res = self.app.analysis_results
        
        # Animated Score Refresh
        target_score = int(res['score'])
        def animate_score(current=0):
            if current <= target_score:
                self.score_circle.configure(text=f"{current}%")
                self.after(10, lambda: animate_score(current + 1))
        animate_score()
        
        if res['score'] > 80:
            status, color = "ABSOLUTE LEGEND 🦄", "#4cc9f0"
        elif res['score'] > 60:
            status, color = "GETTING THERE 🌶️", "#4361ee"
        else:
            status, color = "NEEDS A GLOW UP 💅", "#f72585"
        self.score_status.configure(text=status, text_color=color)
        
        persona_messages = {
            "high": "The AI is obsessed with you. 💍",
            "mid": "You're a 'maybe' in a world of 'no's. 🌶️",
            "low": "The AI swiped left. Hard. 💅"
        }
        self.persona_msg.configure(text=persona_messages[category])
        
        for sec, present in res['sections'].items():
            self.sec_widgets[sec].configure(text="✅" if present else "❌", text_color="#2ecc71" if present else "#e74c3c")

        # Refresh Roast
        self.roast_box.delete("1.0", "end")
        roasts = {
            "low": [
                "Honey, this resume is dryer than a Popeyes biscuit. We need to work on this. 💅",
                "Did you write this on a typewriter while blindfolded? The ATS is going to ignore you faster than my ex. 🚩",
                "This isn't a resume; it's a cry for help. Let's fix it before you end up on LinkedIn 'Open to Work' forever. 💀"
            ],
            "mid": [
                "It's giving... 'average'. You're like the vanilla ice cream of candidates. Let's add some sprinkles. 🍦",
                "You've got the basics, but where's the spice? The ATS thinks you're 'fine', but we want 'hired'. 🌶️",
                "Not a total disaster, but definitely not a showstopper. Let's turn this 'maybe' into a 'YES'. ✨"
            ],
            "high": [
                "Look at you! You're basically a unicorn in a field of donkeys. 🦄",
                "The ATS is already planning the wedding. You and this job are a match made in heaven. 💎",
                "You didn't just understand the assignment; you became the teacher. Main character energy! 👑"
            ]
        }
        import random
        category = "high" if res['score'] > 80 else "mid" if res['score'] > 60 else "low"
        self.roast_box.insert("0.0", f"AI PERSONA SAYS:\n\n\"{random.choice(roasts[category])}\"")

        # Refresh Skills
        self.m_list.delete("1.0", "end")
        for kw in res['present_keywords']: self.m_list.insert("end", f"✨ {kw}\n")
        self.miss_list.delete("1.0", "end")
        for kw in res['missing_keywords']: self.miss_list.insert("end", f"🚩 {kw}\n")

        # Refresh Metrics
        self.met_widgets["Readability"].configure(text=f"{res['metrics']['readability']:.0f}/100")
        self.met_widgets["Word Count"].configure(text=str(res['metrics']['word_count']))
        self.met_widgets["Complexity"].configure(text="High" if res['metrics']['avg_word_len'] > 6 else "Medium" if res['metrics']['avg_word_len'] > 4 else "Simple")
        
        if self.canvas: self.canvas.get_tk_widget().destroy()
        fig = Figure(figsize=(6, 3), dpi=100, facecolor='#1a1a2e')
        ax = fig.add_subplot(111); ax.set_facecolor('#1a1a2e')
        ax.bar(["Match", "Readability", "Skills"], [res['score'], res['metrics']['readability'], (len(res['present_keywords'])/len(res['total_keywords'])*100 if res['total_keywords'] else 0)], color='#4cc9f0')
        ax.set_ylim(0, 100); ax.tick_params(colors='white'); fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame); self.canvas.draw(); self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Refresh Action
        self.action_box.delete("1.0", "end")
        action_plan = "The Glow Up Protocol:\n\n"
        for i, rec in enumerate(res['recommendations'], 1):
            action_plan += f"STEP {i}: {rec}\n\n"
        self.action_box.insert("0.0", action_plan)

    def export_report(self):
        messagebox.showinfo("Exporting...", "Generating your premium PDF report... (Feature unlocked for showcase! ✨)")
        # Logic for PDF generation would go here using fpdf or reportlab
