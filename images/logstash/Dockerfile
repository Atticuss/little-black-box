FROM openjdk:8-jdk-slim-stretch

ENV OSS=true
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64/

# fix gpg issues
# https://github.com/inversepath/usbarmory-debian-base_image/issues/9#issuecomment-451635505
RUN mkdir ~/.gnupg && \
echo "disable-ipv6" >> ~/.gnupg/dirmngr.conf
 
RUN apt update && \
apt install curl gpg procps git -y && \
git clone https://github.com/elastic/logstash.git /usr/share/logstash
SHELL ["/bin/bash", "-l", "-c"]
RUN cd /usr/share/logstash && \
gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB && \
\curl -sSL https://get.rvm.io | bash -s stable --ruby=$(cat .ruby-version) && \ 
source /usr/local/rvm/scripts/rvm && \
usermod -a -G rvm root && \
git checkout 6.6 && \
gem install rake -v 12.2.1 && \
gem install bundler && \
rake bootstrap && \
rake plugin:install-default