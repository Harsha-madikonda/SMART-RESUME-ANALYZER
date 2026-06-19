from spacy.matcher import PhraseMatcher
import csv
print("=========================================================================")
print("                      SMART RESUME ANALYZER")
#print("=========================================================================")
# Version 1.1
import spacy
nlp=spacy.load("en_core_web_sm")
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
with open("resume.txt","r", encoding="utf-8") as file:
    resume_text= file.read()
with open("job_description.txt","r", encoding="utf-8") as file:
    jd_text=file.read()

#removing stop words and punct
def clean_text(text):
    doc=nlp(text)
    clean_words=[]
    for words in doc:
        if not words.is_stop and not words.is_punct:
            clean_words.append(words.lemma_.lower())
    return " ".join(clean_words)
clean_resume=clean_text(resume_text)
clean_jd=clean_text(jd_text)
            
    
documents=[clean_resume,clean_jd]

tfidf=TfidfVectorizer()
vectors=tfidf.fit_transform(documents)

similarity=cosine_similarity(vectors[0:1],vectors[1:2])

score=similarity[0][0]
p=score*100


#csv file to dectionary
skills_db = {}

with open("skills.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        skills_db[row["skill"].lower()] = row["suggestion"]
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

patterns = []

for skill in skills_db.keys():
    patterns.append(nlp.make_doc(skill))

matcher.add("SKILLS", patterns)

def extract_skills(text):
    doc = nlp(text)

    matches = matcher(doc)

    found_skills = set()

    for match_id, start, end in matches:
        found_skills.add(doc[start:end].text.lower())

    return sorted(list(found_skills))


'''all_skills = [
    "python", "java", "react", "node.js", "mongodb", "docker", "aws", "rest apis", "kubernetes", 
    "jenkins", "terraform", "sql", "html", "css", "javascript"]'''
miss_skill=[]
jd_skill=[]
resume_skill=[]

jd_skill = extract_skills(jd_text)

resume_skill = extract_skills(resume_text)

#now compare jd_skills and resume_skills
for skill in jd_skill:
    if skill not in resume_skill:
        miss_skill.append(skill)
# comapre jd and reusme to write strengths 
strengths = []

for skill in jd_skill:
    if skill in resume_skill:
        strengths.append(skill)

print("--------------------------------------------------------------------------")
print("JD Skills:")
print("--------------------------------------------------------------------------")
for i in range(len(jd_skill)):
    print(f"• {jd_skill[i]}")

print("\n-------------------------------------------------------------------------")
print("Resume Skills:")
print("---------------------------------------------------------------------------")
for i in range(len(resume_skill)):
    print(f"• {resume_skill[i]}")

#print score
print("\n==========================================================================")
print("                             ATS REPORT")
print("============================================================================")
print(f"\nMatch Score = {p:.2f}%\n")

#Strenghts print
print("\n--------------------------------------------------------------------------")
print("Strengths:")
print("----------------------------------------------------------------------------")
for skill in strengths:
    print(f"✓ {skill}")

#print missing skills
print("\n--------------------------------------------------------------------------")
print("Missing Skills:")
print("----------------------------------------------------------------------------")
for skill in miss_skill:
    print(f"✗ {skill}")


'''suggestions = {
    "docker": "Learn Docker and build containerized applications",
    "aws": "Learn AWS cloud services and deployment",
    "rest apis": "Build projects using REST APIs",
    "kubernetes": "Learn container orchestration with Kubernetes",
    "jenkins": "Learn CI/CD pipelines using Jenkins",
    "terraform": "Learn Infrastructure as Code using Terraform",
    "python": "It's better to focus more on leetcode problems on python."
}'''
print("\n--------------------------------------------------------------------------")
print("Recommendations:")
print("----------------------------------------------------------------------------")
for ms in miss_skill:
    print(f"• {skills_db.get(ms, f'Consider learning {ms}')}")


