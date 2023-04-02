FROM python:3
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN apt update && apt install libgl1 -y
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
# CMD ["python", "app.py"]
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]

