import os
from flask import Flask, render_template, request, send_file
from analyzer import extract_pdf_text
from analyzer import analyze_resume
from analyzer import skills_db
from analyzer import generate_summary
from pdf_generator import create_report

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        
        resume_file = request.files["resume"]
        resume_text = extract_pdf_text(resume_file)
        jd_text = ""
        # Option 1: User pasted JD
        if request.form["jd_text"].strip():
            jd_text = request.form["jd_text"]
            # Option 2: User uploaded file
        else:
            jd_file = request.files["jd_file"]
            if jd_file.filename == "":
                return "Please upload a JD file or paste a Job Description."
            if jd_file.filename.endswith(".pdf"):
                jd_text = extract_pdf_text(jd_file)
            elif jd_file.filename.endswith(".txt"):
                jd_text = jd_file.read().decode("utf-8")
            else:
                return "Please upload a PDF, TXT, or paste a Job Description."
        
        
        
        
        result = analyze_resume(resume_text,jd_text )
        summary = generate_summary(result)
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
        recommendations = []
        for skill in result["missing_skills"]:
            recommendations.append(skills_db.get(skill, f"Consider learning {skill}"))
        create_report(result, recommendations, rating, summary)

        return render_template("results.html",result=result,recommendations=recommendations,
                               rating=rating,rating_class=rating_class, summary=summary)
    return render_template("index.html")


@app.route("/download")
def download():

    if not os.path.exists("ATS_Report.pdf"):
        return "Please analyze a resume first."

    return send_file(
        "ATS_Report.pdf",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)