..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============================
PLUMgrid L2 VTEP Gateway API
============================

Launchpad blueprint:

https://blueprints.launchpad.net/networking-plumgrid/+spec/l2-gateway-api

This blueprint introduces a PLUMgrid Neutron API extension that can be used to
create and manage L2 Gateway components. L2 Gateways are an important part of
PLUMgrid integration with different hardware vendors. In the basic terms,
L2 Gateways serve the purpose of bridging multiple physical networks with
logical networks together representing them as a single L2 broadcast domain.

This API is going to use VXLAN and VLAN as the two L2 segmentation technologies
being bridged by an L2 Gateway.

Proposed Approach
=================

This specification intends to describe a PLUMgrid Neutron API extension that
allows for bridging VXLAN and VLAN segmentation technologies by a physical
L2 Gateway. The API supports both stand-alone and active/active models of
configurations for the L2 Gateways.

The proposed Neutron API extension provides REST interfaces to support the
following use cases:

Note: These commands/APIs can be executed only by the admin users.


1. Creating a logical gateway that represents a physical L2 Gateway device with
   its interfaces(s).

    neutron l2-gateway-create <gateway-name>
    --device name=<device-name1>,interface_names=<interface-name1>[:<seg-id1>];
    <interface-name2>[:<seg-id2>,<seg-id3>]
    --device name=<device-name2>,interface_names=<interface-name2>[:<seg-id1>];
    <interface-name2>[:<seg-id2>,<seg-id3>]

    where gateway-name is a descriptive name for the logical gateway service.
    device-name1 and device-name2 are the names of the L2 gateways.
    interface-name1 and interface-name2 are physical interfaces on the gateways.
    seg-id indicates the segmentation identifier/VLAN of the physical network to
    which the interfaces belong to.

    NOTE: The current design implementation limits the creation of a single
    l2-gateway, which can have a minimum of one and maximum of two devices.
    Adding two devices to an l2-gateway will represent an Active/Active
    deployment mode.

7. Updating a logical gateway.

    neutron l2-gateway-update <gateway-name/uuid>
    --device name=<existing-device>
    [--add-interface=<new-interface-name>:<segmentation-ids-with-commas>]
    [--remove-interface=<existing-interface-name>]

8. Deletion of a logical gateway.

    neutron l2-gateway-delete <gateway-name/uuid>

9. List all the logical gateways.

    neutron l2-gateway-list

10. Show details of a logical gateway

      neutron l2-gateway-show <gateway-name/uuid>

11. Connecting a logical gateway to an overlay/virtual network.

      neutron l2-gateway-connection-create <gateway-name/uuid>
      <network-name/uuid>
      [--default-segmentation-id=<seg-id>]

      where gateway-name/uuid is a descriptive name for the logical gateway
      service.
      <network-name> is the name of the neutron network.
      --default-segmentation-id indicates the default segmentation-id that will
      be applied to the interfaces for which segmentation id was not specified
      in l2-gateway-create command.

      Response: <connection-uuid> <neutron_net_uuid> <gateway_uuid>

12. Listing connections.

      neutron l2-gateway-connection-list

13.  Show details of an existing connection

      neutron l2-gateway-connection-show <connection-uuid>

14. Delete existing connection between neutron-network and the VLAN on the
    L2 Gateway.

      neutron l2-gateway-connection-delete <connection-uuid>

Data Model Impact
-----------------
The following four tables introduced in the networking-l2gw project will be
used:

pg_l2gateways:
+-----------+--------------+------+-----+---------+-------+
| Field     | Type         | Null | Key | Default | Extra |
+-----------+--------------+------+-----+---------+-------+
| id        | varchar(36)  | NO   | PRI | NULL    |       |
| name      | varchar(255) | YES  |     | NULL    |       |
| tenant_id | varchar(36)  | YES  |     | NULL    |       |
+-----------+--------------+------+-----+---------+-------+

