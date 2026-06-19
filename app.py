from flask import Flask, render_template, request
from analyzer import extract_pdf_text
from analyzer import analyze_resume
from analyzer import extract_skills

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        resume_file = request.files["resume"]
        jd_file = request.files["jd"]
        resume_text = extract_pdf_text(resume_file)
        jd_text = jd_file.read().decode("utf-8")
        result = analyze_resume(
        resume_text,
        jd_text 
        )
        return f"""Semantic Match Score: {result["semantic_score"]:.2f}%<br>
        Skill Match Score: {result["skill_score"]:.2f}%<br>
        Missing Skills: {", ".join(result["missing_skills"])}
        """

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
