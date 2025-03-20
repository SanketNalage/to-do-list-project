from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "todolist"),
        user=os.getenv("POSTGRES_USER", "youruser"),
        password=os.getenv("POSTGRES_PASSWORD", "yourpassword"),
        host="db",  # Use the service name from docker-compose
        port="5432"
    )
    return conn

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks')
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'id': task[0], 'description': task[1]} for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    new_task = request.get_json()['description']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (description) VALUES (%s) RETURNING id', (new_task,))
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': task_id, 'description': new_task}), 201

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Task deleted successfully'})

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    updated_description = request.get_json()['description']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET description = %s WHERE id = %s', (updated_description, id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': id, 'description': updated_description})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)