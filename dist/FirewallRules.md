| Source | Port | Destination | Description |
|--------|------|-------------|-------------|
| dev_user | TCP 22 | server_space | SSH access for development |
| dev_user | TCP 27017 | mongo_atlas | Database access for development |
| server_space | TCP 27017 | mongo_atlas | Server access to MongoDB |
| dev_user | TCP 9092 | confluent_cloud | Kafka message streaming |
| server_space | TCP 9092 | confluent_cloud | Server access to Kafka |
| dev_user | TCP 389 | centera_ldap_1 | LDAP authentication |
| dev_user | TCP 389 | centera_ldap_2 | LDAP authentication |
| dev_user | TCP 389 | centera_ldap_3 | LDAP authentication |
| server_space | TCP 389 | centera_ldap_1 | LDAP authentication for server |
| server_space | TCP 389 | centera_ldap_2 | LDAP authentication for server |
| server_space | TCP 389 | centera_ldap_3 | LDAP authentication for server |