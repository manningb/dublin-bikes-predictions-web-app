FROM python:3.8-slim-buster
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt # Write Flask in this file
WORKDIR /app/flask_app
EXPOSE 5000
ENTRYPOINT [ "python" ] 
CMD ["app.py"]