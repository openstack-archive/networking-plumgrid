#!/bin/bash
# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# this script creates debian package for networking-plumgrid

set -e

# move to networking-plumgrid directory
pushd ../../

# store the path for plugin directory
PLUGIN_DIR="$(pwd)"

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
