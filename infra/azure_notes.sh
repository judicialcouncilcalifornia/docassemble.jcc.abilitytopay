# These are notes of commands to be used with the Azure CLI to setup the DocAssemble Ability to Pay instance.

# This is somewhat based on: https://gist.github.com/jasonbarbee/a52ffb2df46da78d2383e2980cdb7880

# Sets up the resources and resource plan, using the stock DocAssemble docker container
# as the basis for the Azure web service. There are a few environment variables that need
# to be setup (see below) to make sure the DocAssemble service starts.
az appservice plan create --name atp-docassemble-plan --resource-group ATP-DocAssemble --sku P2V1 --is-linux
az webapp create --resource-group ATP-DocAssemble --plan atp-docassemble-plan --name docassemble --deployment-container-image-name rdeshpande/docassemble:latest
az webapp config appsettings set --resource-group ATP-DocAssemble --name docassemble --settings WEBSITES_PORT=80 WEBSITES_CONTAINER_START_TIME_LIMIT=1200 DAPYTHONVERSION=3
az webapp config  set --resource-group ATP-DocAssemble --name docassemble --always-on true

# DocAssemble also supports using S3 or Azure Blob Storage as a backup for the database and all
# uploaded files. When the docker container starts/stops, the Azure blob storage is refreshed or retrieved.
az storage account create -g ATP-DocAssemble --kind BlobStorage --access-tier Hot -n docassemblestorage
az storage container create -n docassemblestoragecontainer --account-name docassemblestorage

# The value for the AZZUREACCOUNTKEY is retrieved from the Azure Portal. These environment variables
# are what tell DocAssemble to actually use the Blob storage as backup.
az webapp config appsettings set --resource-group ATP-DocAssemble --name docassemble --settings AZUREENABLE=true AZURECONTAINER=docassemblestoragecontainer AZUREACCOUNTNAME=docassemblestorage AZUREACCOUNTKEY=<REPLACE_WITH_BLOB_ACCOUNT_KEY>

# Logging - if you want to tail the DocAssemble logs you can use the following command:
az webapp log tail -n docassemble -g ATP-DocAssemble
