# How to upgrade Docassemble

### Prerequisites

[Install the azure CLI tool](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest).

### Step 1: Freeze the latest version of Docassemble to the JCC container registry

1) Look up the version number of the latest Docassemble release https://github.com/jhpyle/docassemble/releases

2) Import it from docker hub into the JCC registry. Replace `$VERSION_NUMBER` with the version you looked up in the previous step.

```
az acr import -n jcccontainerregistry --source docker.io/jhpyle/docassemble -t a2p/docassemble:$VERSION_NUMBER
```

3) Verify that your import worked by listing all the versions in the registry:

```
az acr repository show-tags -n jcccontainerregistry --repository a2p/docassemble
```

### Step 2: Pull the new Docassemble version from the registry

1) SSH into the VM for the environment you need to upgrade. I'll use the dev VM for example.

```
ssh azureuser@mycitations.dev.courts.ca.gov
```

2) Log in to the azure CLI tool

```
sudo az login
```

3) Log in to the container registry

```
sudo az acr login -n jcccontainerregistry
```

4) Pull the image. Replace `$VERSION_NUMBER` with the version you looked up in step 1. This will take some time as each image is several gigabytes in size.

```
sudo docker pull jcccontainerregistry.azurecr.io/a2p/docassemble:$VERSION_NUMBER
```

### Step 3: Restart the Docassemble container

Keep in mind that the public website will be inaccessible during this process (i.e. this part involves some downtime)

0) Find the container id of the running container

```
sudo docker ps
```

1) Kill the running container. Replace $CONTAINER_ID with the id you just looked up.

```
sudo docker stop -t60 $CONTAINER_ID
sudo docker rm $CONTAINER_ID
```

2) Boot the new container. Replace $VERSION_NUMBER as before.

```
cd ~
sudo docker run --env-file=env.list -d -p 8080:80 jcccontainerregistry.azurecr.io/a2p/docassemble:$VERSION_NUMBER
```

3) Watch it spin up. Replace $CONTAINER_ID with the output of the `run` command in the previous step.

```
sudo docker exec -t -i $CONTAINER_ID /bin/bash
tail -f -n 100 /var/log/supervisor/initialize-stderr---supervisor-*.log
```

4) Once you see `initialize finished`, test it out by visiting the URL in your web browser: https://mycitations.dev.courts.ca.gov. Verify that the reported version number is what you expect at https://mycitations.dev.courts.ca.gov/config.

5) Do a test-run through the entire interview to make sure nothing broke in the upgrade.

6) Clean-up old images that you no longer need. Use `sudo docker images` to see installed images, and [`sudo docker rmi`](https://docs.docker.com/engine/reference/commandline/rmi/) to remove.
