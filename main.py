from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
with open("resume.txt","r", encoding="utf-8") as file:
    resume_text= file.read()
    print("----------RESUME-----------------")
    print(resume_text)
with open("job_description.txt","r", encoding="utf-8") as file:
    jd_text=file.read()
    print("----------JOB DESCRIPTION-----------------")
    print(jd_text)
documents=[resume_text,jd_text]
#print(documents)
tfidf=TfidfVectorizer()
vectors=tfidf.fit_transform(documents)
#print("----------TF-IDF VECTORS-----------------")
#print(vectors)
similarity=cosine_similarity(vectors[0:1],vectors[1:2])
print("----------SIMILARITY SCORE-----------------")
score=similarity[0][0]
p=score*100
print(f"Match Score = {p:.2f}%")

'''skills = ["python", "java", "react", "node.js", "mongodb", "docker", "aws", "rest apis"]
miss_skill=[]
for skill in skills:
    if skill not in resume_text.lower():
        miss_skill.append(skill)
print("Missing Skills:")
for i in range(len(miss_skill)):
    print(miss_skill[i])'''
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
    
print("JD SKILLS : ", jd_skill)
print("RESUME SKILLS : ", reume_skill)
print("MISSING SKILLS : ", miss_skill)

# suggatiions for missing skils
suggestions = {
    "docker": "Learn Docker and build containerized applications",
    "aws": "Learn AWS cloud services and deployment",
    "rest apis": "Build projects using REST APIs",
    "kubernetes": "Learn container orchestration with Kubernetes",
    "jenkins": "Learn CI/CD pipelines using Jenkins",
    "terraform": "Learn Infrastructure as Code using Terraform",
    "python": "It's better to focus more on leetcode problems on python."
}
print("----------SUGGESTIOINS---------")
for ms in miss_skill:
    print(suggestions.get(ms))



