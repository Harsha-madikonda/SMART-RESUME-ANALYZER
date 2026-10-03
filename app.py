import os
import re
import json
import uuid

from flask import (
    Flask, render_template, request, send_file,
    jsonify, session, redirect, url_for, abort
)

from analyzer import extract_pdf_text
from analyzer import analyze_resume
from analyzer import skills_db
from analyzer import generate_summary
from pdf_generator import create_report


app = Flask(__name__)

# Needed for session (remembers resume between pages)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")


# ============================================================
# FILE PATHS
# ============================================================

PRACTICE_QUESTIONS_FILE = os.path.join(
    app.root_path, "data", "practice_questions.json"
)

INTERVIEW_QUESTIONS_FILE = os.path.join(
    app.root_path, "data", "interview_questions.json"
)

CAREER_DATA_FILE = os.path.join(
    app.root_path, "data", "career_data.json"
)


# ============================================================
# CAREER PREPARATION HELPERS
# ============================================================

# Resume text is kept in server memory (cookies are too small).
# The session only stores a small id pointing to it.
RESUME_CACHE = {}


def save_resume_text(text):
    """Remember the latest resume text for this browser session."""
    rid = session.get("rid")

    if not rid:
        rid = uuid.uuid4().hex
        session["rid"] = rid

    RESUME_CACHE[rid] = text


def get_resume_text():
    """Get the resume text saved earlier (or empty string)."""
    return RESUME_CACHE.get(session.get("rid"), "")


def load_careers():
    with open(CAREER_DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def skill_in_text(skill, text):
    """Check if a skill (or any of its aliases) appears in text."""
    text = text.lower()

    names = [skill["name"]] + skill.get("aliases", [])

    for name in names:
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(name.lower())
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, text):
            return True

    return False


def analyze_career(career, resume_text, manual_skills):
    """Work out skills, gaps, readiness and roadmap status."""

    auto_detected = []

    if resume_text:
        for skill in career["skills"]:
            if skill_in_text(skill, resume_text):
                auto_detected.append(skill["name"])

    owned = set(auto_detected) | set(manual_skills)

    all_names = [s["name"] for s in career["skills"]]

    your_skills = [n for n in all_names if n in owned]
    missing_skills = [n for n in all_names if n not in owned]

    readiness = round(len(your_skills) / len(all_names) * 100) \
        if all_names else 0

    # Roadmap: done / next / todo
    roadmap = []
    next_found = False

    for step in career["roadmap"]:

        skill_name = step.get("skill")

        done = skill_name is None or skill_name in owned

        if skill_name is None:
            # Steps without a skill are "done" only if all before are done
            done = not next_found

        if done:
            status = "done"
        elif not next_found:
            status = "next"
            next_found = True
        else:
            status = "todo"

        roadmap.append({
            "name": step["name"],
            "status": status
        })

    if readiness >= 80:
        level = "Job Ready"
    elif readiness >= 50:
        level = "Getting There"
    elif readiness >= 25:
        level = "Beginner"
    else:
        level = "Just Starting"

    return {
        "auto_detected": auto_detected,
        "your_skills": your_skills,
        "missing_skills": missing_skills,
        "readiness": readiness,
        "level": level,
        "roadmap": roadmap
    }


# ============================================================
# HOME / RESUME ANALYZER
# ============================================================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # ----------------------------------------------------
        # Get Resume
        # ----------------------------------------------------

        resume_file = request.files["resume"]

        if resume_file.filename == "":
            return "Please upload a resume PDF."

        resume_text = extract_pdf_text(resume_file)

        # Remember resume so Career Preparation can use it
        save_resume_text(resume_text)


        # ----------------------------------------------------
        # Get Job Description
        # ----------------------------------------------------

        jd_text = ""

        # Option 1: User pasted Job Description

        if request.form["jd_text"].strip():

            jd_text = request.form["jd_text"]


        # Option 2: User uploaded Job Description file

        else:

            jd_file = request.files["jd_file"]

            if jd_file.filename == "":
                return "Please upload a JD file or paste a Job Description."

            # PDF Job Description

            if jd_file.filename.lower().endswith(".pdf"):

                jd_text = extract_pdf_text(jd_file)

            # TXT Job Description

            elif jd_file.filename.lower().endswith(".txt"):

                jd_text = jd_file.read().decode("utf-8")

            # Invalid file

            else:

                return "Please upload a PDF, TXT, or paste a Job Description."


        # ----------------------------------------------------
        # Analyze Resume
        # ----------------------------------------------------

        result = analyze_resume(
            resume_text,
            jd_text
        )


        # ----------------------------------------------------
        # Generate Summary
        # ----------------------------------------------------

        summary = generate_summary(result)


        # ----------------------------------------------------
        # Calculate Rating
        # ----------------------------------------------------

        score = result["skill_score"]

        if score >= 90:

            rating = "Excellent Match"
            rating_class = "score-good"

        elif score >= 70:

            rating = "Good Match"
            rating_class = "score-good"

        elif score >= 50:

            rating = "Moderate Match"
            rating_class = "score-average"

        else:

            rating = "Needs Improvement"
            rating_class = "score-poor"


        # ----------------------------------------------------
        # Generate Recommendations
        # ----------------------------------------------------

        recommendations = []

        for skill in result["missing_skills"]:

            recommendations.append(
                skills_db.get(
                    skill,
                    f"Consider learning {skill}"
                )
            )


        # ----------------------------------------------------
        # Create PDF Report
        # ----------------------------------------------------

        create_report(
            result,
            recommendations,
            rating,
            summary
        )


        # ----------------------------------------------------
        # Show Results Page
        # ----------------------------------------------------

        return render_template(
            "results.html",
            result=result,
            recommendations=recommendations,
            rating=rating,
            rating_class=rating_class,
            summary=summary
        )


    # --------------------------------------------------------
    # GET REQUEST
    # --------------------------------------------------------

    return render_template("index.html")


