import csv
import io
import hashlib
import random
import string
import bcrypt
from datetime import datetime, timezone
from flask import Flask, request, make_response, render_template, redirect, url_for, send_from_directory, jsonify, Response, session
from pymongo import MongoClient
import helpers
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
mongo_client = MongoClient("mongo")
db = mongo_client["next-level"]
userpass = db["userpass"]
usertoken = db["usertoken"]
teampts = db["teampts"]
score_audit = db["score_audit"]

correct_answers = {
    "Q1": "AMDFH", "Q2": "LNSGE", "Q3": "RMSGT", "Q4": "SZZJK", "Q5": "TMMAR",
    "Q6": "TVSGH", "Q7": "ALPXZ", "Q8": "XMRKM", "Q9": "WHLPS", "Q10": "JSDRJ",
    "Q11": "XWEWY", "Q12": "PYMJT", "Q13": "BWUFL", "Q14": "WPPQB", "Q15": "DHJPK",
    "Q16": {
        'ZYOGW', 'JETCE', 'YRQOP', 'WSXXE', 'WVDFX', 'EQXMO', 'QGPHM', 'MWWYT', 'ZURAO', 'ZCTEH', 'EUKGB', 'MCJFG',
        'QMKUV', 'YOSSO', 'MYBXZ', 'RMKST', 'TCOOJ', 'UYBIO', 'CBPQH', 'SUPMI', 'UDCUE', 'RPSDO', 'LANMO', 'ZKTNO',
        'TIROT', 'ZBBKW', 'CUBWG', 'OTWMQ', 'GBYKG', 'EYTTN', 'UYDOK', 'LJFOZ', 'MSDGD', 'KEXBH', 'HOMRD', 'LBWKT',
        'BCCOA', 'LJTCZ', 'WIZNB', 'EBJAV', 'KHQTH', 'CVNZY', 'OUKFH', 'MMJLO', 'WLHIG', 'TXSIL', 'PEUGB', 'XVLHA',
        'MIVNT', 'MCSZK', 'BFJLT', 'BGZIX', 'GNNZT', 'HLRRC', 'LGEFI', 'MNKEM', 'NZTSF', 'QCPMW', 'RSKJW', 'RZASS',
        'SOJHR', 'THSFN', 'WHSKT', 'WJLIN', 'WPQNF', 'ALCQH','BNVTR','CEDKP','DQXLA','EPRVN','FJHQT','GAKLM','HZPWR',
        'IMCXD','JRNFA','KULPG','LTXQJ','MABRD','NQHCV','OPZTL','PJKMF','QAVTN','RCLPX','SNDQK','TKVJA','UMRQX','VPLCN',
        'WQJTA','XNPRL','YKCVQ','ZLMTN','AWRKS','BQPLD','CZNTR','DLMQF','EHXKT','FQWNR','GTPKC','HNCLQ','IRZPM','JKVQT',
        'KDMXR','LPNQV','MTRKA','NLBQX','OQKRM','PRXTV','QLNPC','RZKTA','STQVN','TNRLX','UQPMK','VCLQT','WNPRQ','XQKLM',
        'YTRNP','ZPVQC','AQNPL','BTRQX','CQLMV','DPNKR','ETVQZ'
    }
}

question_points = {
    "Q1": 10, "Q2": 10, "Q3": 30, "Q4": 10, "Q5": 10,
    "Q6": 10, "Q7": 20, "Q8": 50, "Q9": 50, "Q10": 50,
    "Q11": 20, "Q12": 50, "Q13": 10, "Q14": 10, "Q15": 10,
    "Q16": 10
}

def utc_now():
    return datetime.now(timezone.utc)


def format_timestamp(value):
    if not value:
        return ""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return str(value)


def get_leaderboard_rows(include_registered=False):
    score_rows = {entry.get("username", ""): entry for entry in teampts.find()}

    if include_registered:
        for user in userpass.find({}, {"username": 1}):
            username = user.get("username", "")
            if username and username not in score_rows:
                score_rows[username] = {
                    "username": username,
                    "points": 0,
                    "questions": [],
                    "updated_at": None
                }

    sorted_data = sorted(
        score_rows.values(),
        key=lambda entry: (-int(entry.get("points", 0)), entry.get("username", ""))
    )
    rows = []
    previous_points = None
    previous_rank = 0

    for index, entry in enumerate(sorted_data, start=1):
        points = entry.get("points", 0)
        if points == previous_points:
            rank = previous_rank
        else:
            rank = index
            previous_rank = rank
            previous_points = points

        rows.append({
            "rank": rank,
            "username": entry.get("username", ""),
            "points": points,
            "questions": entry.get("questions", []),
            "updated_at": format_timestamp(entry.get("updated_at"))
        })

    return rows


def admin_pin_is_configured():
    return bool(os.environ.get("NEXTLEVEL_ADMIN_PIN"))


def admin_is_authenticated():
    return bool(session.get("admin_authenticated"))