pg_l2gatewaydevices:
+--------------------+-------------+------+-----+---------+-------+
| Field              | Type        | Null | Key | Default | Extra |
+--------------------+-------------+------+-----+---------+-------+
| id                 | varchar(36) | NO   | PRI | NULL    |       |
| device_name        | varchar(36) | NO   | PRI | NULL    |       |
| l2_gateway_id      | varchar(36) | NO   | FOR | NULL    |       |
+--------------------+-------------+------+-----+---------+-------+

pg_l2gatewayinterfaces:
+--------------------+-------------+------+----------+---------+-------+
| Field              | Type        | Null | Key      | Default | Extra |
+--------------------+-------------+------+----------+---------+-------+
| id                 | varchar(36) | NO   | PRI      | NULL    |       |
| interface_name     | varchar(36) | NO   | MUL      | NULL    |       |
| device_id          | varchar(36) | NO   | FOR, MUL | NULL    |       |
| segmentation_id    | int(11)     | YES  |          | NULL    |       |
+--------------------+-------------+------+----------+---------+-------+


pg_networkconnections:
+--------------------+---------------------+------+-----+---------+-------+
| Field              | Type                | Null | Key | Default | Extra |
+--------------------+---------------------+------+-----+---------+-------+
| id                 | varchar(36)         | NO   | PRI | NULL    |       |
| tenant_id          | varchar(255)        | YES  |     | NULL    |       |
| l2_gateway_id      | varchar(36)         | YES  | MUL | NULL    |       |
| network_id         | varchar(36)         | YES  | MUL | NULL    |       |
| port_id            | varchar(36)         | NO   | PRI | NULL    |       |
+--------------------+---------------------+------+-----+---------+-------+

REST API Impact
-----------------
New REST resources to be added are described below.

l2gateways:

+-----------+--------------+---------+---------+--------------+
|Attribute  |Type          |Access   |Default  |Description   |
|Name       |              |         |Value    |              |
+===========+==============+=========+=========+==============+
|id         |string        |CRD      |generated|identity      |
|           |(UUID)        |         |         |              |
+-----------+--------------+---------+---------+--------------+
|tenant id  |string        |CRUD     |         |              |
|           |(UUID)        |         |         |              |
+-----------+--------------+---------+---------+--------------+
|name       |string        |CRUD     |''       |              |
|           |              |         |         |              |
+-----------+--------------+---------+---------+--------------+
|devices    |list of       |CRUD     |[]       |              |
|           |dicts         |         |         |              |
|           |for devices   |         |         |              |
|           |and interfaces|         |         |              |
|           |              |         |         |              |
+-----------+--------------+---------+---------+--------------+

Note: In "devices" attribute, existing device can be updated
to add/remove interface only.

networkconnections:

+-------------------+-------+---------+---------+--------------+
|Attribute          |Type   |Access   |Default  |Description   |
|Name               |       |         |Value    |              |
+===================+=======+=========+=========+==============+
|id                 |string |CRD      |generated|connectionuuid|
|                   |(UUID) |         |         |              |
+-------------------+-------+---------+---------+--------------+
|l2                 |string |CRD      |         |              |
|gateway id         |(UUID) |         |         |              |
+-------------------+-------+---------+---------+--------------+
|network id         |string |         |         |              |
|                   | (UUID)|CRD      |         |              |
+-------------------+-------+---------+---------+--------------+
|port_id            |UUID   |CRD      |         |              |
+-------------------+-------+---------+---------+--------------+
|default            | int   |C        |         |              |
|segmentation_id    |       |         |         |              |
+-------------------+-------+---------+---------+--------------+

The following REST APIs will be implemented.

1. neutron l2-gateway-create <gateway-name>
   --device name=<device-name1>,interface_names=<interface-name1>[:<seg-id1>];
   <interface-name2>[:<seg-id2>]
   --device name=<device-name2>,interface_names=<interface-name1>[:<seg-id1>];
   <interface-name2>[:<seg-id2>]

JSON Request

::

    POST /v2/l2-gateways
    Content-Type: application/json
    {"l2_gateway": {"name": "<gateway-name>”,
                    "devices": [{"device_name": "<device-name1>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>]}]
                                },
                                {"device_name": "<device-name2>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>]}]
                                }]}}

Response:

