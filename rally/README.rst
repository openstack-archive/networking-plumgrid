Rally related files
=======================

This directory contains rally tasks and plugins for networking-plumgrid specific extensions.

Structure
---------

* plugins - directory where you can add rally plugins. Almost everything in
  Rally is a plugin. Benchmark context, Benchmark scenario, SLA checks, Generic
  cleanup resources, ....

* extra - all files from this directory will be copy pasted to gates, so you
  are able to use absolute paths in rally tasks.
  Files will be located in ~/.rally/extra/*

* networking-plumgrid.yaml is a task that is run against OpenStack with
  Neutron Service deployed by DevStack with networking-plumgrid as a driver
  in Neutron

Useful links
------------

* More about Rally: https://rally.readthedocs.org/en/latest/

* Rally release notes: https://rally.readthedocs.org/en/latest/release_notes.html

* How to add rally-gates: https://rally.readthedocs.org/en/latest/gates.html

* About plugins:  https://rally.readthedocs.org/en/latest/plugins.html

* Plugin samples: https://github.com/openstack/rally/tree/master/samples/plugins