def latest_score_update():
    latest = score_audit.find_one(sort=[("created_at", -1)])
    return format_timestamp(latest.get("created_at")) if latest else ""


def get_audit_log(limit=25):
    entries = score_audit.find().sort("created_at", -1).limit(limit)
    return [{
        "created_at": format_timestamp(entry.get("created_at")),
        "username": entry.get("username", ""),
        "delta": entry.get("delta", 0),
        "previous_points": entry.get("previous_points", 0),
        "new_points": entry.get("new_points", 0),
        "reason": entry.get("reason", ""),
        "actor": entry.get("actor", "")
    } for entry in entries]


def get_or_create_team_score(username):
    team_data = teampts.find_one({"username": username})
    if team_data:
        return team_data

    if not userpass.find_one({"username": username}):
        return None

    team_data = {
        "username": username,
        "used_q16_codes": [],
        "questions": [],
        "points": 0,
        "updated_at": None
    }
    teampts.insert_one(team_data)
    return team_data

@app.route('/')
def index():
    visits = int(request.cookies.get('visits', 0)) + 1
    response = make_response(render_template('index.html'))
    response.set_cookie('visits', str(visits), max_age=3600)
    return response

@app.route('/game')
def game():
    user = ""
    token = request.cookies.get('token')
    questions_answered_correctly = []
    all_q16_used = False
    if token:
        user_data = usertoken.find_one({"token": token})
        if user_data:
            user = user_data.get("username", "")
            team_data = teampts.find_one({"username": user})
            if team_data:
                questions_answered_correctly = team_data.get("questions", [])
                used_q16_codes = team_data.get("used_q16_codes", [])
                all_q16_used = set(used_q16_codes) == set(correct_answers["Q16"])
    return render_template('game.html', team=user, questions_correct=questions_answered_correctly,
                           all_q16_used=all_q16_used)

@app.route('/leaderboard')
def leaderboard():
    response = make_response(render_template(
        'leaderboard.html',
        leaderboard=get_leaderboard_rows(),
        last_updated=latest_score_update()
    ))
    visits = int(request.cookies.get('visits', 0)) + 1
    response.set_cookie('visits', str(visits), max_age=3600)
    return response

@app.route('/leaderboard_data')
def leaderboard_data():
    return jsonify({
        "generated_at": format_timestamp(utc_now()),
        "last_updated": latest_score_update(),
        "leaderboard": get_leaderboard_rows()
    })

@app.route('/mentors')
def mentors():
    visits = int(request.cookies.get('visits', 0)) + 1
    response = make_response(render_template('mentors.html'))
    response.set_cookie('visits', str(visits), max_age=3600)
    return response

@app.route('/login')
def login():
    visits = int(request.cookies.get('visits', 0)) + 1
    response = make_response(render_template('login.html'))
    response.set_cookie('visits', str(visits), max_age=3600)
    return response

@app.route('/about')
def about():
    visits = int(request.cookies.get('visits', 0)) + 1
    response = make_response(render_template('about.html'))
    response.set_cookie('visits', str(visits), max_age=3600)
    return response

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if not admin_pin_is_configured():
        return render_template(
            'admin_login.html',
            error="Admin access is disabled until NEXTLEVEL_ADMIN_PIN is configured."
        ), 503

    error = ""
    if request.method == 'POST':
        pin = request.form.get('pin', '')
        if pin == os.environ.get("NEXTLEVEL_ADMIN_PIN"):
            session["admin_authenticated"] = True
            return redirect(url_for('admin_dashboard'))
        error = "The admin PIN was not accepted."

    return render_template('admin_login.html', error=error)

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop("admin_authenticated", None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not admin_is_authenticated():
        return redirect(url_for('admin_login'))

    return render_template(
        'admin.html',
        teams=get_leaderboard_rows(include_registered=True),
        audit_log=get_audit_log()
    )

@app.route('/admin/scores/adjust', methods=['POST'])
def admin_adjust_score():
    if not admin_is_authenticated():
        return redirect(url_for('admin_login'))

    username = request.form.get('username', '').strip()
    reason = request.form.get('reason', '').strip()
    actor = request.form.get('actor', '').strip() or "Event staff"

    try:
        requested_delta = int(request.form.get('delta', '0'))
    except ValueError:
        return "Point adjustment must be a whole number.", 400

    if not username:
        return "Team is required.", 400
    if not reason:
        return "Reason is required.", 400
    if requested_delta == 0:
        return "Point adjustment cannot be zero.", 400

    team_data = get_or_create_team_score(username)
    if not team_data:
        return "Team not found.", 404

    previous_points = int(team_data.get("points", 0))
    new_points = max(0, previous_points + requested_delta)
    actual_delta = new_points - previous_points
    changed_at = utc_now()

    teampts.update_one(
        {"username": username},
        {"$set": {"points": new_points, "updated_at": changed_at}}
    )
    score_audit.insert_one({
        "username": username,
        "delta": actual_delta,
        "requested_delta": requested_delta,
        "previous_points": previous_points,
        "new_points": new_points,
        "reason": reason,
        "actor": actor,
        "created_at": changed_at
    })

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export/scores.csv')
def admin_export_scores():
    if not admin_is_authenticated():
        return redirect(url_for('admin_login'))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["rank", "team", "points", "questions_completed", "last_updated"])
    for row in get_leaderboard_rows(include_registered=True):
        writer.writerow([
            row["rank"],
            row["username"],
            row["points"],
            len(row["questions"]),
            row["updated_at"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=next-level-scores.csv"}
    )

@app.route('/registeruser', methods=['POST'])
def register_user():
    username = request.form.get('username')
    password = request.form.get('regpass')
    if not helpers.is_valid_input(username) or not helpers.is_valid_input(password):
        return "Invalid input", 400

    if userpass.find_one({"username": username}):
        return "Username already exists", 400

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    userpass.insert_one({"username": username, "password": password_hash})
    return redirect(url_for('login'))

@app.route('/loginuser', methods=['POST'])
def login_user():
    username = request.form.get('usernamel')
    password = request.form.get('regpassl')

    if not helpers.is_valid_input(username) or not helpers.is_valid_input(password):
        return "Invalid input", 400

    user = userpass.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=200))
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        usertoken.insert_one({"username": username, "token": token_hash})
        response = make_response(redirect(url_for('game')))
        response.set_cookie('token', token_hash, max_age=3600)
        return response
    else:
        return "Username not found or password is incorrect", 400

