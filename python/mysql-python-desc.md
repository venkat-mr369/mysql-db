MySQL replication setup instructions. 

## Summary of Steps for mysql server 

| Step | Description | Commands |
|------|-------------|----------|
| **1** | Stop MySQL Instance | `sudo systemctl stop mysqld@mysql1` |
| **2** | Delete Old Directories | `sudo rm -rf /u01/data/mysql1_binlog` & `sudo rm -rf /u01/data` |
| **3** | Create Directories | `sudo mkdir /u01/data` with `chmod 750` & `chown mysql:mysql` |
| **4** | Restore Backup | `mysqlbackup --copy-back-and-apply-log` |
| **5** | Set Permissions | `chown -R mysql:mysql` & `chmod 750` on all dirs |
| **6** | Start MySQL | `sudo systemctl start mysqld@mysql1` |
| **7** | Configure Replication | SQL: `CHANGE REPLICATION SOURCE TO...` |

## Server Configuration
- **Primary:** 192.168.1.1:3301
- **Secondary:** 192.168.2.1:3301

## Python Script Usage
```bash
# Run full workflow
python mysql_replication_setup.py --full

# Run specific step
python mysql_replication_setup.py --step 1

# Generate SQL only
python mysql_replication_setup.py --sql-only
```
