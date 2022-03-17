#!/bin/sh

#FORMAT=ps
FORMAT=png

path=`pwd`

pylint --rcfile=pylintrc --import-graph=stem.dot ../*.py ../libs/*.py ../tools/*.py > pylint.log

cd ..
pyreverse -p stem -f ALL -a1 -s1 -A -S  -o dot . libs/ tools/
mv -f *stem.dot $path
cd $path

for i in `ls *.dot`;
do
  base=`basename $i .dot`
  dot -T${FORMAT} $i > $base.${FORMAT}
done