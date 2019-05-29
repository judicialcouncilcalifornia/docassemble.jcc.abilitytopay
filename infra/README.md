# How to deploy AbilityToPay to an Azure Linux VM from scratch

### Prerequisites

[Install the azure CLI tool](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest).

## Setup Azure Resources

### Use resource names that are easy to understand out of context

```
RESOURCE_GROUP_NAME=ATP-UAT-Resource-Group
VM_NAME=ATP-UAT-VM
STORAGE_ACCOUNT_NAME=atpuatblobaccount
STORAGE_CONTAINER_NAME=atpuatblobcontainer
```

### Create the Azure resource group (only necessary if resource group does not already exist)

```
az group create --name $RESOURCE_GROUP_NAME --location westus
```

### Create blob storage account and storage container

```
az storage account create --resource-group $RESOURCE_GROUP_NAME --kind BlobStorage --access-tier Hot --name $STORAGE_ACCOUNT_NAME
az storage container create --name $STORAGE_CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME
az storage account keys list -g $RESOURCE_GROUP_NAME -n $STORAGE_ACCOUNT_NAME
```

Take note of one of the storage account keys.

### Create the Linux VM

See https://docs.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-cli.

```
az vm create \
  --resource-group $RESOURCE_GROUP_NAME \
  --name $VM_NAME \
  --image credativ:Debian:9:latest \
  --admin-username azureuser \
  --generate-ssh-keys
```

Take note of the public IP address of the VM. You'll need this to log in later. This command copies the key in ~/.ssh/id_rsa.pub to the VM, or generates a keypair for you if it does not already exist.

### Open ports 80 and 443 on the VM

```
az vm open-port --port 80 --resource-group $RESOURCE_GROUP_NAME --name $VM_NAME
az vm open-port --port 443 --resource-group $RESOURCE_GROUP_NAME --name $VM_NAME --priority 1100
```

### Disallow ssh from IPs outside of JCC

This has to be done in the azure web UI as far as I can tell. This is in the Networking tab of the VM settings. You should restrict the `default-allow-ssh` rule Source IP range to the JCC subnet.

## Install dependencies on the VM

### ssh in

On Windows, powershell needs to be installed separately.

```
ssh azureuser@<public-ip-address>
```

### install docker

See [https://docs.docker.com/install/linux/docker-ce/debian/](https://docs.docker.com/install/linux/docker-ce/debian/)

```
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
### install nginx
```
sudo apt-get install nginx
```

Okay, you're done doing things on the VM for now.

## Copy config to the VM

### nginx config

Copy over the nginx config file from this repo.
```
scp docassemble-https-proxy azureuser@<public-ip-address>:/etc/nginx/sites-available/
```

### docassemble config

Create an env.list file like below and copy it over.
```
cat > env.list <<EOF
DAPYTHONVERSION=3
BEHINDHTTPSLOADBALANCER=true
AZUREENABLE=true
AZURECONTAINER=$STORAGE_CONTAINER_NAME
AZUREACCOUNTNAME=$STORAGE_ACCOUNT_NAME
AZUREACCOUNTKEY=<put the storage account key here>
EOF

scp env.list azureuser@<public-ip-address>:~
```

## Copy over SSL certs

```
scp cert.crt azureuser@<public-ip-address>:/etc/nginx
scp cert.key azureuser@<public-ip-address>:/etc/nginx
```

## Update DNS entries

Talk to infra team about how to do this.

## Setup the docassemble container

### SSH back into the VM

```
ssh azureuser@<public-ip-address>
```

### Build the docassemble docker image

This will take a while (~20 mins) on the first run:
```
sudo docker run --env-file=env.list -d -p 8080:80 bennlichh/docassemble:0.4.41
```

### Attach to the container (optional)

List running images:
```
docker ps
```

Attach:
```
docker exec -t -i <image-id> /bin/bash
```

Watch everything get set up:
```
tail -f -n 100 /var/log/supervisor/initialize-stderr---supervisor-*.log
```

## Set Ability To Pay config

1) Visit `<public-ip-address>/config`

2) Setup an admin username/password

3) update config.yml a2p block (this includes credentials for image upload storage and oauth communication with the a2p api), e.g.:

```
a2p:
  client_id:
  client_secret:
  blob_account_key:
  oauth_resource:
  base_url:
  ad_url:
  blob_account_name:
```

4) update config.yml default interview (delete existing entry):

```
default interview: docassemble.jcc.abilitytopay:data/questions/interview.yml
```

## Verify everything works

Visit `<public-ip-address>`, ignore the cert warning, and you should see the ability to pay intro screen.

Visit the domain name you set up and you should see the ability to pay intro screen with working SSL certificate.

Complete an interview and you should see the petition show up in the clerk's module.
