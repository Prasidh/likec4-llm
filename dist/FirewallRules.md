| Source | Port | Destination | Description |
|--------|------|-------------|-------------|
| dev_user | TCP 22 | server_space | Allow SSH access for development activities |
| dev_user | TCP 27017 | mongo_atlas | Allow MongoDB connections for data access |
| dev_user | TCP 9092 | confluent_cloud | Allow Kafka connections for message publishing and consuming |
| centera_ldap_1 | TCP 389 | centera_ldap_2 | Allow LDAP communication between Centera LDAP servers |
| centera_ldap_1 | TCP 389 | centera_ldap_3 | Allow LDAP communication between Centera LDAP servers |
| centera_ldap_2 | TCP 389 | centera_ldap_3 | Allow LDAP communication between Centera LDAP servers |