::

    {"l2_gateway": {"name": "<gateway-name>”,
                    "tenant_id": "1fdcfb7b5a3f401f9b91b387fb306827",
                    "devices": [{"device_name": "<device-name1>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>]}]
                                },
                                {"device_name": "<device-name2>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>]}]
                                }],
                    "id": "164b3403-7da4-441a-8bb3-2631cdc18b6d"}}

Normal Response Code(s): Created (201)
Error Response Code(s):  Standard http error codes

2. neutron l2-gateway-update <existing-gateway-name/uuid>
    [--add-interface=<new-interface-name>:<segmentation-ids-with-commas>]
    [--remove-interface=<existing-interface-name>]

JSON Request

::

    POST /v2/l2-gateways
    Content-Type: application/json
    {"l2_gateway": {"name": "<gateway-name>",
                    "devices": [{"device_name": "<existing-device>",
                                 "new_interfaces": [{"name":"<new-interface-name>",
                                                     "segmentation-id":[<seg-id>]}]
                                },
                                 "deleted_interfaces": [{"name":"<interface-name>"}]
                               ]}}

Response:

::

    {"l2_gateway": {"name": "<gateway-name>",
                    "tenant_id": "1fdcfb7b5a3f401f9b91b387fb306827",
                    "devices": [{"device_name": "<device-name1>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>}]
                                },
                                {"device_name": "<device-name2,IP-2>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>]}]
                                }],
                    "id": "164b3403-7da4-441a-8bb3-2631cdc18b6d"}}

Normal Response Code(s): Created (200)
Error Response Code(s):  Standard http error codes

3. neutron l2-gateway-list

Request

::

    GET /v2/l2-gateways
    Content-Type: application/json

Response:

