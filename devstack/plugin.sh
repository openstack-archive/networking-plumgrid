#!/bin/bash

# Save trace settings
PG_XTRACE=$(set +o | grep xtrace)
set +o xtrace

function neutron_plugin_create_nova_conf {
    :
}

function neutron_plugin_setup_interface_driver {
    :
}

function neutron_plugin_configure_common {
    Q_USE_SECGROUP=True
    Q_PLUGIN_REMOTE_SOURCE_DIR=/opt/stack/networking-plumgrid/networking_plumgrid
    Q_PLUGIN_CONF_PATH=etc/neutron/plugins/plumgrid
    Q_PLUGIN_CONF_FILENAME=plumgrid.ini
    Q_PLUGIN_CONF_FILE=$Q_PLUGIN_CONF_PATH/$Q_PLUGIN_CONF_FILENAME
    Q_PLUGIN="plumgrid"
    Q_PLUGIN_CLASS="networking_plumgrid.neutron.plugins.plugin.NeutronPluginPLUMgridV2"
    PLUMGRID_DIRECTOR_IP=${PLUMGRID_DIRECTOR_IP:-localhost}
    PLUMGRID_DIRECTOR_PORT=${PLUMGRID_DIRECTOR_PORT:-7766}
    PLUMGRID_ADMIN=${PLUMGRID_ADMIN:-username}
    PLUMGRID_PASSWORD=${PLUMGRID_PASSWORD:-password}
    PLUMGRID_TIMEOUT=${PLUMGRID_TIMEOUT:-70}
    PLUMGRID_DRIVER=${PLUMGRID_DRIVER:-neutron.plumgrid.drivers.fake_plumlib.Plumlib}
}

function neutron_plugin_configure_service {
    iniset /$Q_PLUGIN_CONF_FILE plumgriddirector director_server $PLUMGRID_DIRECTOR_IP
    iniset /$Q_PLUGIN_CONF_FILE plumgriddirector director_server_port $PLUMGRID_DIRECTOR_PORT
    iniset /$Q_PLUGIN_CONF_FILE plumgriddirector username $PLUMGRID_ADMIN
    iniset /$Q_PLUGIN_CONF_FILE plumgriddirector password $PLUMGRID_PASSWORD
    iniset /$Q_PLUGIN_CONF_FILE plumgriddirector servertimeout $PLUMGRID_TIMEOUT
    iniset /$Q_PLUGIN_CONF_FILE plumgriddirector driver $PLUMGRID_DRIVER
}

function configure_plumgrid_plugin {
    echo "Configuring Neutron for PLUMgrid"

    if is_service_enabled q-svc ; then
        Q_PLUGIN_CLASS="networking_plumgrid.neutron.plugins.plugin.NeutronPluginPLUMgridV2"
        export NETWORK_API_EXTENSIONS='binding,external-net,extraroute,provider,quotas,router,security-group'
        NEUTRON_CONF=/etc/neutron/neutron.conf
        iniset $NEUTRON_CONF DEFAULT core_plugin "$Q_PLUGIN_CLASS"
        iniset $NEUTRON_CONF DEFAULT service_plugins ""
    fi
}

function neutron_plugin_configure_debug_command {
    :
}

function is_neutron_ovs_base_plugin {
    # False
    return 1
}

function has_neutron_plugin_security_group {
    # return 0 means enabled
    return 0
}

function neutron_plugin_check_adv_test_requirements {
    is_service_enabled q-agt && is_service_enabled q-dhcp && return 0
}

if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
    # Set up system services
    echo_summary "Configuring system services Template"
    #configure_plumgrid_plugin

elif [[ "$1" == "stack" && "$2" == "install" ]]; then
    # Perform installation of service source
    echo_summary "Installing Template"
    cd $PLUMGRID_DIR
    sudo python setup.py install
    #configure_plumgrid_plugin

elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    # Configure after the other layer 1 and 2 services have been configured
    echo_summary "Configuring Template"
    #configure_plumgrid_plugin

elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
    # Initialize and start the template service
    echo_summary "Initializing Template"
    #configure_plumgrid_plugin
fi

if [[ "$1" == "unstack" ]]; then
    echo "networking-plumgrid unstack"
    # no-op
        :
fi

if [[ "$1" == "clean" ]]; then
    echo_summary "networking-plumgrid clean"
    # no-op
        :
fi
# Restore xtrace
$PG_XTRACE
