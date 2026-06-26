from flask import Flask, render_template, request, session, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('index.html')


# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,email,password) VALUES(?,?,?)",
            (username, email, password)
        )

        conn.commit()
        conn.close()

        return "Registration Successful!"

    return render_template('register.html')
# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()

        conn.close()

        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Login"

    return render_template('login.html')

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM submissions WHERE username=?",
        (session['username'],)
    )
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT MAX(score) FROM submissions WHERE username=?",
        (session['username'],)
    )
    best = cur.fetchone()[0]

    if best is None:
        best = 0

    conn.close()

    return render_template(
        'dashboard.html',
        total=total,
        best=best
    )

@app.route('/profile')
def profile():

    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT username, email FROM users WHERE username=?",
        (session['username'],)
    )
    user = cur.fetchone()

    # Number of submissions
    cur.execute(
        "SELECT COUNT(*) FROM submissions WHERE username=?",
        (session['username'],)
    )
    total = cur.fetchone()[0]

    # Highest score
    cur.execute(
        "SELECT MAX(score) FROM submissions WHERE username=?",
        (session['username'],)
    )
    best = cur.fetchone()[0]

    if best is None:
        best = 0

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        total=total,
        best=best
    )


# ---------------- CONTEST ----------------

@app.route('/contest')
def contest():

    if 'username' not in session:
        return redirect('/login')

    return render_template('contest.html')


# ---------------- SUBMIT ----------------

@app.route('/submit', methods=['POST'])
def submit():

    if 'username' not in session:
        return redirect('/login')

    code = request.form['code']

    if len(code) > 300:
        score = 100
    elif len(code) > 200:
        score = 80
    elif len(code) > 100:
        score = 60
    elif len(code) > 50:
        score = 40
    else:
        score = 20

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO submissions(username, score) VALUES(?, ?)",
        (session['username'], score)
    )

    conn.commit()
    conn.close()

    return render_template("result.html", score=score)


# ---------------- LEADERBOARD ----------------

@app.route('/leaderboard')
def leaderboard():

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT username, MAX(score)
        FROM submissions
        GROUP BY username
        ORDER BY MAX(score) DESC
    """)

    data = cur.fetchall()

    conn.close()

    return render_template('leaderboard.html', data=data)


# ---------------- ADMIN ----------------

@app.route('/admin')
def admin():

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("""
        SELECT username, MAX(score)
        FROM submissions
        GROUP BY username
        ORDER BY MAX(score) DESC
    """)

    scores = cur.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        users=users,
        scores=scores
    )
@app.route('/history')
def history():

    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT score
        FROM submissions
        WHERE username=?
        ORDER BY rowid DESC
    """, (session['username'],))

    history = cur.fetchall()
    print("Logged in user:", session['username'])
    print("History:", history)
    conn.close()

    return render_template("history.html", history=history)

if __name__ == '__main__':
    app.run(debug=True)
