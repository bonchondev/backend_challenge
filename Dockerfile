FROM --platform=amd64 python

WORKDIR /app

COPY ./requirements.txt ./*.py /app/

RUN pip install -r requirements.txt

RUN python /app/dbsetup.py -m up 

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
