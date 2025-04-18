# My Steps When Choosing and Implementing the Models

## _BEIR_

### Install the Dependency
cannot use conda, it always has some error, finally installed in local environment

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




hsydeMacBook-Pro:COMP631Project hsy$ openssl version
OpenSSL 3.4.1 11 Feb 2025 (Library: OpenSSL 3.4.1 11 Feb 2025)
hsydeMacBook-Pro:COMP631Project hsy$ openssl req -x509 -nodes -newkey rsa:4096 -keyout elasticsearch.key -out elasticsearch.crt -days 365
.+...+......+............+..............+.........+.......+..+......+.+......+..+...+...+............+++++++++++++++++++++++++++++++++++++++++++++*.......+....+..+....+...............+......+........+++++++++++++++++++++++++++++++++++++++++++++*.+.........+....+.....+......+.+............+.....+...+....+......+...+..........................+...+......+......+.+..............+.........+............+....+...+......+..............+..........+..+.........+.........+......+............+............................+..+............+..........+......+......+.........+...........+...+.+..+.........+.+..+..........+..................+................................+......+.+..............+......+.+...+......+.....+.+..+............+.+...+.....+............+....+..........................+...+.+...............+.....+.+.....+............+......+.+......+............+..+...+...+...............+............+...............+.+............+.....+....+.....+......+.......+...+.....+...+................+.....+......+......................+...+........+......+........................+....+...+........+....+.....................+.....+.+......+.........+...+..+....+......+.....+....+.....+....+........+....+.....+.........+.........+..................+.......+........+...+.......+...+...........+..........+.....+.+..+.......+.....+.............+.....+................+..+...+.......+.....+....+...+..+.+.................+......+....+..+......+....+...+........+.......+++++
......+.......+...+...+..............+...+...+.+......+...+..+............+......+.......+++++++++++++++++++++++++++++++++++++++++++++*...+......+...+...+........+....+..+.........+.+........+...+++++++++++++++++++++++++++++++++++++++++++++*..+.............+..+...+.+........+.+......+......+...+..+..........+..+..........+...........+....+..+.+..+.+......+........+.......+...........+...+....+...........+.+.....+...+.+......+.....+...+...+....+..............+............+....+...+..+..........+........+...+.......+..+..................+......+.......+.....+..........+...+........................+..+..........+...+..................+..............+.+..+.................................+...........................+.+..............+.+..+.............+..............+.+......+......+........+....+..+.+............+.....+.+..+.......+........+...+.......+...+......+....................+...+......+.+........+...+...+......+.+...+.........+........+.........+......+......................+..+.+..+...............+.+.....+.+...........+....+...+..+....+..+.............+...........+...+.+.....+.+.........+...........+.+..+.............+...+.....+.+...........+..................+....+...+.....+..................+.........+.......+.....+...............+...+...+......................+...........+.......+...+.........+..+....+......+.........+..+....+........+......+.+......+.................+...+..........+........+..........+........................+...+..+......+......+.+..+............+.+..+...............+.......+.....+......+...+.......+............+...........+..........+......+..............+................+.....+.........+...................+..+.+.....+....+.........+..............+...............+.+......+.........+......+...........+....+......+...........................+.....................+...........+++++
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:











打开docker: 

hsydeMacBook-Pro:~ hsy$ docker ps -a
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED      STATUS                     PORTS     NAMES
e3c4239a3fe3   docker.elastic.co/elasticsearch/elasticsearch:8.17.3   "/bin/tini -- /usr/l…"   2 days ago   Exited (143) 7 hours ago             es01
hsydeMacBook-Pro:~ hsy$ docker start e3c4239a3fe3
e3c4239a3fe3


hsydeMacBook-Pro:~ hsy$ pip3 install "numpy<2"
DEPRECATION: Loading egg at /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/ieeg-1.6-py3.11.egg is deprecated. pip 25.1 will enforce this behaviour change. A possible replacement is to use pip for package installation. Discussion can be found at https://github.com/pypa/pip/issues/12330
Collecting numpy<2
  Downloading numpy-1.26.4-cp311-cp311-macosx_10_9_x86_64.whl.metadata (61 kB)