@app.route('/submit', methods=['POST'])
def submit():
    token = request.cookies.get('token')
    if not token:
        return "Please Login", 403

    user_data = usertoken.find_one({"token": token})
    if not user_data:
        return "User not authenticated", 403

    username = user_data["username"]
    team_data = teampts.find_one({"username": username})
    if not team_data:
        team_data = {"username": username, "used_q16_codes": [], "questions": [], "points": 0}
        teampts.insert_one(team_data)

    team_used_q16_codes = team_data.get("used_q16_codes", [])
    team_answered_questions = team_data.get("questions", [])

    questions_correct = []
    total_points = 0

    for q, answer in correct_answers.items():
        user_answer = request.form.get(q)
        if q == "Q16":
            # Check if the code has been used by any team
            code_used_by_other_team = teampts.find_one({"used_q16_codes": user_answer})
            if user_answer in answer and user_answer not in team_used_q16_codes and not code_used_by_other_team:
                team_used_q16_codes.append(user_answer)
                questions_correct.append(q)
                total_points += question_points[q]
            elif code_used_by_other_team:
                return f"Code {user_answer} has already been used by another team.", 400
        else:
            if user_answer == answer and q not in team_answered_questions:
                questions_correct.append(q)
                total_points += question_points[q]

    if questions_correct:
        teampts.update_one(
            {"username": username},
            {
                "$addToSet": {"questions": {"$each": questions_correct}},
                "$set": {"used_q16_codes": team_used_q16_codes, "updated_at": utc_now()},
                "$inc": {"points": total_points}
            },
            upsert=True
        )

    return redirect(url_for('leaderboard'))

@app.route('/assets/img/mentors/<filename>')
def mentor_image(filename):
    return send_from_directory('static/img/mentors', filename)

@app.route('/assets/img/staffs/<filename>')
def staffs_image(filename):
    return send_from_directory('static/img/staffs', filename)

@app.route('/assets/img/others/<filename>')
def other_image(filename):
    return send_from_directory('static/img/others', filename)


@app.route("/conferences")
def conferences():
    images = [
        "img/conferences/conference_01.png",
        "img/conferences/conference_02.png",
        "img/conferences/conference_03.png",
        "img/conferences/conference_04.png",
        "img/conferences/conference_05.png",
        "img/conferences/conference_06.png",
        "img/conferences/conference_07.png",
        "img/conferences/conference_08.png",
        "img/conferences/conference_09.png",
        "img/conferences/conference_10.png",
        "img/conferences/conference_11.png",
        "img/conferences/conference_12.png",
        "img/conferences/conference_13.png",

    ]
    return render_template(
        "conferences.html",
        images=images,
        title="Conference Highlights"
    )



def register_users_from_json():
    json_file_path = 'users.json'
    try:
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file_path}' is not a valid JSON.")
        return

    for entry in json_data:
        username = entry.get("Username")
        password = entry.get("Password")

        if not helpers.is_valid_input(username) or not helpers.is_valid_input(password):
            print(f"Invalid input for user: {username}")
            continue

        if userpass.find_one({"username": username}):
            print(f"Username '{username}' already exists")
            continue

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        userpass.insert_one({"username": username, "password": password_hash})
        print(f"Registered user: {username}")

if os.environ.get("NEXTLEVEL_SKIP_USER_SEED") != "1":
    register_users_from_json()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
