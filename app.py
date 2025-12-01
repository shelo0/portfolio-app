from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
DATABASE = os.environ.get('DATABASE_PATH', 'portfolio.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, title TEXT NOT NULL,
                bio TEXT, email TEXT, github TEXT, linkedin TEXT
            );
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                category TEXT NOT NULL, proficiency INTEGER DEFAULT 80
            );
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                description TEXT, technologies TEXT, github_link TEXT, live_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                email TEXT NOT NULL, message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        cursor = conn.execute('SELECT COUNT(*) FROM profile')
        if cursor.fetchone()[0] == 0:
            conn.execute(
                'INSERT INTO profile (name, title, bio, email, github, linkedin) VALUES (?, ?, ?, ?, ?, ?)',
                (
                    'DevOps Engineer',
                    'Full Stack Developer & DevOps Specialist',
                    'Building scalable applications with Docker, Jenkins, Python, and cloud technologies.',
                    'contact@example.com',
                    'https://github.com/shelo0',
                    'https://linkedin.com/in/profile'
                )
            )
            skills = [
                ('Python', 'Programming', 90),
                ('Flask', 'Framework', 85),
                ('Docker', 'DevOps', 90),
                ('Jenkins', 'CI/CD', 85),
                ('Linux', 'Systems', 85),
                ('Git', 'Version Control', 90),
                ('REST APIs', 'Development', 88),
                ('SQLite', 'Database', 82)
            ]
            conn.executemany(
                'INSERT INTO skills (name, category, proficiency) VALUES (?, ?, ?)',
                skills
            )
            projects = [
                (
                    'CI/CD Pipeline',
                    'Built complete CI/CD with Jenkins and Docker',
                    'Jenkins, Docker, Python',
                    'https://github.com/shelo0/sample-app',
                    ''
                ),
                (
                    'Portfolio REST API',
                    'Full REST API with CRUD operations',
                    'Python, Flask, SQLite, Docker',
                    'https://github.com/shelo0/portfolio-app',
                    ''
                ),
                (
                    'Cloud Deployment',
                    'Deployed apps to Vultr using Docker Swarm',
                    'Docker Swarm, Vultr, Linux',
                    '',
                    ''
                )
            ]
            conn.executemany(
                'INSERT INTO projects (title, description, technologies, github_link, live_link) VALUES (?, ?, ?, ?, ?)',
                projects
            )
            conn.commit()

init_db()

@app.route('/')
def home():
    conn = get_db()
    profile = conn.execute('SELECT * FROM profile LIMIT 1').fetchone()
    skills = conn.execute('SELECT * FROM skills ORDER BY proficiency DESC').fetchall()
    projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', profile=profile, skills=skills, projects=projects)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api')
def api_docs():
    return jsonify({
        'name': 'Portfolio API',
        'version': '1.0',
        'endpoints': {
            'GET /api/profile': 'Get profile',
            'PUT /api/profile': 'Update profile',
            'GET /api/skills': 'List skills',
            'POST /api/skills': 'Add skill',
            'DELETE /api/skills/<id>': 'Delete skill',
            'GET /api/projects': 'List projects',
            'POST /api/projects': 'Add project',
            'DELETE /api/projects/<id>': 'Delete project',
            'GET /api/messages': 'List messages',
            'POST /api/messages': 'Send message',
            'GET /health': 'Health check'
        }
    })

@app.route('/api/profile', methods=['GET'])
def get_profile():
    conn = get_db()
    profile = conn.execute('SELECT * FROM profile LIMIT 1').fetchone()
    conn.close()
    return jsonify(dict(profile)) if profile else (jsonify({'error': 'Not found'}), 404)

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    conn = get_db()
    conn.execute(
        'UPDATE profile SET name=?, title=?, bio=?, email=?, github=?, linkedin=? WHERE id=1',
        (
            data.get('name'),
            data.get('title'),
            data.get('bio'),
            data.get('email'),
            data.get('github'),
            data.get('linkedin')
        )
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profile updated'})

@app.route('/api/skills', methods=['GET'])
def get_skills():
    conn = get_db()
    skills = conn.execute('SELECT * FROM skills ORDER BY proficiency DESC').fetchall()
    conn.close()
    return jsonify([dict(s) for s in skills])

@app.route('/api/skills', methods=['POST'])
def create_skill():
    data = request.get_json()
    if not data.get('name') or not data.get('category'):
        return jsonify({'error': 'Name and category required'}), 400
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO skills (name, category, proficiency) VALUES (?, ?, ?)',
        (data['name'], data['category'], data.get('proficiency', 80))
    )
    conn.commit()
    skill_id = cursor.lastrowid
    conn.close()
    return jsonify({'message': 'Skill created', 'id': skill_id}), 201

@app.route('/api/skills/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    conn = get_db()
    conn.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Skill deleted'})

@app.route('/api/projects', methods=['GET'])
def get_projects():
    conn = get_db()
    projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(p) for p in projects])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO projects (title, description, technologies, github_link, live_link) VALUES (?, ?, ?, ?, ?)',
        (
            data['title'],
            data.get('description', ''),
            data.get('technologies', ''),
            data.get('github_link', ''),
            data.get('live_link', '')
        )
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return jsonify({'message': 'Project created', 'id': project_id}), 201

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    conn = get_db()
    conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Project deleted'})

@app.route('/api/messages', methods=['GET'])
def get_messages():
    conn = get_db()
    messages = conn.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(m) for m in messages])

@app.route('/api/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not all([data.get('name'), data.get('email'), data.get('message')]):
        return jsonify({'error': 'Name, email, message required'}), 400
    conn = get_db()
    conn.execute(
        'INSERT INTO messages (name, email, message) VALUES (?, ?, ?)',
        (data['name'], data['email'], data['message'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Message sent'}), 201

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    conn = get_db()
    conn.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Message deleted'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)