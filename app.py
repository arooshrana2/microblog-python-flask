import os, datetime, json
from flask import Flask, render_template, request
from dotenv import load_dotenv


load_dotenv()

DATA_FILE = 'data/entries.json'

def load_entries():
    """Load entries from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_entries(entries):
    """Save entries to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(entries, f, indent=2)

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['GET', 'POST'])
    def home():
        entries = load_entries()
        
        if request.method == 'POST':
            entry_content = request.form.get('content')
            blog_name = request.form.get('blog_name', 'default')
            formatted_date = datetime.datetime.today().strftime('%Y-%m-%d')
            entries.append({'content':entry_content, 'date':formatted_date, 'blog_name':blog_name})
            save_entries(entries)
        
        entries_with_date = [
            (
                entry['content'],
                entry['date'],
                datetime.datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%b %d')
            )
            for entry in entries
        ]

        return render_template("home.html", entries=entries_with_date)

    @app.route("/blog/<blog_name>", methods=['GET'])
    def blog(blog_name):
        entries = load_entries()
        filtered_entries = [entry for entry in entries if entry.get('blog_name') == blog_name]
        
        entries_with_date = [
            (
                entry['content'],
                entry['date'],
                datetime.datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%b %d')
            )
            for entry in filtered_entries
        ]

        return render_template("blog.html", blog_name=blog_name, entries=entries_with_date)
    
    return app