# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .tracked_resource import TrackedResource


class Server(TrackedResource):
    """Represents a server.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar id: Resource ID
    :vartype id: str
    :ivar name: Resource name.
    :vartype name: str
    :ivar type: Resource type.
    :vartype type: str
    :param location: Required. The location the resource resides in.
    :type location: str
    :param tags: Application-specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param sku: The SKU (pricing tier) of the server.
    :type sku: ~azure.mgmt.rdbms.mysql.models.Sku
    :param administrator_login: The administrator's login name of a server.
     Can only be specified when the server is being created (and is required
     for creation).
    :type administrator_login: str
    :param version: Server version. Possible values include: '5.6', '5.7'
    :type version: str or ~azure.mgmt.rdbms.mysql.models.ServerVersion
    :param ssl_enforcement: Enable ssl enforcement or not when connect to
     server. Possible values include: 'Enabled', 'Disabled'
    :type ssl_enforcement: str or
     ~azure.mgmt.rdbms.mysql.models.SslEnforcementEnum
    :param user_visible_state: A state of a server that is visible to user.
     Possible values include: 'Ready', 'Dropping', 'Disabled'
    :type user_visible_state: str or
     ~azure.mgmt.rdbms.mysql.models.ServerState
    :param fully_qualified_domain_name: The fully qualified domain name of a
     server.
    :type fully_qualified_domain_name: str
    :param earliest_restore_date: Earliest restore point creation time
     (ISO8601 format)
    :type earliest_restore_date: datetime
    :param storage_profile: Storage profile of a server.
    :type storage_profile: ~azure.mgmt.rdbms.mysql.models.StorageProfile
    """

    _validation = {
        'id': {'readonly': True},
        'name': {'readonly': True},
        'type': {'readonly': True},
        'location': {'required': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'location': {'key': 'location', 'type': 'str'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'sku': {'key': 'sku', 'type': 'Sku'},
        'administrator_login': {'key': 'properties.administratorLogin', 'type': 'str'},
        'version': {'key': 'properties.version', 'type': 'str'},
        'ssl_enforcement': {'key': 'properties.sslEnforcement', 'type': 'SslEnforcementEnum'},
        'user_visible_state': {'key': 'properties.userVisibleState', 'type': 'str'},
        'fully_qualified_domain_name': {'key': 'properties.fullyQualifiedDomainName', 'type': 'str'},
        'earliest_restore_date': {'key': 'properties.earliestRestoreDate', 'type': 'iso-8601'},
        'storage_profile': {'key': 'properties.storageProfile', 'type': 'StorageProfile'},
    }

    def __init__(self, *, location: str, tags=None, sku=None, administrator_login: str=None, version=None, ssl_enforcement=None, user_visible_state=None, fully_qualified_domain_name: str=None, earliest_restore_date=None, storage_profile=None, **kwargs) -> None:
        super(Server, self).__init__(location=location, tags=tags, **kwargs)
        self.sku = sku
        self.administrator_login = administrator_login
        self.version = version
        self.ssl_enforcement = ssl_enforcement
        self.user_visible_state = user_visible_state
        self.fully_qualified_domain_name = fully_qualified_domain_name
        self.earliest_restore_date = earliest_restore_date
        self.storage_profile = storage_profile
