from PyPDF2 import PdfReader
import csv
import spacy
from spacy.matcher import PhraseMatcher
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
nlp=spacy.load("en_core_web_sm")

#cleaning resume and jd
def clean_text(text):
    doc=nlp(text)
    clean_words=[]
    for words in doc:
        if not words.is_stop and not words.is_punct:
            clean_words.append(words.lemma_.lower())
    return " ".join(clean_words)


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
skill_aliases = {
    "react.js": "react",
    "reactjs": "react",
    "node js": "node.js",
    "express js": "express.js",
    "mongo db": "mongodb",
    "pl/sql": "sql",
    "structured query language": "sql"
}
def normalize_text(text):

    text = text.lower()

    for alias, skill in skill_aliases.items():
        text = text.replace(alias, skill)

    return text

# extracting skills from jd and resume
def extract_skills(text):
    text = normalize_text(text)
    doc = nlp(text)
    

    matches = matcher(doc)

    found_skills = set()

    for match_id, start, end in matches:
        found_skills.add(doc[start:end].text.lower())

    return sorted(list(found_skills))


def extract_pdf_text(pdf_file):

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def analyze_resume(resume_text, jd_text):
    clean_resume=clean_text(resume_text)
    clean_jd=clean_text(jd_text)
    documents=[clean_resume,clean_jd]
    tfidf=TfidfVectorizer()
    vectors=tfidf.fit_transform(documents)

    similarity=cosine_similarity(vectors[0:1],vectors[1:2])

    score=similarity[0][0]
    p=score*100
    jd_skill = extract_skills(jd_text)

    resume_skill = extract_skills(resume_text)
    miss_skill=[]
    #now compare jd_skills and resume_skills
    for skill in jd_skill:
        if skill not in resume_skill:
            miss_skill.append(skill)
# comapre jd and reusme to write strengths 
    strengths = []
 
    for skill in jd_skill:
        if skill in resume_skill:
            strengths.append(skill)
    matched_skills=len(strengths)
    total_jd_skills=len(jd_skill)
    if total_jd_skills > 0:
        skill_match_score = (matched_skills / total_jd_skills) * 100
    else:
        skill_match_score = 0
    return {
    "semantic_score": p,
    "skill_score": skill_match_score,
    "jd_skills": jd_skill,
    "resume_skills": resume_skill,
    "strengths": strengths,
    "missing_skills": miss_skill,
    "total_jd_skills":total_jd_skills}
    
