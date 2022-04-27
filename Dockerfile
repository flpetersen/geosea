# Dockerfile , Image, Container
FROM python:3.9

COPY /src /src
COPY README.md /

WORKDIR /src

# requirements
RUN pip install obspy 

RUN pip3 install --upgrade setuptools pip

RUN pip3 install PyQt6==6.2.2 numpy==1.21.4 pandas==1.3.5 \
pyqtgraph==0.12.3 \
opencv-python==4.5.4.60 \
pytz==2021.3 \
PyYAML==6.0 \
python-dateutil==2.8.2 \
six==1.16.0

CMD [ "python", "main.py"]