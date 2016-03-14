FROM ubuntu:trusty
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y python-dev python-setuptools curl wget git vim 
RUN wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
RUN easy_install pip
RUN pip install django flask-sockets flask gunicorn httpclient requests ws4py
RUN echo -e '\n\n\n\n\n\n\n\n' | adduser --disabled-password --quiet me
USER me
WORKDIR /home/me
ADD arb.sh /home/me/arb.sh
