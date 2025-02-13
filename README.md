# COMP631-RAG-agent


## Resources:
[OPEN ALEX API](https://docs.openalex.org/how-to-use-the-api/api-overview)
<br>
[ZhouGongJieMeng](https://www.zgjmorg.com)

<br>
1. instlall the dependency to parsing the website to get the resource
    `pip install requests beautifulsoup4`
<br>
2. check how many documents I already stored
   `find data/ZhouGong -type f -name "*.json" | wc -l`

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

---------------------------------------------------- ignore this now ------------------------------------------------------------------------------
- [Markdown cheet sheet](https://www.markdownguide.org/cheat-sheet/)
1. install the database
MacOS
- download Docker to deploy
- install homebrew
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
- Install docker
    brew install --cask docker
- Install elasticsearch in docker
hsydeMacBook-Pro:~ hsy$ docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.5.3

hsydeMacBook-Pro:~ hsy$ docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.5.3
Unable to find image 'docker.elastic.co/elasticsearch/elasticsearch:8.5.3' locally
8.5.3: Pulling from elasticsearch/elasticsearch
8812ca00b1da: Download complete 
98900c908ae3: Download complete 
c74d6ab43b68: Download complete 
cea74c4ff319: Download complete 
ff6142af9229: Download complete 
52064ea931b6: Download complete 
d0eb0fe83e8a: Download complete 
e461483763d2: Download complete 
073cc5fd4b12: Download complete 
Digest: sha256:c9b454f73b1e2365d43f1f46f1b9464b981e5f98c1dd46fee01dbd5a4a446973
Status: Downloaded newer image for docker.elastic.co/elasticsearch/elasticsearch:8.5.3
e65f15b24a06f79ed7950de636689a195ed78e92e7e3948452542faf9471b8e0
hsydeMacBook-Pro:~ hsy$ curl -X GET "localhost:9200"
curl: (56) Recv failure: Connection reset by peer
hsydeMacBook-Pro:~ hsy$ docker ps
CONTAINER ID   IMAGE                                                 COMMAND                  CREATED          STATUS          PORTS                              NAMES
e65f15b24a06   docker.elastic.co/elasticsearch/elasticsearch:8.5.3   "/bin/tini -- /usr/l…"   56 seconds ago   Up 55 seconds   0.0.0.0:9200->9200/tcp, 9300/tcp   elasticsearch
hsydeMacBook-Pro:~ hsy$ 

Restart the elasticsearch by using the http, because the http is more for cloud develop, local will be easier to use http
hsydeMacBook-Pro:~ hsy$ docker run -d --name elasticsearch -p 9200:9200 \
>   -e "discovery.type=single-node" \
>   -e "xpack.security.enabled=false" \
>   docker.elastic.co/elasticsearch/elasticsearch:8.5.3
cc925b2c019009a7071ca3bd53c2e8a62feacc26a6531baf8743f27af62c2590
hsydeMacBook-Pro:~ hsy$ curl -X GET "http://localhost:9200"
{
  "name" : "cc925b2c0190",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "-yYKqdCQRx67S-v8hFihEw",
  "version" : {
    "number" : "8.5.3",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "4ed5ee9afac63de92ec98f404ccbed7d3ba9584e",
    "build_date" : "2022-12-05T18:22:22.226119656Z",
    "build_snapshot" : false,
    "lucene_version" : "9.4.2",
    "minimum_wire_compatibility_version" : "7.17.0",
    "minimum_index_compatibility_version" : "7.0.0"
  },
  "tagline" : "You Know, for Search"
}
hsydeMacBook-Pro:~ hsy$ 



- create index for the data
    curl -X PUT "http://localhost:9200/dreams" -H "Content-Type: application/json" -d '{
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
            "category": { "type": "keyword" },
            "title": { "type": "text" },
            "content": { "type": "text" }
            }
        }
    }'

check if insert successfully
http://localhost:9200/dreams/_search?pretty=true
出现乱码

在 macOS/Linux 终端里执行以下命令，确保 Terminal 支持 UTF-8
echo $LANG
终端没有返回任何东西，于是设置成支持它的
export LANG=en_US.UTF-8

创建索引
curl -X PUT "http://localhost:9200/dreams" -H "Content-Type: application/json" -d '{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "category": { "type": "keyword" },
      "title": { "type": "text" },
      "content": { "type": "text" }
    }
  }
}'
重新插入数据，确保 JSON 是 UTF-8
curl -X POST "http://localhost:9200/dreams/_doc/1" -H "Content-Type: application/json; charset=UTF-8" -d '{
  "category": "人物",
  "title": "梦见老师",
  "content": "梦见老师意味着你对自己期望很高..."
}'






