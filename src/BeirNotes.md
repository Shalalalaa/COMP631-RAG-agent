# My steps when choosing and implement the models
## _BEIR_

### Install the dependency
The environment I used is MacOS Docker
This follows the guide from github website ["Beir Github"]
1. Firstly I installed the Beir repository
   ```!pip install beir```
3. dowload the Elasticsearch from [Elasticsearch Website](https://www.elastic.co/cn/downloads/elasticsearch)
   [Docker version](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)

   docker network create elastic
   docker pull docker.elastic.co/elasticsearch/elasticsearch:8.17.3
   docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .

hsydeMacBook-Pro:~ hsy$ docker network create elastic
6969065f055eb8d4cccf38382f76af0fa4f9da404cdab141909ca32edae7ebfe
hsydeMacBook-Pro:~ hsy$ docker pull docker.elastic.co/elasticsearch/elasticsearch:8.17.3
8.17.3: Pulling from elasticsearch/elasticsearch
8e24285bc7e9: Download complete 
4bb953b2341e: Download complete 
a0a8cf8ea932: Download complete 
c8e302a2e0d1: Download complete 
542cc10a95ab: Download complete 
ca2cb92388d3: Download complete 
712c04fdbd90: Download complete 
425da96d0239: Download complete 
4ca545ee6d5d: Download complete 
2920558bb9da: Download complete 
Digest: sha256:224c75e346bd745ce908f06a1cbad7bf10988961dcdcdfccb22556b3f856b3f0
Status: Downloaded newer image for docker.elastic.co/elasticsearch/elasticsearch:8.17.3
docker.elastic.co/elasticsearch/elasticsearch:8.17.3
hsydeMacBook-Pro:~ hsy$ docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:8.17.3
✅ Elasticsearch security features have been automatically configured!
✅ Authentication is enabled and cluster connections are encrypted.

ℹ️  Password for the elastic user (reset with `bin/elasticsearch-reset-password -u elastic`):
  dfp15E8oiP6HEOF+MUdx

ℹ️  HTTP CA certificate SHA-256 fingerprint:
  6393f4a9c52e335fef49550077630280377aa94d62304ba8620661bcd4e794d3

ℹ️  Configure Kibana to use this cluster:
• Run Kibana and click the configuration link in the terminal when Kibana starts.
• Copy the following enrollment token and paste it into Kibana in your browser (valid for the next 30 minutes):
  eyJ2ZXIiOiI4LjE0LjAiLCJhZHIiOlsiMTcyLjE4LjAuMjo5MjAwIl0sImZnciI6IjYzOTNmNGE5YzUyZTMzNWZlZjQ5NTUwMDc3NjMwMjgwMzc3YWE5NGQ2MjMwNGJhODYyMDY2MWJjZDRlNzk0ZDMiLCJrZXkiOiJEOHktZUpVQm9JRTdWUjZtV3FHbzpzYjRHaUE5ZFRXMkVHU3NnZUpBUTJBIn0=

ℹ️ Configure other nodes to join this cluster:
• Copy the following enrollment token and start new Elasticsearch nodes with `bin/elasticsearch --enrollment-token <token>` (valid for the next 30 minutes):
  eyJ2ZXIiOiI4LjE0LjAiLCJhZHIiOlsiMTcyLjE4LjAuMjo5MjAwIl0sImZnciI6IjYzOTNmNGE5YzUyZTMzNWZlZjQ5NTUwMDc3NjMwMjgwMzc3YWE5NGQ2MjMwNGJhODYyMDY2MWJjZDRlNzk0ZDMiLCJrZXkiOiJFY3ktZUpVQm9JRTdWUjZtV3FHcDpDZ0tROUpSTVEtV1hmOEwtVnlma05nIn0=

  If you're running in Docker, copy the enrollment token and run:
  `docker run -e "ENROLLMENT_TOKEN=<token>" docker.elastic.co/elasticsearch/elasticsearch:8.17.3`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━





🔹 1. 从 Docker 复制证书
首先，你需要把 http_ca.crt 证书从容器中复制到本地：

docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
现在 http_ca.crt 文件应该在你当前的 终端工作目录 中。

🔹 2. 在 macOS 上导入证书
方法 1：使用 Keychain Access（钥匙串访问）手动导入
打开“钥匙串访问”：

在 macOS 上 按 Command + Space，输入 “钥匙串访问”（Keychain Access），然后回车打开。
选择系统证书存储：

在左上角，点击 “系统”（System）。

导入 http_ca.crt 证书：

点击 “file” → “import items”
选择你刚刚复制的 http_ca.crt
点击 “打开” 进行导入
信任该证书：

在钥匙串访问中，找到 http_ca.crt，双击打开
展开 “信任” 选项
在 “使用此证书时” 选择 “始终信任”
关闭窗口，系统可能会要求输入密码以确认更改




   
   
5. Check if Elasticsearch can run?
   check local machine:
   https://elastic:dfp15E8oiP6HEOF+MUdx@localhost:9200
   
6. 


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [Beir Github]: <https://github.com/beir-cellar/beir/wiki/Installing-beir>