Downloading numpy-1.26.4-cp311-cp311-macosx_10_9_x86_64.whl (20.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 20.6/20.6 MB 26.8 MB/s eta 0:00:00
Installing collected packages: numpy
  Attempting uninstall: numpy
    Found existing installation: numpy 2.2.2
    Uninstalling numpy-2.2.2:
      Successfully uninstalled numpy-2.2.2
Successfully installed numpy-1.26.4
hsydeMacBook-Pro:~ hsy$ 


###SSL 问题以及解决方法：
Elasticsearch 的 Python 客户端库（elasticsearch-py）默认可能不读取系统钥匙串，而是依赖 certifi。
钥匙串信任 ≠ Python 信任：MacOS 系统信任证书不直接影响 Python，需单独配置。
test.py的内容：
# import ssl
# print(ssl.get_default_verify_paths())

hsydeMacBook-Pro:COMP631Project hsy$ python3 test.py 
DefaultVerifyPaths(cafile='/Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem', capath=None, openssl_cafile_env='SSL_CERT_FILE', openssl_cafile='/Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem', openssl_capath_env='SSL_CERT_DIR', openssl_capath='/Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/certs')
hsydeMacBook-Pro:COMP631Project hsy$ sudo cp /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem.bak
Password:
hsydeMacBook-Pro:COMP631Project hsy$ sudo sh -c "cat /Users/hsy/http_ca.crt >> /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem"
hsydeMacBook-Pro:COMP631Project hsy$ grep "BEGIN CERTIFICATE" /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem
-----BEGIN CERTIFICATE-----
-----BEGIN CERTIFICATE-----
-----BEGIN CERTIFICATE-----

方法一：将证书合并到 Python 的 cert.pem
备份原始证书文件：
sudo cp /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem.bak
将自签名证书追加到 cert.pem：
sudo sh -c "cat /Users/hsy/http_ca.crt >> /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem"
验证合并结果：
grep "BEGIN CERTIFICATE" /Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem # 应能看到你的证书内容
重启 Python 进程。


可以通过 **代码内动态设置环境变量** 或 **使用 `.env` 文件** 来避免每次手动输入 `export`。以下是两种方法：

---

### **方法一：直接在代码中设置环境变量**
在代码开头使用 `os.environ` 动态设置变量，无需终端操作：

```python
import os

# 直接在代码中设置环境变量
os.environ["ES_USERNAME"] = "elastic"
os.environ["ES_PASSWORD"] = "dfp15E8oiP6HEOF+MUdx"
os.environ["ES_CA_CERTS"] = "/Users/hsy/http_ca.crt"

# 后续代码无需修改
from beir.retrieval.search.lexical import BM25Search as BM25

model = BM25(
    index_name="your-index-name",
    hostname="https://localhost:9200",
    language="german",
    initialize=True,
    number_of_shards=1
)
```

---

### **方法二：使用 `.env` 文件（推荐）**
通过 `.env` 文件管理敏感信息，避免硬编码在代码中：

1. **创建 `.env` 文件**：
   ```bash
   # 项目根目录下创建 .env 文件
   echo "ES_USERNAME=elastic" >> .env
   echo "ES_PASSWORD=dfp15E8oiP6HEOF+MUdx" >> .env
   echo "ES_CA_CERTS=/Users/hsy/http_ca.crt" >> .env
   ```

2. **安装 `python-dotenv` 包**：
   ```bash
   pip install python-dotenv
   ```

3. **在代码中加载 `.env` 文件**：
   ```python
   import os
   from dotenv import load_dotenv

   # 加载 .env 文件中的环境变量
   load_dotenv()  # 默认加载项目根目录的 .env 文件

   # 后续代码直接读取环境变量
   username = os.getenv("ES_USERNAME")
   password = os.getenv("ES_PASSWORD")
   ca_certs = os.getenv("ES_CA_CERTS")

   # 初始化 BM25 并传递认证信息（需根据实际代码调整）
   hostname = f"https://{username}:{password}@localhost:9200"
   model = BM25(
       index_name="your-index-name",
       hostname=hostname,
       language="german",
       initialize=True,
       number_of_shards=1
   )
   ```

---

### **注意事项**
1. **安全性**：
   - 不要将 `.env` 文件或硬编码的密码提交到版本控制（如 Git）中！在 `.gitignore` 中添加 `.env`。
   - 生产环境应使用密钥管理服务（如 AWS Secrets Manager、Vault）。

2. **优先级**：
   - 代码中设置的变量会覆盖 `.env` 文件和系统环境变量。

3. **Elasticsearch 客户端配置**：
   - 确保 `ElasticSearch` 类能读取 `os.environ` 中的变量（如 `ca_certs=os.getenv("ES_CA_CERTS")`）。

通过以上方法，可以彻底避免每次手动输入 `export`，同时保持代码的灵活性和安全性。





























(base) hsydeMacBook-Pro:COMP631Project hsy$ docker ps
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED        STATUS        PORTS                              NAMES
e3c4239a3fe3   docker.elastic.co/elasticsearch/elasticsearch:8.17.3   "/bin/tini -- /usr/l…"   42 hours ago   Up 42 hours   0.0.0.0:9200->9200/tcp, 9300/tcp   es01

(base) hsydeMacBook-Pro:COMP631Project hsy$ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' es01
172.18.0.2


🔹 1. 确保 Elasticsearch 运行正常
在终端运行：

curl -X GET "https://elastic:dfp15E8oiP6HEOF+MUdx@localhost:9200/_cat/health?v"
如果返回：
epoch      status
1700000000 green
说明 Elasticsearch 运行正常。

如果 Elasticsearch 没有运行，你需要启动它：
docker start my-elasticsearch
或者：
systemctl start elasticsearch

curl -k -u elastic:dfp15E8oiP6HEOF+MUdx https://localhost:9200



----------------------------------------------------------
Use conda environment
(base) hsydeMacBook-Pro:COMP631Project hsy$ conda env list

# conda environments:
#
base                 * /usr/local/Caskroom/miniforge/base
comp631                /usr/local/Caskroom/miniforge/base/envs/comp631

(base) hsydeMacBook-Pro:COMP631Project hsy$ conda activate comp631
(comp631) hsydeMacBook-Pro:COMP631Project hsy$


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





###_Connect to the datasets in Hugging face_

brew install miniforge
hsydeMacBook-Pro:Desktop hsy$ conda --version
conda 24.11.3
查看已安装的 Conda 环境
conda env list


3️⃣ 创建新环境
conda create --name myenv python=3.10
myenv 是环境名称，你可以换成任何你想要的名字
python=3.10 指定 Python 版本（可换成 3.9, 3.8 等）
创建环境后，你需要激活它：
conda activate myenv
退出环境：
conda deactivate

4️⃣ 安装软件包
在 conda 环境下安装软件包：
conda install numpy pandas scikit-learn
或安装特定版本：
conda install numpy=1.22
⚠️ 如果找不到包，可以加 -c conda-forge：
conda install -c conda-forge somepackage

5️⃣ 更新和卸载包
更新 conda：
conda update conda
更新所有包：
conda update --all
卸载包：
conda remove numpy
6️⃣ 删除环境
conda remove --name myenv --all
这将删除 myenv 环境及所有相关包。

我创建：
conda create --name comp631 python=3.12.0

#                                                                                                                                                              
# To activate this environment, use                                                                                                                            
#                                                                                                                                                              
#     $ conda activate comp631                                                                                                                                 
#                                                                                                                                                              
# To deactivate an active environment, use                                                                                                                     
#                                                                                                                                                              
#     $ conda deactivate 

conda init
conda activate comp631
(comp631) hsydeMacBook-Pro:Desktop hsy$ which python                                                                                          
/Users/hsy/.pyenv/versions/pypy3.10-7.3.12/bin/python                                                                                         
(comp631) hsydeMacBook-Pro:Desktop hsy$ conda deactivate                                                                                                                                (comp631) hsydeMacBook-Pro:Desktop hsy$ conda activate comp631                                                                                
(comp631) hsydeMacBook-Pro:Desktop hsy$ export PATH="/usr/local/Caskroom/miniforge/base/envs/comp631/bin:$PATH"                               
(comp631) hsydeMacBook-Pro:Desktop hsy$ which python                                                                                          
/usr/local/Caskroom/miniforge/base/envs/comp631/bin/python                                                                                    
(comp631) hsydeMacBook-Pro:Desktop hsy$ pip install datasets 




