from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database setup
DATABASE = "video_data.db"

def init_db():
    # First, delete the existing database file
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print("Removed existing database")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Create tables with proper schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                likes INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                username TEXT,
                FOREIGN KEY(video_id) REFERENCES videos(id),
                UNIQUE(video_id, username)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT
            )
        """)
        
        # Add test videos
        test_videos = [
            ("Steph_didnt_move_on.mp4", 0),
            ("STEPH_CURRY_BEHIND_THE_BACK_FLOATER_OMG.mp4", 0),
            ("Oh_how_I_miss_when_she_was_just_a_sleepy_baby_my_little_Pawtrasha.mp4", 0),
            ("Ronaldo_scored_a_hat_trick_to_lead_Manchester_United_to_a_3-2_win_over_Tottenham.mp4", 0),
            ("baby_wants_milk!!.mp4", 0),
            ("BATCAT.mp4", 0),
            ("A_WORLD_CLASS_ASSIST_BY_LEWANDOWSKI_AND_A_WORLD_CLASS_FINISH_BY_LAMINE_YAMAL_TO_EQUALIZE_FOR_BARCA.mp4", 0),
            ("one_pin_wonder.mp4", 0)
        ]
        
        cursor.executemany(
            "INSERT INTO videos (filename, likes) VALUES (?, ?)",
            test_videos
        )
        conn.commit()
        print("Database initialized successfully")

# Initialize database when the app starts
init_db()

@app.route('/')
def home():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, likes FROM videos")
        videos = cursor.fetchall()
        
        print("Database records:", videos)

    video_data = [
        {
            'id': video[0],
            'filename': video[1],
            'likes': video[2]
        } 
        for video in videos
    ]
    
    # Debug: Print the actual files in the videos directory
    videos_dir = os.path.join('static', 'videos')
    print("Files in videos directory:", os.listdir(videos_dir))
    
    # Debug: Print the constructed paths
    for video in video_data:
        full_path = os.path.join('static', 'videos', video['filename'])
        print(f"Checking path: {full_path}")
        print(f"File exists: {os.path.exists(full_path)}")
    
    return render_template('index.html', 
                         videos=video_data,
                         logged_in=('username' in session),
                         username=session.get('username'))

@app.route('/like', methods=['POST'])
def like_video():
    print("Like route accessed")
    
    if 'username' not in session:
        print("No user logged in")
        return jsonify(success=False, message="Please log in to like videos")
    
    try:
        data = request.json
        video_id = data.get("video_id")
        username = session['username']
        
        print(f"Attempting to like/unlike video {video_id} by user {username}")
        
        with sqlite3.connect(DATABASE) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # Verify video exists
            cursor.execute("SELECT id FROM videos WHERE id = ?", (video_id,))
            if not cursor.fetchone():
                return jsonify(success=False, message="Video not found")
            
            # Check for existing like
            cursor.execute("""
                SELECT id FROM user_likes 
                WHERE video_id = ? AND username = ?
            """, (video_id, username))
            existing_like = cursor.fetchone()
            
            if existing_like:
                # Remove like
                cursor.execute("""
                    DELETE FROM user_likes 
                    WHERE video_id = ? AND username = ?
                """, (video_id, username))
                cursor.execute("""
                    UPDATE videos 
                    SET likes = likes - 1 
                    WHERE id = ?
                """, (video_id,))
                action = 'unliked'
            else:
                # Add like
                cursor.execute("""
                    INSERT INTO user_likes (video_id, username) 
                    VALUES (?, ?)
                """, (video_id, username))
                cursor.execute("""
                    UPDATE videos 
                    SET likes = likes + 1 
                    WHERE id = ?
                """, (video_id,))
                action = 'liked'
            
            conn.commit()
            
            # Get updated like count
            cursor.execute("SELECT likes FROM videos WHERE id = ?", (video_id,))
            new_likes = cursor.fetchone()[0]
            
            print(f"Action: {action}, New likes: {new_likes}")
            return jsonify(success=True, likes=new_likes, action=action)
            
    except Exception as e:
        print(f"Error in like route: {str(e)}")
        return jsonify(success=False, message=str(e))

@app.route('/comment', methods=['POST'])
def comment_video():
    data = request.json
    video_id = data.get("video_id")
    comment = data.get("comment")
    user = "test_user"  # Replace with real user authentication

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (video_id, user, comment) VALUES (?, ?, ?)", (video_id, user, comment))
        conn.commit()

    return jsonify(success=True)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(success=False, message="Username and password are required")

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            password_hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                         (username, password_hash))
            conn.commit()
        return jsonify(success=True)
    except sqlite3.IntegrityError:
        return jsonify(success=False, message="Username already exists")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(success=False, message="Username and password are required")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result and check_password_hash(result[0], password):
            session['username'] = username
            return jsonify(success=True)
        return jsonify(success=False, message="Invalid username or password")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos")
    print(cursor.fetchall())
