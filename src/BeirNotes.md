# My Steps When Choosing and Implementing the Models

## _BEIR_

### Install the Dependency
Use conda environment
(base) hsydeMacBook-Pro:COMP631Project hsy$ conda env list

# conda environments:
#
base                 * /usr/local/Caskroom/miniforge/base
comp631                /usr/local/Caskroom/miniforge/base/envs/comp631

(base) hsydeMacBook-Pro:COMP631Project hsy$ conda activate comp631
(comp631) hsydeMacBook-Pro:COMP631Project hsy$


The environment I used is **macOS Docker**. This follows the guide from the [Beir Github](https://github.com/beir-cellar/beir/wiki/Installing-beir).

1. Firstly, I installed the Beir repository:
   ```bash
   pip install beir
   ```
   Meet problems it seems like miss rust, so download
   brew install rust
   

3. Download Elasticsearch from [Elasticsearch Website](https://www.elastic.co/cn/downloads/elasticsearch):
   - [Docker version](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)

   ```bash
   docker network create elastic
   docker pull docker.elastic.co/elasticsearch/elasticsearch:8.17.3
   docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
   ```

### **Elasticsearch Setup**
#### **1️⃣ Create Docker Network and Pull Elasticsearch**
```bash
docker network create elastic
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.17.3
```

#### **2️⃣ Run Elasticsearch in Docker**
```bash
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:8.17.3
```
Output:
```
✅ Elasticsearch security features have been automatically configured!
✅ Authentication is enabled and cluster connections are encrypted.

ℹ️  Password for the elastic user (reset with `bin/elasticsearch-reset-password -u elastic`):
  dfp15E8oiP6HEOF+MUdx
```

#### **3️⃣ Copy SSL Certificate from Docker**
```bash
docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
```

#### **4️⃣ Import SSL Certificate on macOS**
- Open **Keychain Access**
- Select **System** and unlock it
- Click **File → Import Items...**
- Select **http_ca.crt**
- **Trust the certificate**:
  - Find `http_ca.crt` in Keychain
  - Double-click → Expand **Trust**
  - Set **"Always Trust"**

#### **5️⃣ Set Environment Variable**
```bash
export ELASTIC_PASSWORD="dfp15E8oiP6HEOF+MUdx"
```
This allows you to run commands without manually entering the password.

To make this setting permanent:
```bash
echo 'export ELASTIC_PASSWORD="dfp15E8oiP6HEOF+MUdx"' >> ~/.zshrc
source ~/.zshrc  # Reload terminal settings
```

#### **6️⃣ Test Elasticsearch Setup**
- Open a browser and visit:
  ```
  https://elastic:dfp15E8oiP6HEOF+MUdx@localhost:9200
  ```
- Alternatively, use `curl`:
  ```bash
  curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200
  ```
- Expected Output:
  ```json
  {
    "name": "e3c4239a3fe3",
    "cluster_name": "docker-cluster",
    "tagline": "You Know, for Search"
  }
  ```

✅ **Elasticsearch is now running successfully!** 


(base) hsydeMacBook-Pro:COMP631Project hsy$ docker ps
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED        STATUS        PORTS                              NAMES
e3c4239a3fe3   docker.elastic.co/elasticsearch/elasticsearch:8.17.3   "/bin/tini -- /usr/l…"   42 hours ago   Up 42 hours   0.0.0.0:9200->9200/tcp, 9300/tcp   es01

(base) hsydeMacBook-Pro:COMP631Project hsy$ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' es01
172.18.0.2




如果你想删除 Conda 环境
如果你不再需要 comp631 这个环境，并且想删除它，可以使用：
conda remove --name comp631 --all
conda remove --name beir_env --all
然后再运行：
conda env list
确认它已经被删除。


如果你要切换到另一个 Conda 环境
如果你想换到其他环境，比如 beir_env，可以运行：
conda activate beir_env
这样你就进入了新的环境。
删除本地环境的beir和缓存，避免冲突
pip3 uninstall -y beir
pip3 cache purge
python3 -m pip show beir

pip list 可以检所有用pip下载的东西


some simple queries:

{"_id": "q1", "text": "What are the psychological interpretations of dreaming about water?"}
{"_id": "q2", "text": "Cognitive neuroscience theories on lucid dreaming"}
{"_id": "q3", "text": "The impact of REM sleep on memory consolidation"}
{"_id": "q4", "text": "Symbolism of dreams in Freudian psychoanalysis"}
{"_id": "q5", "text": "How do emotions affect dream recall?"}
{"_id": "q6", "text": "Neuroscientific studies on nightmare disorders"}
{"_id": "q7", "text": "Machine learning applications in dream analysis"}
{"_id": "q8", "text": "Jungian dream analysis and its applications"}
{"_id": "q9", "text": "Differences between lucid dreaming and normal dreaming"}
{"_id": "q10", "text": "The role of subconscious mind in dream formation"}




