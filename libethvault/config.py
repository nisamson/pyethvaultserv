CONFIG = {"cert": "",
          "key": "",
          "vault_registry": "0x0000000000000000000000000000000000000000000000000000000000000000",
          "email": "alerts@example.com",
          "rpc_port": 8545,
          "creation": 1000000,
          "db_loc": "./ethvault.sqlite",
          "mail_delay": 10,
          "loop_delay": 15
          }


def set_config(config_dict):
    for k, v in config_dict.iteritems():
        CONFIG[k] = v
