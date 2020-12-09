import PyPDF2
import textract
import docx
import math
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import spacy
from spacy.matcher import Matcher
import spacy
import os
import sys
from pathlib import Path
from word2number import w2n
import numpy as np
import en_core_web_sm

nlp = en_core_web_sm.load()
from gensim import corpora, models, similarities

from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words('english'))
curdir = os.getcwd()
sys.path.append(curdir)
class resumeParsar():
    def __init__(self):
        self.full_path = os.getcwd()
        self.data_path = str(Path(self.full_path).parents[0]) + '/app/data/'
        self.df = pd.read_csv(self.data_path+'Skills.csv')
        self.skills = list(self.df['skills'])
        #self.skills = [' {0} '.format(elem) for elem in self.skills]
        self.df_hobbies = pd.read_csv(self.data_path+ 'Hobbies.csv')
        self.hobbies = list(self.df_hobbies['hobbies'])
        self.hobbies = [' {0} '.format(elem) for elem in self.hobbies]
        self.education = [
                'BE','B.E.', 'B.E', 'BS', 'B.S',
                'ME', 'M.E', 'M.E.', 'MS', 'M.S',
                'BTECH', 'B.TECH', 'M.TECH', 'MTECH','BCA','MCA','BSC','MSC','B.S.C','M.S.C','M.C.A' 
                'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','10TH','12TH','BACHELORS OF ENGINEERING','B.E','PG','PGP','PGPA'
    ,'PGDBA']
        self.df_locations = pd.read_csv(self.data_path + 'Locations.csv')
        self.locations = list(self.df_locations['Cities'])
        self.locations = [' {0} '.format(elem) for elem in self.locations]



    def getFileExtension(self,filename):
        extension = filename.split('.')[-1]
        return extension

    def checkExtension(self,filename):
        ValidExtension = ["pdf", "docx"]
        extension = self.getFileExtension(filename)
        if extension not in ValidExtension:
            print("Error:Not a valid File")
            return False
        else:
            return True

    def readpdfFile(self,filename):
        content = ""
        pdfFileObj = open(filename, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        noofpages = pdfReader.numPages
        for i in range(0, noofpages):
            page = pdfReader.getPage(i)
            content_page = page.extractText()
            content = content + ' ' + content_page
        content = content.encode('utf-8')
        return content

    def iter_hyperlink_rels(self,rels):
        hls = ""
        for rel in rels:
            if rels[rel].reltype == RT.HYPERLINK:
                hls = hls + str(rels[rel]._target)
        return hls

    def readtables(self,filename):
        document = docx.Document(filename)
        tables = document.tables
        data = []
        if len(tables) > 0:
            data = []
            for table in tables:
                keys = None
                for i, row in enumerate(table.rows):
                    text = (cell.text for cell in row.cells)

                    if i == 0:
                        keys = tuple(text)
                        continue
                    row_data = dict(zip(keys, text))
                    data.append(row_data)
        return data

    def extracttabletextskills(self,filename):
        document = docx.Document(filename)
        tables = document.tables
        data = []
        table_text = ""
        if len(tables) > 0:
            data = []
        for table in tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        table_text = table_text + " " + paragraph.text
            if any(skill in str(table_text).lower() for skill in self.skills):
                break
            return table_text

    def extracttabletexteducation(self,filename):
        document = docx.Document(filename)
        tables = document.tables
        data = []
        table_text = ""
        if len(tables) > 0:
            data = []
        for table in tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        table_text = table_text + " " + paragraph.text
            if any(edu in str(table_text).lower() for edu in self.education):
                break
            return table_text
        else:
            return ''

    def readdocxFile(self,filename):
        doc = docx.Document(filename)
        fullText = ""

        for para in doc.paragraphs:
            text_para = (para.text)
            fullText = fullText + ' ' + text_para
        rels = doc.part.rels
        hls = self.iter_hyperlink_rels(rels)
        fullText = fullText + " " + hls
        return fullText

    def extract_name(self,fulltext):
        name = re.findall("[\dA-Za-z+\' ']*", fulltext)[0]
        return name

    def extract_mobile_number(self,text):
        phone = re.findall(re.compile('([0-9]{10}|[0-9]{4}\s[0-9]{3}\s[0-9]{3})'), text)
        if phone:
            number = ''.join(phone[0])
            if len(number) > 10:
                return '+' + number
            else:
                return number

    def extract_email(self,text):
        email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
        if email:
            try:
                return email
            except IndexError:
                return None

    def extract_primary_secondry_skill(self,filename):
        primary_skill = ''
        secondry_skill = ''
        count = 0
        doc = docx.Document(filename)
        for para in doc.paragraphs:
            text_para = (para.text)
            if any(skill in str(text_para).lower() for skill in self.skills) and count < 3:
                primary_skill = primary_skill + ',' + str(
                    [skill for skill in self.skills if (skill in str(text_para).lower())]).replace('[', '').replace(']',
                                                                                                               '').replace(
                    '\'', '').replace(', ', ',').strip()
                count = count + 1
            elif any(skill in str(text_para).lower() for skill in self.skills) and count > 2:
                secondry_skill = secondry_skill + ',' + str(
                    [skill for skill in self.skills if (skill in str(text_para).lower())]).replace('[', '').replace(']',
                                                                                                               '').replace(
                    '\'', '').replace(', ', ',').strip()
                count = count + 1
        primary_skill = ','.join(set(primary_skill.split(',')))
        secondry_skill = ','.join(set(secondry_skill.split(',')))
        return primary_skill, secondry_skill

    def extract_current_preferred_location(self,filename):
        Current_Location = ''
        Preferred_Location = ''
        count = 0
        doc = docx.Document(filename)
        for para in doc.paragraphs:
            text_para = (para.text)
            if any(str(location) in str(text_para).lower() for location in self.locations) and count < 2:
                Current_Location = Current_Location + ',' + str(
                    [str(location) for location in self.locations if (str(location) in str(text_para).lower())]).replace('[', '').replace(']',
                                                                                                               '').replace(
                    '\'', '').replace(', ', ',').strip()
                count = count + 1
            elif any(str(location) in str(text_para).lower() for location in self.locations) and count >= 2:
                Preferred_Location = Preferred_Location + ',' + str(
                    [str(location) for location in self.locations if (str(location) in str(text_para).lower())]).replace('[', '').replace(']',
                                                                                                               '').replace(
                    '\'', '').replace(', ', ',').strip()
                count = count + 1
        Current_Location = ','.join(set(Current_Location.split(',')))
        Preferred_Location = ','.join(set(Preferred_Location.split(',')))
        return Current_Location, Preferred_Location

    def extract_location(self,resume_text):
        location_all = ''
        if any(str(location) in str(resume_text).lower() for location in self.locations):
            location_all = location_all + ',' + str([str(location) for location in self.locations if (str(location) in str(resume_text).lower())]).replace('[','').replace(']','').replace('\'', '').replace(', ', ',').strip()
        return location_all

    def extract_hobbies(self,resume_text):
        hobbies_all = ''
        if any(str(hobby) in str(resume_text).lower() for hobby in self.hobbies):
            hobbies_all = hobbies_all + ',' + str([str(hobby) for hobby in self.hobbies if (str(hobby) in str(resume_text).lower())]).replace('[','').replace(']','').replace('\'', '').replace(', ', ',').strip()
        return hobbies_all

    def visa_check(self,resume_text):
        visa_all=''
        visas = ['h1b','h1n1','l1','schengen']
        if any(str(visa) in str(resume_text).lower() for visa in visas):
            visa_all = visa_all + ',' + str([str(visa) for visa in visas if (str(visa) in str(resume_text).lower())]).replace('[',
                                                                                                            '').replace(
                ']', '').replace('\'', '').replace(', ', ',').strip()
        return visa_all


    def extract_skills(self,resume_text):
        skills_all = ''
        if any(skill in str(resume_text).lower() for skill in self.skills):
            skills_all = skills_all + ',' + str([skill for skill in self.skills if (skill in str(resume_text).lower())]).replace('[', '').replace(']','').replace('\'', '').replace(', ', ',').strip()
        return skills_all

    def extract_education(self,resume_text, filename):
        education = []
        escape_text = ['personal', 'course', 'certification', 'certifications', 'certificate', 'declaration', 'declare',
                       'skill', 'project', 'experience', 'projects']
        doc = docx.Document(filename)
        i = 0
        found_in_para = 0
        for para in doc.paragraphs:
            text_para = (para.text)
            if found_in_para == 1 and len(text_para) > 2:
                if any(ext in text_para.lower() for ext in escape_text):
                    found_in_para = 2
                else:
                    education.append(text_para)
            if 'education' in text_para.lower():
                found_in_para = 1
        if found_in_para == 0:
            nlp_text = nlp(resume_text)
            nlp_text = [sent.string.strip() for sent in nlp_text.sents]

            edu = {}
            for index, text in enumerate(nlp_text):
                for tex in text.split():
                    tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                    if tex.upper() in self.education and tex not in STOPWORDS:
                        edu[tex] = text + nlp_text[index + 1]
            # Extract year

            for key in edu.keys():
                year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
                if year:
                    education.append((key, ''.join(year[0])))
                else:
                    education.append(key)
        return education

    def getexpr(self,filename):
        text_exp = ""
        doc = docx.Document(filename)
        for para in doc.paragraphs:
            text_para = (para.text)
            match = re.findall(r'.*(\s[1-3][0-9]{3}|3000)', text_para)
            if match:
                if any(ext in text_para.upper() for ext in self.education):
                    text_exp = text_exp
                else:
                    text_exp = text_exp + "\n" + text_para + " "
        return text_exp

    def project_details(self,filename):
        valid_para = []
        doc = docx.Document(filename)
        for para in doc.paragraphs:
            text_para = (para.text)
            if len((text_para).strip()) > 5:
                valid_para.append(text_para)
        para_size = len(valid_para)
        end_index = math.ceil(para_size * 80 / 100)
        mylist = valid_para[5:end_index]
        projects = ('\n'.join(mylist))
        return projects
    def extractoverall_experience_through_yrs(self,filename):
        doc = docx.Document(filename)
        yrs = []
        for para in doc.paragraphs:
            text_para = (para.text)
            if 'education' not in text_para.lower():
                yrs.extend(re.findall('(\d{4})',text_para))
        if len(yrs)>1:
            yrs.sort()
            yrs = [int(i) for i in yrs]
            diffrence = np.diff(yrs)
            if diffrence[0]>15:
                #yrs = [str(i) for i in yrs]
                length = len(yrs)
                yrs = yrs[1:length]
        elif len(yrs)<1:
            yrs = []
        yrs = [int(i) for i in yrs]
        diff = np.diff(yrs)
        if len(diff)>0:
            return str(sum(diff))+' '+'years'
        else:
            return ""



    def extract_overall_experience(self,filename):
        doc = docx.Document(filename)
        yrs=[]
        for para in doc.paragraphs:
            text_para = (para.text)
            exp_tokens = ['yrs','years','year','exp','experience']
            for para in doc.paragraphs:
                text_para = (para.text)
                yrs=[int(i) for i in text_para.split() if i.isdigit() and int(i)<40]
                try:
                    flag = w2n.word_to_num(text_para)
                    if flag > 100:
                        flag = 0
                except:
                    flag = 0
                if any(ext in text_para.lower() for ext in exp_tokens) and (len(yrs)>0 or flag >0):
                    yrs.append(flag)
        if len(yrs)>0 and max(yrs) >0:
            return str(max(yrs))+' '+'years'
        else:
            #return self.extractoverall_experience_through_yrs(filename)
            return ''


    def generate_resume_result(self,filename):
        result = {}
        if self.checkExtension(filename):
            extension = self.getFileExtension(filename)
            if extension == 'docx':
                fulltext = self.readdocxFile(filename)
                tables = self.readtables(filename)
            else:
                fulltext = self.readpdfFile(filename)
            tabular_data = self.readtables(filename)
            if self.extract_name(fulltext):
                result['Name'] = self.extract_name(fulltext)
            if self.extract_mobile_number(fulltext):
                result['Mobile_number'] = self.extract_mobile_number(fulltext)
            if self.extract_email(fulltext):
                result['Email'] = self.extract_email(fulltext)
            if self.extract_skills(fulltext):
                result['Skills_All'] = self.extract_skills(fulltext)
            elif len(self.extracttabletextskills(fulltext, self.skills)) > 0:
                result['Skills_All'] = self.extracttabletextskills(fulltext, self.skills)
            if self.extract_education(fulltext, filename):
                result['Education'] = self.extract_education(fulltext, filename)
            elif len(self.extracttabletexteducation(filename)) > 0:
                result['Education'] = self.extracttabletexteducation(filename)
            result['Experience'] = self.getexpr(filename)
            Primary_skills, Secondary_skills = self.extract_primary_secondry_skill(filename)
            Current_Location,Preferred_Location = self.extract_current_preferred_location(filename)
            Overall_Experience = self.extract_overall_experience(filename)
            result['Primary_Skills'] = Primary_skills
            result['Secondary_Skills'] = Secondary_skills
            result['Current_Location'] = Current_Location
            result['Preferred_Location'] = self.extract_location(fulltext)
            result['Projects'] = self.project_details(filename)
            result['Overall_Experience'] = Overall_Experience
            result['Hobbies'] = self.extract_hobbies(fulltext)
            result['Visa'] = self.visa_check(fulltext)
        return result




if __name__ == "__main__":
    rp = resumeParsar()
    #filename= "//home//lid//Downloads//Omar_Nour_CV.docx"
    filename=sys.argv[1]
    print(filename)
    result = rp.generate_resume_result(filename)
    print(result)

