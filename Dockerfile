FROM time_wiz_base:v1
MAINTAINER <lucknell3@gmail.com>
COPY --chown=joey:joey . /src/bot
CMD ["./run.sh"] 