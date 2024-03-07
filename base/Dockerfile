FROM archlinux:latest
MAINTAINER lucknell <lucknell3@gmail.com>
ENV TZ "America/Los_Angeles"
RUN pacman-key --refresh-keys
RUN pacman -Syu --noconfirm && pacman -S --noconfirm base-devel python python-pip
RUN mkdir -p /src/bot/ && mkdir -p /home/joey
RUN useradd -m -G wheel -s /bin/bash joey
RUN sed -Ei 's/^#\ (%wheel.*NOPASSWD.*)/\1/' /etc/sudoers
RUN chown joey:joey /src/bot/ && chown joey:joey /home/joey
COPY --chown=joey:joey requirements.txt /src/bot/.
USER joey
WORKDIR /src/bot
RUN pip3 install  --break-system-packages -r requirements.txt