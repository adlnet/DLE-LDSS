# Dockerfile
FROM registry1.dso.mil/ironbank/opensource/python:v3.9
USER root
WORKDIR /home/python
COPY --chown=python:python . .

RUN if [ ! -f /tmp/debug.log ]; then touch /tmp/debug.log ; fi
RUN chmod a=rwx /tmp/debug.log

# copy source and install dependencies
RUN mkdir -p /tmp/app
RUN mkdir -p /tmp/app/openlxp-xms
RUN mkdir -p /tmp/shared

COPY --chown=python:python --chmod=755 requirements.txt start-server.sh start-app.sh /tmp/app/
COPY --chown=python:python .cache/python-packages /tmp/app/.cache/python-packages/
ENV PYTHONPATH /tmp/app/.cache/python-packages
ENV PATH $PATH:/tmp/app/.cache/python-packages/bin

# #apply permissions to scripts
# USER root
# RUN chmod +x /tmp/app/start-server.sh
# RUN chmod +x /tmp/app/start-app.sh
# USER python

COPY ./app /tmp/app/openlxp-xms/
WORKDIR /tmp/app/openlxp-xms/

RUN rm -rf /home/python/.cache/python-packages/future/backports/test/badcert.pem \
/home/python/.cache/python-packages/future/backports/test/badkey.pem \
/home/python/.cache/python-packages/future/backports/test/keycert.passwd.pem \
/home/python/.cache/python-packages/future/backports/test/keycert.pem \
/home/python/.cache/python-packages/future/backports/test/keycert2.pem \
/home/python/.cache/python-packages/future/backports/test/ssl_key.passwd.pem \
/home/python/.cache/python-packages/future/backports/test/ssl_key.pem \
/home/python/.cache/python-packages/tornado/test/test.key \
/home/python/.cache/python-packages/social_core/tests/testkey.pem \
/tmp/app/.cache/python-packages/future/backports/test/badcert.pem \ 
/tmp/app/.cache/python-packages/future/backports/test/badkey.pem \ 
/tmp/app/.cache/python-packages/future/backports/test/keycert.passwd.pem \ 
/tmp/app/.cache/python-packages/future/backports/test/keycert.pem \ 
/tmp/app/.cache/python-packages/future/backports/test/keycert2.pem \ 
/tmp/app/.cache/python-packages/future/backports/test/ssl_key.passwd.pem \ 
/tmp/app/.cache/python-packages/future/backports/test/ssl_key.pem \ 
/tmp/app/.cache/python-packages/social_core/tests/testkey.pem

USER python

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
