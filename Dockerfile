FROM debian:latest

RUN apt update && apt install -y tzdata locales

RUN ln -sf /bin/bash /bin/sh

ARG ZONE
ENV LANGUAGE=en_US.UTF-8 \
    TZ=$ZONE
RUN ln -sf /usr/share/zoneinfo/$ZONE /etc/localtime
RUN echo $ZONE >/etc/timezone

ARG USER_ID
ARG USER_NAME
ARG GROUP_ID
ARG GROUP_NAME
RUN groupadd -g $GROUP_ID $GROUP_NAME && \
    useradd $USER_NAME --create-home --home-dir /happypandax --no-log-init --no-user-group \
    --shell /bin/bash --uid $USER_ID --gid $GROUP_ID
WORKDIR /happypandax

ENV HPX_DOCKER=true
ENV HPX_DATA=/data
ENV HPX_CONTENT=/content
RUN mkdir $HPX_DATA $HPX_CONTENT
VOLUME ["/data", "/content"]

# Set permissions
ADD --chown=$USER_NAME:$GROUP_NAME docker/happypandax0.13.3.linux.tar.gz .
ADD --chown=$USER_NAME:$GROUP_NAME docker/startup.sh .
ADD --chown=$USER_NAME:$GROUP_NAME docker/config.yaml $HPX_DATA
RUN chown -R $USER_NAME:$GROUP_NAME $HPX_DATA && \
    chown -R $USER_NAME:$GROUP_NAME $HPX_CONTENT && \
    chown -R $USER_NAME:$GROUP_NAME /happypandax
RUN chmod +x ./startup.sh
#USER $USER_NAME # Do not. Container needs to start as root, then startup.sh run as hpx user

EXPOSE 7006
EXPOSE 7007
EXPOSE 7008
ENTRYPOINT ["./startup.sh"]