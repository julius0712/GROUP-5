from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error 
from dotenv import load_dotenv 
import os

load_dotenv()

app = Flask(__name__)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_INVENTORY')
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM workouts ORDER BY date DESC")
    workouts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(workouts)


@app.route('/api/workouts', methods=['POST'])
def add_workout():
    data = request.json
    required_fields = ['date', 'exercise']
    if not data or not all(f in data for f in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workouts (date, exercise, sets, reps, weight)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['date'],
            data['exercise'],
            data.get('sets'),
            data.get('reps'),
            data.get('weight')
        ))
        conn.commit()
        workout_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({'id': workout_id, **data}), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM workouts WHERE id = %s", (id,))
    workout = cursor.fetchone()
    cursor.close()
    conn.close()

    if not workout:
        return jsonify({'error': 'Workout not found'}), 404
    return jsonify(workout)

@app.route('/api/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        updates = []
        values = []
        for field in ['date', 'exercise', 'sets', 'reps', 'weight']:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        query = f"UPDATE workouts SET {', '.join(updates)} WHERE id = %s"
        values.append(id)
        cursor.execute(query, tuple(values))

        if cursor.rowcount == 0:
            return jsonify({'error': 'Workout not found'}), 404

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Workout updated successfully'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workouts WHERE id = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Workout not found'}), 404

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Workout deleted successfully'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/progress', methods=['GET'])
def get_progress():
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT date, sets, reps, weight FROM workouts ORDER BY date ASC")
        workouts = cursor.fetchall()
        cursor.close()
        conn.close()

        progress = {}

        for w in workouts:
            date = w['date'].strftime('%Y-%m-%d')
        try:
            sets = int(w['sets'] or 0)
            reps = int(w['reps'] or 0)
            weight = float(w['weight'] or 0)
        except (TypeError, ValueError):
            sets = reps = 0
            weight = 0.0

        total_volume = sets * reps * weight
        progress[date] = progress.get(date, 0) + total_volume

        progress_list = [{'date': d, 'total_volume': v} for d, v in sorted(progress.items())]

        return jsonify(progress_list), 200


if __name__ == '__main__':
    app.run(debug=True)
