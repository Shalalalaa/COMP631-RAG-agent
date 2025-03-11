Run Kibana
1. Pull the Kibana Docker image.
docker pull docker.elastic.co/kibana/kibana:8.17.3
hsydeMacBook-Pro:~ hsy$ docker pull docker.elastic.co/kibana/kibana:8.17.3
8.17.3: Pulling from kibana/kibana
0961e5ed6e0a: Download complete 
56c96bfa149e: Download complete 
2675abfb9d2f: Download complete 
8deb66cfd190: Download complete 
4ca545ee6d5d: Already exists 
f4f59eec995f: Download complete 
53b1f59a050f: Download complete 
07997af583d7: Download complete 
c109816ec202: Download complete 
2ffd3541d0b7: Download complete 
778b08e1783f: Download complete 
6ce04461e85c: Download complete 
Digest: sha256:7dfee7a14cf7de9f22285d9e9db3bf423c36f3f4a82c0dce7294b0fb1532c863
Status: Downloaded newer image for docker.elastic.co/kibana/kibana:8.17.3
docker.elastic.co/kibana/kibana:8.17.3


2. Optional: Verify the Kibana image’s signature.
wget https://artifacts.elastic.co/cosign.pub
cosign verify --key cosign.pub docker.elastic.co/kibana/kibana:8.17.3

3. Start a Kibana container.
docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.17.3

hsydeMacBook-Pro:~ hsy$ docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.17.3
Kibana is currently running with legacy OpenSSL providers enabled! For details and instructions on how to disable see https://www.elastic.co/guide/en/kibana/8.17/production.html#openssl-legacy-provider
{"log.level":"info","@timestamp":"2025-03-11T21:36:37.468Z","log.logger":"elastic-apm-node","ecs.version":"8.10.0","agentVersion":"4.10.0","env":{"pid":7,"proctitle":"/usr/share/kibana/bin/../node/glibc-217/bin/node","os":"linux 6.12.5-linuxkit","arch":"x64","host":"fd53e140f123","timezone":"UTC+00","runtime":"Node.js v20.18.2"},"config":{"active":{"source":"start","value":true},"breakdownMetrics":{"source":"start","value":false},"captureBody":{"source":"start","value":"off","commonName":"capture_body"},"captureHeaders":{"source":"start","value":false},"centralConfig":{"source":"start","value":false},"contextPropagationOnly":{"source":"start","value":true},"environment":{"source":"start","value":"production"},"globalLabels":{"source":"start","value":[["git_rev","faabb4e47ac99b6f367713ef845613b7313914b8"]],"sourceValue":{"git_rev":"faabb4e47ac99b6f367713ef845613b7313914b8"}},"logLevel":{"source":"default","value":"info","commonName":"log_level"},"metricsInterval":{"source":"start","value":120,"sourceValue":"120s"},"serverUrl":{"source":"start","value":"https://kibana-cloud-apm.apm.us-east-1.aws.found.io/","commonName":"server_url"},"transactionSampleRate":{"source":"start","value":0.1,"commonName":"transaction_sample_rate"},"captureSpanStackTraces":{"source":"start","sourceValue":false},"secretToken":{"source":"start","value":"[REDACTED]","commonName":"secret_token"},"serviceName":{"source":"start","value":"kibana","commonName":"service_name"},"serviceVersion":{"source":"start","value":"8.17.3","commonName":"service_version"}},"activationMethod":"require","message":"Elastic APM Node.js Agent v4.10.0"}
Native global console methods have been overridden in production environment.
[2025-03-11T21:36:44.241+00:00][INFO ][root] Kibana is starting
[2025-03-11T21:36:44.495+00:00][INFO ][node] Kibana process configured with roles: [background_tasks, ui]
[2025-03-11T21:37:19.654+00:00][INFO ][plugins-service] The following plugins are disabled: "cloudChat,cloudExperiments,cloudFullStory,dataUsage,investigateApp,investigate,profilingDataAccess,profiling,searchHomepage,searchIndices,securitySolutionServerless,serverless,serverlessObservability,serverlessSearch".
[2025-03-11T21:37:20.144+00:00][INFO ][http.server.Preboot] http server running at http://0.0.0.0:5601
[2025-03-11T21:37:20.469+00:00][INFO ][plugins-system.preboot] Setting up [1] plugins: [interactiveSetup]
[2025-03-11T21:37:20.519+00:00][INFO ][preboot] "interactiveSetup" plugin is holding setup: Validating Elasticsearch connection configuration…
[2025-03-11T21:37:20.594+00:00][INFO ][root] Holding setup until preboot stage is completed.


i Kibana has not been configured.

Go to http://0.0.0.0:5601/?code=156665 to get started.





4. When Kibana starts, it outputs a unique generated link to the terminal. To access Kibana, open this link in a web browser.
5. In your browser, enter the enrollment token that was generated when you started Elasticsearch.
To regenerate the token, run:
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana


6. Log in to Kibana as the elastic user with the password that was generated when you started Elasticsearch.
To regenerate the password, run:
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic




















