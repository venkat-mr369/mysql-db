## MYSQL CONFIG EDITOR

### HELP
```sh
mysql_config_editor set --help
```

### CONFIGURE 
```sh
mysql_config_editor set --user=root --login-path=client --password
```

### VERIFY_1
```sh
mysql_config_editor print
```
password should show with hidden format

### VERIFY_2
```sh
mysql
mysql>select user();
```
