GITHUB_URL=https://github.com/jhpyle/docassemble
FOLDER=/tmp/docassemble

cd /tmp
if [ ! -d "$FOLDER" ] ; then
    git clone "$GITHUB_URL" "$FOLDER"
fi
cd docassemble
git checkout master
git pull
docker build -t rdeshpande/docassemble .
docker push rdeshpande/docassemble
