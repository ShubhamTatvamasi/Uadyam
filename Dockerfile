FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk;nltk.download('stopwords');nltk.download('punkt')"

RUN python -m spacy download en

COPY . .

RUN pip install resume_parser

RUN apt update && apt install antiword

ENTRYPOINT ["python"]
