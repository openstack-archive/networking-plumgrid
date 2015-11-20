#!/bin/bash

set -e

# store the path for plugin directory
PLUGIN_DIR="$( cd ../../ && pwd )"

cd $PLUGIN_DIR

# Get the version from PKG-INFO
VERSION=`cat PKG-INFO | grep Version | grep -o '[0-9]*[.][0-9]*[.][0-9]*'`

# Create the tarball and untar it
python setup.py sdist --dist-dir /tmp
tar xzvf /tmp/networking_plumgrid-${VERSION}.tar.gz -C /tmp

# Rename the tarball as debian packager expects to see
mv /tmp/networking_plumgrid-${VERSION}.tar.gz /tmp/networking-plumgrid_${VERSION}.orig.tar.gz

# Copy the debian related commands into extracted dir
cp -r ${PLUGIN_DIR}/packaging/debian-packaging/debian /tmp/networking_plumgrid-${VERSION}

# Create a changelog for specific release version
cd /tmp/networking_plumgrid-${VERSION}
dch --create -v ${VERSION} --package networking-plumgrid "Release ${VERSION}"

# Build the package
debuild -us -uc

# copy the debian package to respective directory
cp /tmp/*.deb $PLUGIN_DIR/packaging/debian-packaging
