import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from docx import Document
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser

class ModernResumeImprover:
    def __init__(self):
        self.window = ThemedTk(theme="arc")  # Modern theme
        self.window.title("AI Resume Improver Pro")
        self.window.geometry("1000x700")
        self.window.configure(bg='#f0f0f0')
        
        # Initialize variables
        self.resume_text = ""
        self.job_description = ""
        self.current_page = 0
        
        # Predefined job roles
        self.job_roles = {
            "Data Analyst": ["python", "sql", "excel", "statistics", "visualization", "pandas", "tableau", "power bi"],
            "Backend Developer": ["python", "java", "databases", "api", "rest", "docker", "git", "aws"],
            "Frontend Developer": ["javascript", "html", "css", "react", "vue", "typescript", "responsive design"],
            "Data Scientist": ["python", "r", "machine learning", "deep learning", "statistics", "sql", "tensorflow"],
            "DevOps Engineer": ["docker", "kubernetes", "jenkins", "aws", "ci/cd", "linux", "terraform"],
        }
        
        self.setup_styles()
        self.setup_gui()
        
    def setup_styles(self):
        # Custom styles for widgets
        style = ttk.Style()
        style.configure("Custom.TButton",
                       padding=10,
                       font=('Helvetica', 10, 'bold'))
        
        style.configure("Title.TLabel",
                       font=('Helvetica', 16, 'bold'),
                       padding=10)
                       
        style.configure("SubTitle.TLabel",
                       font=('Helvetica', 12),
                       padding=5)
                       
        style.configure("Card.TFrame",
                       background='white',
                       relief='raised',
                       borderwidth=1)
        
    def setup_gui(self):
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.home_tab = self.create_home_tab()
        self.analysis_tab = self.create_analysis_tab()
        self.visualization_tab = self.create_visualization_tab()
        self.help_tab = self.create_help_tab()
        
        # Add tabs to notebook
        self.notebook.add(self.home_tab, text='Home')
        self.notebook.add(self.analysis_tab, text='Analysis')
        self.notebook.add(self.visualization_tab, text='Visualization')
        self.notebook.add(self.help_tab, text='Help')
        
    def create_home_tab(self):
        tab = ttk.Frame(self.notebook, padding="20")
        
        # Welcome message
        welcome_frame = ttk.Frame(tab, style="Card.TFrame")
        welcome_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(welcome_frame, 
                 text="Welcome to AI Resume Improver Pro",
                 style="Title.TLabel").pack(pady=10)
                 
        ttk.Label(welcome_frame,
                 text="Enhance your resume with AI-powered analysis and suggestions",
                 style="SubTitle.TLabel").pack(pady=5)
        
        # Quick start guide
        guide_frame = ttk.Frame(tab, style="Card.TFrame")
        guide_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(guide_frame,
                 text="Quick Start Guide",
                 style="Title.TLabel").pack(pady=10)
                 
        steps = [
            "1. Upload your resume (.txt or .docx)",
            "2. Select a job role or enter custom requirements",
            "3. Run the analysis",
            "4. View detailed results and suggestions"
        ]
        
        for step in steps:
            ttk.Label(guide_frame,
                     text=step,
                     style="SubTitle.TLabel").pack(pady=2)
        
        # Action buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill='x', padx=10, pady=20)
        
        ttk.Button(button_frame,
                  text="Start Analysis",
                  style="Custom.TButton",
                  command=lambda: self.notebook.select(1)).pack(side='left', padx=5)
                  
        ttk.Button(button_frame,
                  text="View Tutorial",
                  style="Custom.TButton",
                  command=self.show_tutorial).pack(side='left', padx=5)
        
        return tab
        
    def create_analysis_tab(self):
        tab = ttk.Frame(self.notebook, padding="20")
        
        # Left panel - Input
        left_panel = ttk.Frame(tab)
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        # Resume upload section
        resume_frame = ttk.LabelFrame(left_panel, text="Resume Upload", padding=10)
        resume_frame.pack(fill='x', pady=5)
        
        self.resume_label = ttk.Label(resume_frame, text="No file selected")
        self.resume_label.pack(side='left', padx=5)
        
        ttk.Button(resume_frame,
                  text="Choose File",
                  style="Custom.TButton",
                  command=self.load_resume).pack(side='right')
        
        # Job description section
        job_frame = ttk.LabelFrame(left_panel, text="Job Requirements", padding=10)
        job_frame.pack(fill='x', pady=5)
        
        ttk.Label(job_frame, text="Select Role:").pack(anchor='w')
        self.role_var = tk.StringVar()
        role_dropdown = ttk.Combobox(job_frame,
                                   textvariable=self.role_var,
                                   values=list(self.job_roles.keys()))
        role_dropdown.pack(fill='x', pady=5)
        role_dropdown.bind('<<ComboboxSelected>>', self.on_role_select)
        
        ttk.Label(job_frame, text="Or Enter Custom Requirements:").pack(anchor='w')
        self.job_desc_text = tk.Text(job_frame, height=5, width=40)
        self.job_desc_text.pack(fill='x', pady=5)
        
        # Right panel - Results
        right_panel = ttk.Frame(tab)
        right_panel.pack(side='right', fill='both', expand=True, padx=5)
        
        # Results section
        results_frame = ttk.LabelFrame(right_panel, text="Analysis Results", padding=10)
        results_frame.pack(fill='both', expand=True)
        
        self.results_text = tk.Text(results_frame, height=20, width=50)
        self.results_text.pack(fill='both', expand=True)
        
        # Analysis button
        ttk.Button(tab,
                  text="Analyze Resume",
                  style="Custom.TButton",
                  command=self.analyze_resume).pack(pady=10)
        
        return tab
        
    def create_visualization_tab(self):
        tab = ttk.Frame(self.notebook, padding="20")
        
        # Create frame for matplotlib figure
        self.plot_frame = ttk.Frame(tab)
        self.plot_frame.pack(fill='both', expand=True)
        
        # Initial message
        ttk.Label(self.plot_frame,
                 text="Run analysis to see visualizations",
                 style="Title.TLabel").pack(pady=20)
        
        return tab
        
    def create_help_tab(self):
        tab = ttk.Frame(self.notebook, padding="20")
        
        # Help sections
        sections = [
            ("Getting Started", "Learn how to use the basic features of AI Resume Improver"),
            ("FAQ", "Frequently asked questions about resume improvement"),
            ("Tips & Tricks", "Expert tips for maximizing your resume score"),
            ("Contact Support", "Get help with technical issues")
        ]
        
        for title, desc in sections:
            section_frame = ttk.Frame(tab, style="Card.TFrame")
            section_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(section_frame,
                     text=title,
                     style="Title.TLabel").pack(anchor='w', padx=10, pady=5)
                     
            ttk.Label(section_frame,
                     text=desc,
                     style="SubTitle.TLabel").pack(anchor='w', padx=10, pady=5)
                     
            ttk.Button(section_frame,
                      text="Learn More",
                      style="Custom.TButton",
                      command=lambda t=title: self.show_help_section(t)).pack(anchor='w', padx=10, pady=5)
        
        return tab
    
    def load_resume(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("Word files", "*.docx")]
        )
        if file_path:
            try:
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        self.resume_text = file.read()
                elif file_path.endswith('.docx'):
                    doc = Document(file_path)
                    self.resume_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                
                self.resume_label.config(text=os.path.basename(file_path))
                messagebox.showinfo("Success", "Resume loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load resume: {str(e)}")
    
    def on_role_select(self, event=None):
        selected_role = self.role_var.get()
        if selected_role in self.job_roles:
            keywords = ', '.join(self.job_roles[selected_role])
            self.job_desc_text.delete('1.0', tk.END)
            self.job_desc_text.insert('1.0', keywords)
    
    def analyze_resume(self):
        if not self.resume_text:
            messagebox.showerror("Error", "Please load a resume first!")
            return
            
        job_desc = self.job_desc_text.get('1.0', tk.END).strip()
        if not job_desc:
            messagebox.showerror("Error", "Please enter job description or select a predefined role!")
            return
            
        # Process text and calculate similarity
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([self.resume_text, job_desc])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Extract keywords
        if "," in job_desc:
            required_keywords = [kw.strip() for kw in job_desc.split(",") if kw.strip()]
        else:
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix[1].toarray()[0]
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            required_keywords = [word for word, score in keyword_scores[:10] if score > 0]
        
        # Find missing keywords
        resume_words = set(self.resume_text.lower().split())
        missing_keywords = [kw for kw in required_keywords if kw.lower() not in resume_words]
        
        # Display results
        self.show_results(similarity, missing_keywords, required_keywords)
        self.create_visualizations(similarity, missing_keywords, required_keywords)
        
        # Switch to visualization tab
        self.notebook.select(2)
    
    def show_results(self, similarity, missing_keywords, required_keywords):
        results = f"Match Score: {similarity * 100:.2f}%\n\n"
        results += "Required Keywords:\n"
        for kw in required_keywords:
            status = "✓" if kw not in missing_keywords else "✗"
            results += f"{status} {kw}\n"
        
        results += "\nMissing Keywords:\n"
        if missing_keywords:
            for kw in missing_keywords:
                results += f"- {kw}\n"
        else:
            results += "None - Great job!\n"
        
        results += "\nSuggestions:\n"
        if missing_keywords:
            results += "1. Consider adding experience or skills related to:\n"
            results += "\n".join([f"   - {kw}" for kw in missing_keywords])
            results += "\n\n2. Use specific examples to demonstrate these skills"
        else:
            results += "Your resume contains all the key requirements!"
        
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', results)
    
    def create_visualizations(self, similarity, missing_keywords, required_keywords):
        # Clear previous plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Create figure with subplots
        fig = Figure(figsize=(12, 6))
        
        # Match score gauge
        ax1 = fig.add_subplot(121)
        self.create_gauge_chart(ax1, similarity)
        
        # Keyword presence chart
        ax2 = fig.add_subplot(122)
        self.create_keyword_chart(ax2, missing_keywords, required_keywords)
        
        # Add figure to frame
        canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_gauge_chart(self, ax, similarity):
        score = similarity * 100
        
        # Create gauge chart
        ax.set_title('Resume Match Score')
        ax.add_patch(plt.Circle((0.5, 0), 0.4, fill=False))
        
        # Add colored arc based on score
        if score < 50:
            color = 'red'
        elif score < 75:
            color = 'orange'
        else:
            color = 'green'
            
        ax.add_patch(plt.matplotlib.patches.Arc((0.5, 0), 0.8, 0.8, 
                                              theta1=0, theta2=score*1.8,
                                              color=color, linewidth=10))
        
        # Add score text
        ax.text(0.5, -0.2, f'{score:.1f}%',
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=20)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.axis('off')
    
    def create_keyword_chart(self, ax, missing_keywords, required_keywords):
        present = len(required_keywords) - len(missing_keywords)
        sizes = [present, len(missing_keywords)]
        labels = ['Present', 'Missing']
        colors = ['#2ecc71', '#e74c3c']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90)
        ax.set_title('Keyword Coverage')
    
    def show_tutorial(self):
        # Open tutorial in new window
        tutorial = tk.Toplevel(self.window)
        tutorial.title("Tutorial")
        tutorial.geometry("600x400")
        
        # Add tutorial content
        ttk.Label(tutorial,
                 text="How to Use AI Resume Improver",
                 style="Title.TLabel").pack(pady=10)
                 
        steps = [
            "1. Click 'Choose File' to upload your resume",
            "2. Select a predefined job role or enter custom requirements",
            "3. Click 'Analyze Resume' to start the analysis",
            "4. View your results in the Analysis tab",
            "5. Check the Visualization tab for graphical insights",
            "6. Follow the suggestions to improve your resume"
        ]
        
        for step in steps:
            ttk.Label(tutorial, text=step, padding=5).pack()
            
        ttk.Button(tutorial,
                  text="Close",
                  style="Custom.TButton",
                  command=tutorial.destroy).pack(pady=20)
    
    def show_help_section(self, section):
        # Placeholder for help section content
        messagebox.showinfo(section, f"Displaying help for {section}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ModernResumeImprover()
    app.run()