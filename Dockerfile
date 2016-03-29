FROM python:2.7-onbuild

COPY .  /app
WORKDIR /app

CMD ["python", "/app/low-sodium.py"]
