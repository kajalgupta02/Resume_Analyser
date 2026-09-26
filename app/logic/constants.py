"""Stable analysis vocabulary and defaults."""

DEFAULT_LLM_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_LLM_MODEL = "gpt-4o-mini"

COMMON_INDUSTRY_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust", "php", "ruby", "kotlin", "swift", "sql", "r", "html", "css", "bash", "shell",
    "react", "react.js", "next.js", "angular", "vue", "vue.js", "node.js", "express", "django", "flask", "fastapi", "spring boot", "asp.net", "dotnet",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "keras", "opencv", "redux", "tailwind", "tailwind css", "bootstrap", "graphql", "flutter", "react native",
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ci/cd", "cicd", "jenkins", "github actions", "gitlab", "ansible", "helm", "linux", "unix", "nginx", "prometheus", "grafana", "microservices", "serverless", "cloudformation",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "oracle", "cassandra", "sqlite", "kafka", "rabbitmq", "apache spark", "spark", "hadoop", "snowflake", "bigquery",
    "rest api", "rest apis", "restful", "restful apis", "git", "github", "gitlab", "agile", "scrum", "kanban", "jira", "unit testing", "integration testing", "tdd", "system design", "system architecture", "oop", "object oriented programming", "data structures", "algorithms",
    "figma", "ui/ux", "ui design", "ux design", "wireframing", "prototyping", "web accessibility", "wcag", "seo", "a/b testing", "machine learning", "deep learning", "nlp", "natural language processing", "computer vision", "business intelligence", "tableau", "power bi", "excel", "product management", "product roadmap", "data analysis", "data visualization",
]

BOILERPLATE_STOPWORDS = {
    "opportunity", "equal", "employer", "candidate", "responsibilities", "requirements", "qualification", "qualifications", "experience", "years", "role", "looking", "company", "team", "work", "working", "join", "help", "ideal", "successful", "environment", "benefits", "position", "apply", "seeking", "must", "able", "strong", "excellent", "demonstrated", "knowledge", "understanding", "good", "great", "degree", "bachelor", "master", "equivalent", "related", "field", "skills", "ability", "duties", "including", "responsible", "well", "plus", "required", "preferred", "competitive", "package",
}
