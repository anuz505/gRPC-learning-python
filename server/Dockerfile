FROM python
WORKDIR /app
COPY . .
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "app.py"]