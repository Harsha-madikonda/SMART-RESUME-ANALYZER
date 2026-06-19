from analyzer import skills_db
from analyzer import analyze_resume
print("=========================================================================")
print("                      SMART RESUME ANALYZER")



#reading resume and jd txts
with open("resume.txt","r", encoding="utf-8") as file:
    resume_text= file.read()
with open("job_description.txt","r", encoding="utf-8") as file:
    jd_text=file.read()

result = analyze_resume(
    resume_text,
    jd_text
)

print("--------------------------------------------------------------------------")
print("JD Skills:")
print("--------------------------------------------------------------------------")
for skill in result['jd_skills']:
    print(f"• {skill}")

print("\n-------------------------------------------------------------------------")
print("Resume Skills:")
print("---------------------------------------------------------------------------")
for skill in result['resume_skills']:
    print(f"• {skill}")

#print score
print("\n==========================================================================")
print("                             ATS REPORT")
print("============================================================================")
print(f"\nSemantic Match Score = {result['semantic_score']:.2f}%")
# skill match score
if result["total_jd_skills"] == 0:
    print("No recognizable skills found in the Job Description.")
else:
    print(f"Skill Match Score      = {result['skill_score']:.2f}%\n")

#Strenghts print
print("\n--------------------------------------------------------------------------")
print("Strengths:")
print("----------------------------------------------------------------------------")
for skill in result["strengths"]:
    print(f"✓ {skill}")

#print missing skills
print("\n--------------------------------------------------------------------------")
print("Missing Skills:")
print("----------------------------------------------------------------------------")
for skill in result["missing_skills"]:
    print(f"✗ {skill}")

print("\n--------------------------------------------------------------------------")
print("Recommendations:")
print("----------------------------------------------------------------------------")
for ms in result["missing_skills"]:
    print(f"• {skills_db.get(ms, f'Consider learning {ms}')}")


