print("=========================================================================")
print("SMART RESUME ANALYZER")
print("=========================================================================")
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
with open("resume.txt","r", encoding="utf-8") as file:
    resume_text= file.read()
with open("job_description.txt","r", encoding="utf-8") as file:
    jd_text=file.read()
documents=[resume_text,jd_text]

tfidf=TfidfVectorizer()
vectors=tfidf.fit_transform(documents)

similarity=cosine_similarity(vectors[0:1],vectors[1:2])

score=similarity[0][0]
p=score*100
print(f"\nMatch Score = {p:.2f}%\n")

all_skills = [
    "python", "java", "react", "node.js", "mongodb", "docker", "aws", "rest apis", "kubernetes", 
    "jenkins", "terraform", "sql", "html", "css", "javascript"]
miss_skill=[]
jd_skill=[]
reume_skill=[]

#check skills in JD
for skill in range(len(all_skills)):
    if all_skills[skill] in jd_text.lower():
        jd_skill.append(all_skills[skill])

#check skills in resume
for skill in range(len(all_skills)):
    if all_skills[skill] in resume_text.lower():
        reume_skill.append(all_skills[skill])

#now compare jd_skills and resume_skills
for skill in jd_skill:
    if skill not in reume_skill:
        miss_skill.append(skill)

print("--------------------------------------------------------------------------")
print("JD Skills")
print("--------------------------------------------------------------------------")
for i in range(len(jd_skill)):
    print(f"• {jd_skill[i]}")

print("\n--------------------------------------------------------------------------")
print("Resume Skills")
print("--------------------------------------------------------------------------")
for i in range(len(reume_skill)):
    print(f"• {reume_skill[i]}")

print("\n--------------------------------------------------------------------------")
print("Missing Skills")
print("--------------------------------------------------------------------------")
for i in range(len(miss_skill)):
    print(f"• {miss_skill[i]}")
    
suggestions = {
    "docker": "Learn Docker and build containerized applications",
    "aws": "Learn AWS cloud services and deployment",
    "rest apis": "Build projects using REST APIs",
    "kubernetes": "Learn container orchestration with Kubernetes",
    "jenkins": "Learn CI/CD pipelines using Jenkins",
    "terraform": "Learn Infrastructure as Code using Terraform",
    "python": "It's better to focus more on leetcode problems on python."
}
print("\n--------------------------------------------------------------------------")
print("Suggested Improvements")
print("--------------------------------------------------------------------------")
for ms in miss_skill:
    print(f"• {suggestions.get(ms)}")


