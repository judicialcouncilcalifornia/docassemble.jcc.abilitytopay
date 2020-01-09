rsync -r --exclude-from=.gitignore . azureuser@atp-api-monitor.westus.cloudapp.azure.com:~/atp-api-monitor
ssh azureuser@atp-api-monitor.westus.cloudapp.azure.com sudo systemctl restart atp-api-monitor
echo 'Deployed'
