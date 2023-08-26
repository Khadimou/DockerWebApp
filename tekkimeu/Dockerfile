FROM python:3.10-slim

WORKDIR /usr/src/app

#prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure python output is sent directly to the terminal
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

RUN chmod +x /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

ENTRYPOINT ["sh","/usr/src/app/entrypoint.sh"]
