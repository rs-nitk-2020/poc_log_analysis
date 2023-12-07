FROM  python:3.11
WORKDIR /Warning-App
RUN apt-get update && apt-get -y upgrade &&  apt-get install -y git ca-certificates curl gnupg
# EXPOSE 8000
COPY requirements.txt ./
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . ./
ENTRYPOINT ["python3", "start_script.py"]
