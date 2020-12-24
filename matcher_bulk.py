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
from matcher import  matcher
import ast
en_nlp = spacy.load('en')

class matcher_bulk():
    def __init__(self):
        print('Bulk Matching started')
        self.mt = matcher()
    def match_bulk(self,resume_ls,jd_ls):
        result_final=[]
        for resume in resume_ls:
            try:
                resume = ast.literal_eval(resume)[0]
            except:
                resume = ast.literal_eval(resume)
            for jd in jd_ls:
                try:
                    jd = ast.literal_eval(jd)[0]
                except:
                    jd = ast.literal_eval(jd)
                result = self.mt.get_similarity_overall(jd, resume, self.mt.skill_2_vec)
                result_final.append(result)
        return result_final

if __name__ == "__main__":

    mb = matcher_bulk()
    resume_ls = open("/home/lid/resume.txt").readlines()
    jd_ls = open("/home/lid/JD.txt").readlines()
    result_final=mb.match_bulk(resume_ls, jd_ls)
    print(len(result_final))
    df = pd.DataFrame(result_final)
    print(df)


    





