from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from forms import CreateQuizForm, UploadQuizForm
import pandas as pd
from extensions import db  # Import db from extensions.py
from models import Quiz, Question, User  # Now this import works
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz.db"
app.config["UPLOAD_FOLDER"] = "data"
app.config["ALLOWED_EXTENSIONS"] = {"csv"}

# Initialize db with the app
db.init_app(app)

socketio = SocketIO(app)

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# Helper function to check file extensions
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create_quiz", methods=["GET", "POST"])
def create_quiz():
    form = CreateQuizForm()
    if form.validate_on_submit():
        quiz = Quiz(title=form.title.data, description=form.description.data)
        db.session.add(quiz)
        db.session.commit()

        for question in form.questions.data:
            q = Question(
                quiz_id=quiz.id,
                text=question["text"],
                option1=question["option1"],
                option2=question["option2"],
                option3=question["option3"],
                option4=question["option4"],
                correct_option=question["correct_option"],
            )
            db.session.add(q)

        db.session.commit()
        flash("Quiz created successfully!", "success")
        return redirect(url_for("home"))

    return render_template("create_quiz.html", form=form)


@app.route("/upload_quiz", methods=["GET", "POST"])
def upload_quiz():
    form = UploadQuizForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Process CSV file
            try:
                df = pd.read_csv(filepath)
                quiz = Quiz(
                    title=df.iloc[0]["title"], description=df.iloc[0]["description"]
                )
                db.session.add(quiz)
                db.session.commit()

                for _, row in df.iterrows():
                    question = Question(
                        quiz_id=quiz.id,
                        text=row["text"],
                        option1=row["option1"],
                        option2=row["option2"],
                        option3=row["option3"],
                        option4=row["option4"],
                        correct_option=row["correct_option"],
                    )
                    db.session.add(question)

                db.session.commit()
                flash("Quiz uploaded successfully!", "success")
            except Exception as e:
                flash(f"Error processing CSV: {e}", "danger")

            os.remove(filepath)  # Clean up uploaded file
            return redirect(url_for("home"))

    return render_template("upload_quiz.html", form=form)


@app.route("/join", methods=["POST"])
def join_quiz():
    quiz_code = request.form["quiz_code"]
    username = request.form["username"]

    quiz = Quiz.query.filter_by(id=quiz_code).first()
    if not quiz:
        flash("Quiz not found!", "danger")
        return redirect(url_for("home"))

    return redirect(url_for("quiz", quiz_code=quiz_code, username=username))


@app.route("/quiz/<quiz_code>/<username>")
def quiz(quiz_code, username):
    quiz = Quiz.query.get_or_404(quiz_code)
    return render_template("quiz.html", quiz=quiz, username=username)


@socketio.on("join")
def on_join(data):
    username = data["username"]
    quiz_code = data["quiz_code"]

    join_room(quiz_code)
    emit("message", f"{username} has joined the quiz.", room=quiz_code)


@socketio.on("submit_answer")
def on_submit_answer(data):
    username = data["username"]
    quiz_code = data["quiz_code"]
    answer = data["answer"]
    emit("answer_received", {"username": username, "answer": answer}, room=quiz_code)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
