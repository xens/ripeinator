FROM        python:3.8.6-alpine
LABEL maintainer="Romain Aviolat <r.aviolat@gmail.com>"

COPY ripe.py  /bin/ripe
RUN pip install requests pyyaml
CMD sh
