FROM python:3.9-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    chromium \
    chromium-driver \
    varnish \
    supervisor 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .
COPY default.vcl /
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV DISPLAY=:99

####### CHANGE HERE ##########
ENV ADMIN_PASSWORD=xxx
ENV FLAG=kalmar{test_flag}
ENV HOSTNAME=localhost

ENV CHROME_OPTIONS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"

EXPOSE 80

# Flask app
CMD ["/usr/bin/supervisord"]