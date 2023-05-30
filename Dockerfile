FROM python:3.8-slim-buster


WORKDIR /app
COPY . /app
RUN pip3 install -r /app/requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]