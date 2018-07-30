FROM library/python

WORKDIR /home/geckodriver_installer

ADD . /home/geckodriver_installer

# Chromedriver 2.29 complains on Ubuntu about
# missing libnss3 and libgconf-2-4 libraries.
RUN apt-get -yqq update
RUN apt-get -yqq install libnss3 libgconf-2-4

RUN pip install -q -r requirements.txt

CMD tox