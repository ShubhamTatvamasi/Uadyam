import nltk
from gensim.models import Word2Vec
from nltk.corpus import stopwords
import re
import pandas as pd
import numpy as np
from scipy import spatial
import numpy as np
import os, sys
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from jd_parsar import jdParsar
from resume_parsar import resumeParsar
from pathlib import Path
import math
from collections import Counter
en_nlp = spacy.load('en')

class matcher():
    def __init__(self):
        print('Matching started')
        self.jdparsar=jdParsar()
        self.resumeparsar=resumeParsar()
        self.full_path = os.getcwd()
        self.data_path = str(Path(self.full_path).parents[0]) + '/app/data/'
        self.df = pd.read_csv(self.data_path + 'Skills.csv')
        skills = self.df['skills'].to_string()
        sentences = nltk.sent_tokenize(skills)
        sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        for i in range(len(sentences)):
            sentences[i] = [word for word in sentences[i] if word not in stopwords.words('english')]
        self.skill_2_vec = Word2Vec(sentences, min_count=1)

    def get_propn(self,text):
        nns=[]
        en_doc = en_nlp(u'' + text)
        for token in en_doc:
            if str(token.pos_) == 'PROPN' or str(token.pos_) == 'NOUN':
                nns.append(token.text)
        return nns

    def counter_cosine_similarity(self,c1, c2):
        terms = set(c1).union(c2)
        dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
        magA = math.sqrt(sum(c1.get(k, 0) ** 2 for k in terms))
        magB = math.sqrt(sum(c2.get(k, 0) ** 2 for k in terms))
        return dotprod / (magA * magB)



    def pre_process_text(self,text):
        text = re.sub(r'\[[0-9]*\]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.lower()
        text = re.sub(r'\d', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text


    def get_mean_vector(self,word2vec_model, words):
        # remove out-of-vocabulary words
        words = [word for word in words if word in word2vec_model.wv.vocab]
        if len(words) >= 1:
            return np.mean(word2vec_model[words], axis=0)
        else:
            return []


    def get_similarity_score(self,resume_vector, jd_vector):
        if len(resume_vector)==0 or len(jd_vector)==0:
            similarity=0
        else:
            similarity = 1 - spatial.distance.cosine(resume_vector, jd_vector)
        return similarity


    def get_parsed_jds(self,filename):
        result_jd = self.jdparsar.getparsedjd(filename)
        return result_jd

    def get_parsed_resume(self,resume_filename):
        resume_result = self.resumeparsar.generate_resume_result(resume_filename)
        return resume_result

    def get_similarity_overall(self,jd_result,resume_result,skill_2_vec):
        result={}
        print(resume_result['Primary_Skills'])
        print(jd_result['Primary_Skills'])
        resume_skill_all_vector = self.get_mean_vector(skill_2_vec, resume_result['Skills_All'])
        resume_primary_skill_vector = self.get_mean_vector( skill_2_vec, resume_result['Primary_Skills'])
        jd_skill_all_vector=self.get_mean_vector( skill_2_vec, jd_result['Skills_All'])
        jd_primary_skill_vector=self.get_mean_vector(skill_2_vec, jd_result['Primary_Skills'])
        result['Skill_All_Simalrity'] = self.get_similarity_score(resume_skill_all_vector, jd_skill_all_vector)
        result['Primary_Skill_Simalrity'] = self.get_similarity_score(resume_primary_skill_vector, jd_primary_skill_vector)
        result['Weighted_Skill_Similarity'] = ((result['Primary_Skill_Simalrity'] + result['Skill_All_Simalrity']/4))/2
        resume_text=resume_result['Projects']
        jd_text=result_jd['Title']+result_jd['Skill_With_Experince']
        resume_nouns = self.get_propn(resume_text)
        jd_nouns = self.get_propn(jd_text)
        c_resume = Counter(resume_nouns)
        c_jd = Counter(jd_nouns)
        result['Content_Similarity']=self.counter_cosine_similarity(c_resume,c_jd)
        ps_resume = Counter(resume_result['Primary_Skills'].split(','))
        ps_jd = Counter(jd_result['Primary_Skills'].split(','))
        result['Primary_Skill_exact_similarity']=self.counter_cosine_similarity(ps_resume,ps_jd)
        loc_resume =Counter(resume_result['Preferred_Location'].split(','))
        loc_jd = Counter(jd_result['Location'].split(','))
        result['Location_similarity']=self.counter_cosine_similarity(loc_resume,loc_jd)
        skill_all_resume=Counter(resume_result['Skills_All'].split(','))
        skill_all_jd=Counter(jd_result['Skills_All'].split(','))
        result['Skills_All_exact_similarity'] = self.counter_cosine_similarity(skill_all_resume,skill_all_jd)
        result['Over_all_Similarity']= (result['Skills_All_exact_similarity']/4 + result['Skill_All_Simalrity']/4+ \
                                       result['Primary_Skill_exact_similarity']/2+ \
                                       result['Primary_Skill_Simalrity']/2 + result['Content_Similarity'] +result['Location_similarity'])/3
        return result

if __name__ == "__main__":
    mp = matcher()
    resume_filename = os.getcwd() + "/downloads/Omar_Nour_CV.docx"
    resume_result=mp.get_parsed_resume(resume_filename)
    #jd_location = "//home//lid//Downloads//Job Description-20201121T112409Z-001//Job Description//*.docx"
    jd_file_name= os.getcwd() + "/downloads/DevOps_JD.docx"
    result_jd = mp.get_parsed_jds(jd_file_name)
    result=mp.get_similarity_overall(result_jd, resume_result, mp.skill_2_vec)
    print(result)
