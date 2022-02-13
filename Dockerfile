FROM python:3.9.5-buster

WORKDIR /Megatron
RUN chmod 777 /Megatron
RUN apt-get update -y
RUN pip3 install -U pip
RUN curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
RUN sudo apt install nodejs
RUN npm install -g localtunnel
COPY requirements.txt .
RUN pip3 install --no-cache-dir -U -r requirements.txt
COPY . .
CMD python3 -m Megatron & lt --port 8000 --subdomain filetolinktelegrambot
