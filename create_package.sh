DIR=`pwd`

mkdir -p /tmp/stem/
rm -f tools/*.pyc libs/*.pyc 
cp -prf images/ libs/ *.py tools/ ui/ uml/ metadata.txt docs/build/latex/DocumentazioneSTEM.pdf /tmp/stem/
mkdir -p /tmp/stem/docs/build/
cp -prf docs/build/html/ /tmp/stem/docs/build/

cd /tmp/
zip -9r stem.zip stem
cd $DIR