::

    {"l2_gateways": [{"name": "<gateway-name/uuid>”,
                      "tenant_id": "1fdcfb7b5a3f401f9b91b387fb306827",
                      "devices": [{"device_name": "<device-name1>”,
                                   "interfaces": [{"name":"<interface-name1>",
                                                   "segmentation-id":[<seg-id1>]},
                                                  {"name":"<interface-name2>",
                                                   "segmentation-id":[<seg-id2>]}]
                                  },
                                  {"device_name": "<device-name2>”,
                                   "interfaces": [{"name":"<interface-name1>",
                                                   "segmentation-id":[<seg-id1>]},
                                                  {"name":"<interface-name2>",
                                                   "segmentation-id":[<seg-id2>}]
                                  }],
                      "id": "164b3403-7da4-441a-8bb3-2631cdc18b6d"}]}


    Normal Response Code(s):  OK (200)
    Error Response Code(s):  Standard http error codes

4. neutron l2-gateway-show <gateway-name/uuid>

Request

::

    GET /v2/l2-gateways/<gateway-name/uuid>
    Content-Type: application/json

Response:

::

    {"l2_gateway": {"name": "<gateway-name/uuid>”,
                    "tenant_id": "1fdcfb7b5a3f401f9b91b387fb306827",
                    "devices": [{"device_name": "<device-name1>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>]}]
                                },
                                {"device_name": "<device-name2>”,
                                 "interfaces": [{"name":"<interface-name1>",
                                                 "segmentation-id":[<seg-id1>]},
                                                {"name":"<interface-name2>",
                                                 "segmentation-id":[<seg-id2>]}]
                                }],
                    "id": "164b3403-7da4-441a-8bb3-2631cdc18b6d"}
    }

Normal Response Code(s):  OK (200)
Error Response Code(s):  Standard http error codes

5. neutron l2-gateway-delete <gateway-name/uuid>

Request

::

    DELETE /v2/l2-gateways/<gateway-name/uuid>
    Content-Type: application/json

Response:

::

    Null
    Normal Response Code(s):  No content (204)
    Error Response Code(s):  Standard http error codes

6. neutron l2-gateway-connection-create <gateway-name/uuid> <network-name/uuid>
      [--default-segmentation-id=<seg-id>]

Request

::

    POST /v2/l2-gateway-connections
    Content-Type: application/json

    {"network_id": "591ffe08-f8f5-44c1-85c1-1026878f69bd",
     "default_segmentation_id": <seg-id>,
     "gateway_id": "164b3403-7da4-441a-8bb3-2631cdc18b6d"
    }

Response:

::

    {"tenant_id": "1fdcfb7b5a3f401f9b91b387fb306827",
     "connection_id": "<connection-uuid>",
     "network_id": "46904e95-2201-431a-a9c8-4b06e9194003",
     "default_segmentation_id": <seg-id>,
     "gateway_id": "164b3403-7da4-441a-8bb3-2631cdc18b6d",
     "port_id": "37b4e32d1c134e62beb3c36230a13e2a"
    }

Normal Response Code(s): Created (201)

Error Response Code(s):  Standard http error codes

7. neutron l2-gateway-connection-list

Request

::

    GET /v2/l2-gateway-connections
    Content-Type: application/json

Response:

::

    {"l2_gateway_connections": [{"connection_id": "<connection-uuid>",
                                                   "tenant_id": "1fdcfb7b5a3f401f9b91b387fb306827",
                                                   "network_id":
                                                   "46904e95-2201-431a-a9c8-4b06e9194003",
                                                   "default_segmentation_id": <seg-id>,
                                                   "gateway_id":
                                                   "164b3403-7da4-441a-8bb3-2631cdc18b6d",
                                                   "port_id": "37b4e32d1c134e62beb3c36230a13e2a"}]
    }
    Normal Response Code(s):  OK (200)
    Error Response Code(s):  Standard http error codes

8. neutron l2-gateway-connection-show <connection-uuid>

Request

::

    GET /v2/l2-gateway-connections/<connection-uuid>
    Content-Type: application/json

Response:

::

    {"connection_id" : "<connection-uuid>",
     "tenant_id": "1fdcfb7b5a3f401f9b91b387fb306827",
     "network_id": "46904e95-2201-431a-a9c8-4b06e9194003",
     "default_segmentation_id": <seg-id>,
     "gateway_id": "164b3403-7da4-441a-8bb3-2631cdc18b6d",
     "port_id": "37b4e32d1c134e62beb3c36230a13e2a"
    }

    Normal Response Code(s):  OK (200)
    Error Response Code(s):  Standard http error codes

9. neutron l2-gateway-connection-delete <connection-uuid>

Request

::

    DELETE /v2/l2-gateway-connections/<connection-uuid>
    Content-Type: application/json

Response:

::

    Null
    Normal Response Code(s):  No content (204)
    Error Response Code(s):  Standard http error codes

Typical use case scenario
-------------------------

Let’s consider a use case where a user with administrative privileges wants to onboard two
physical L2 gateways configured in Active/Active mode of deployment. The metadata
described for the physical gateway is as following:

::

    hostname(s): ‘tor-switch-1’, ‘tor-switch-2’
    physical interface(s): ‘Ethernet40’
    segmentation-ID(s): ‘VLAN 50’
    bare metal host machine(s): ‘PS-1’

The user can then execute the following sequence of commands to establish connectivity
between the virtual machines in the overlay network and the physical bare metal hosts
connected to the L2 gateway.

1. The user will create a logical Neutron network.

    neutron net-create network1

2. The user creates a logical gateway, ‘vtep-gateway-1’, which onboards the physical
   L2 gateway.

    neutron l2-gateway-create vtep-gateway-1
    --device name=[{“name”: “tor-switch-1”}],interface_names==Ethernet40
    --device name=[{“name”: “tor-switch-2”}],interface_names==Ethernet40

    The underlying API implementation will establish connection with the
    physical L2 gateway and add a corresponding entry in the Neutron database.

3. The user will connect the logical gateway with an existing overlay (VXLAN) network,
   ‘network1’.

    neutron l2-gateway-connection-create vtep1 network1 --default-segmentation-id=50

    where the default segmentation-ID is used for all interfaces which do not
    already have an associated segmentation-ID. The API implementation will
    leverage the PLUMgrid plugin to perform the following operations:

    - Update the L2 gateway with the IP and MAC addresses of all virtual machines
      connected to the logical network, “network1”
    - Update the L2 gateway with endpoint VTEP-IP of the compute nodes which host
      the virtual machines connected to the network, “network1”
    - Update the L2 gateway with the corresponding VXLAN-VNI key binding between “VLAN50”
      and the logical network, “network1”

    Since the L2 gateway is now aware of the corresponding VTEP-IPs of each compute node,
    it creates VXLAN tunnels linking to the compute nodes.

4. The PLUMgrid plugin implementation will then handle the relaying VTEP-IP address of the
   L2 gateway, MAC addresses of the bare metal host machines and their corresponding IP
   addresses to PLUMgrid platform.

5. PLUMgrid platform then relays this information to the compute nodes.

6. Based on the provided information, the compute nodes will establish reverse VXLAN tunnels
   to L2 gateway.

7. From this point onwards, any new instances of virtual machines launched on the
   compute nodes, which are connected to the same network, “network1”, will use the existing
   VXLAN tunnels to exchange traffic.

8. In the same regard, any new bare metal physical machines connected to the onboarded
   VLAN 50 will use the existing VXLAN tunnels to exchange traffic.

9. In the case when no virtual machines are hosted on the compute node, the VXLAN tunnel to that
   compute node will be destroyed. Similarly, when all bare metal physical machines are removed
   from the onboarded VLAN, the VXLAN tunnel to L2 gateway is also destroyed.

10. The user can also destroy the logical connection between the bare metal host machines and
    virtual machines in the logical network by executing the following command:

    neutron l2-gateway-connection-delete connection-uuid

    The underlying implementation will leverage the PLUMgrid plugin to update the
    L2 gateway and perform the following operations:
    - Remove information about the IP and MAC addresses of all virtual machines connected
      to the logical network, “network1”
    - Remove information about the endpoint VTEP-IP of the compute nodes which host the
      virtual machines connected to the network, “network1”
    - Remove information about the corresponding VXLAN-VNI key binding between “VLAN50”
      and the logical network, “network1”

    On the other side, the corresponding VXLAN tunnels to the L2 gateway are also destroyed.

11. After the logical connection is destroyed, the user can also delete the logical gateway,
    ‘vtep-gateway-1’.

    neutron l2-gateway-delete vtep-gateway-1

    The underlying implementation will remove a corresponding entry from the Neutron DB and
    update the PLUMgrid platform accordingly.

Security Impact
---------------
None

Notifications Impact
--------------------

Will be handled by the PLUMgrid platform

Other End User Impact
---------------------

Python-neutronclient will invoke the APIs.

Performance Impact
------------------
None

IPv6 Impact
-----------
None

Other Impact
---------------------
Access credentials for the L2 gateway (Management IP, username and password) need to be
specified in the plumgrid.ini file during initial setup.

Developer Impact
----------------
None

Community Impact
----------------
This specification presents a flexible implementation which can easily adapt to any future community requirements.

Alternatives
------------
None

Implementation
==============

Assignee(s)
-----------

Fawad Khaliq (fawad@plumgrid.com)
Muneeb Ahmad (muneeb@plumgrid.com)

Work Items
----------

The work division is as following:

1. Implementation of the Neutron API extension

   * Add support for the REST calls described above.
   * Implementation of the proposed DB model.
   * Definition of RPCs for the underlying implementation.

2. Implementation of new CLIs in a client

3. Packaging of the implemented software and its deployment


Dependencies
============
None

Testing
=======

Rally Tests
-------------
None

Tempest Tests
-------------
None

Functional Tests
----------------
None

API Tests
---------
The following tempest API tests will be added:
1. CRUD operation of an L2 gateway
2. CRD connection of an L2 gateway with a neutron network

Documentation Impact
====================

User Documentation
------------------
Documentation will cover functionality and configuration details.

Developer Documentation
-----------------------
OpenStack wiki needs to be updated

References
==========
[1] Networking-l2gw with service plugin
    https://github.com/openstack/networking-l2gw/tree/master/networking_l2gw
[2] Bringing provider networks into OpenStack using L2 gateway
    https://www.openstack.org/summit/vancouver-2015/summit-videos/presentation/bringing-provider-networks-into-openstack-using-l2-gateway