# ============================================================
# DOWNLOAD ATS REPORT
# ============================================================

@app.route("/download")
def download():

    if not os.path.exists("ATS_Report.pdf"):

        return "Please analyze a resume first."

    return send_file(
        "ATS_Report.pdf",
        as_attachment=True
    )


# ============================================================
# CAREER PREPARATION
# ============================================================

@app.route("/career")
def career():
    """Step 1: choose a career."""

    careers = load_careers()

    return render_template(
        "career.html",
        careers=careers,
        has_resume=bool(get_resume_text())
    )


@app.route("/career/<career_id>", methods=["GET", "POST"])
def career_detail(career_id):
    """Step 2: readiness, skills, roadmap for the chosen career."""

    careers = load_careers()

    if career_id not in careers:
        abort(404)

    # ---------------- POST: update resume / manual skills ----
    if request.method == "POST":

        resume_file = request.files.get("resume")

        if resume_file and resume_file.filename:

            if resume_file.filename.lower().endswith(".pdf"):
                save_resume_text(extract_pdf_text(resume_file))

        # Manual skills are stored per career
        manual_all = session.get("manual_skills", {})
        manual_all[career_id] = request.form.getlist("skills")
        session["manual_skills"] = manual_all

        return redirect(url_for("career_detail", career_id=career_id))

    # ---------------- GET: show page -------------------------
    career_info = careers[career_id]

    resume_text = get_resume_text()
    manual_skills = session.get("manual_skills", {}).get(career_id, [])

    analysis = analyze_career(career_info, resume_text, manual_skills)

    return render_template(
        "career_detail.html",
        career_id=career_id,
        career=career_info,
        analysis=analysis,
        manual_skills=manual_skills,
        has_resume=bool(resume_text)
    )


# ============================================================
# PRACTICE TEST PAGE
# ============================================================

@app.route("/practice")
def practice():

    return render_template("practice.html")


@app.route("/interview")
def interview():

    return render_template("interview.html")


# ============================================================
# PRACTICE TEST API
# ============================================================

@app.route("/api/practice")
def practice_api():

    category = request.args.get(
        "category",
        "python"
    ).lower()

    difficulty = request.args.get(
        "difficulty",
        "easy"
    ).lower()

    try:

        with open(
            PRACTICE_QUESTIONS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            question_bank = json.load(file)

    except FileNotFoundError:

        return jsonify({
            "success": False,
            "message": "Practice question bank not found."
        }), 500

    except json.JSONDecodeError:

        return jsonify({
            "success": False,
            "message": "questions.json contains invalid JSON."
        }), 500

    questions = question_bank.get(
        category,
        {}
    ).get(
        difficulty,
        []
    )

    if not questions:

        return jsonify({
            "success": False,
            "message": (
                "No questions available for "
                f"{category} - {difficulty} yet."
            )
        }), 404

    return jsonify({
        "success": True,
        "category": category,
        "difficulty": difficulty,
        "questions": questions
    })


# ============================================================
# INTERVIEW API
# ============================================================

@app.route("/api/interview")
def interview_api():

    role = request.args.get(
        "role",
        "fullstack"
    ).lower()

    difficulty = request.args.get(
        "difficulty",
        "easy"
    ).lower()

    try:

        with open(
            INTERVIEW_QUESTIONS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            question_bank = json.load(file)

    except FileNotFoundError:

        return jsonify({
            "success": False,
            "message": "Interview question bank not found."
        }), 500

    except json.JSONDecodeError:

        return jsonify({
            "success": False,
            "message": (
                "interview_questions.json "
                "contains invalid JSON."
            )
        }), 500

    common_questions = question_bank.get(
        "common",
        {}
    ).get(
        difficulty,
        []
    )

    role_questions = question_bank.get(
        role,
        {}
    ).get(
        difficulty,
        []
    )

    questions = (
        common_questions +
        role_questions
    )

    if not questions:

        return jsonify({
            "success": False,
            "message": (
                "No interview questions available for "
                f"{role} - {difficulty} yet."
            )
        }), 404

    return jsonify({
        "success": True,
        "role": role,
        "difficulty": difficulty,
        "questions": questions
    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)