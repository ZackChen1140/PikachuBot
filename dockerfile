FROM python:3.9-buster

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "PikachuBot.py"]