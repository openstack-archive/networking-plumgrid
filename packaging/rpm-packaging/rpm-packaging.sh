#!/bin/bash

set -e

# store the path for plugin directory
PLUGIN_DIR="$( cd ../../ && pwd )"

cd $PLUGIN_DIR

# create rpm build environment
rm -rf ~/rpmbuild
mkdir -p ~/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}

# Get the version from PKG-INFO
VERSION=`cat PKG-INFO | grep Version | grep -o '[0-9]*[.][0-9]*[.][0-9]*'`

# Create the tarball and untar it
python setup.py sdist --dist-dir ~/rpmbuild/SOURCES

# Copy the rpm spec file into rpm specs directory
cp ${PLUGIN_DIR}/packaging/rpm-packaging/networking-plumgrid.spec ~/rpmbuild/SPECS

# update version in spec file
sed -ie "s/Version:\s\+XXX/Version:        ${VERSION}/" ~/rpmbuild/SPECS/networking-plumgrid.spec

# Build the package
rpmbuild -bs ~/rpmbuild/SPECS/networking-plumgrid.spec

# copy the rpm package to respective directory
cp ~/rpmbuild/SRPMS/*.rpm $PLUGIN_DIR/packaging/rpm-packaging
