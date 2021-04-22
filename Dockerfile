FROM python:3.8.1
RUN pip install -r requirements.txt

ENV APP_HOME /flask_app
WORKDIR $APP_HOME

COPY . /flask_app

ENTRYPOINT ["python app.py"]