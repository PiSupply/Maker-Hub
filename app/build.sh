#!/bin/sh
VERSION=0.1.0

rm -r MANIFEST MakerHub-*.tar.gz deb_dist dist python3-makerhub_*.deb

python setup.py --command-packages=stdeb.command sdist_dsc
cd deb_dist/makerhub-$VERSION
dpkg-buildpackage -rfakeroot -uc -us
cd ..
cp python3-makerhub_$VERSION-1_all.deb ../..
# git tag/commit/push
