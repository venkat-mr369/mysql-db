# MySQL Primary-Secondary Replication Setup Guide

## Overview

This document describes the complete process for setting up MySQL replication between a Primary and Secondary server, including backup restoration using MySQL Enterprise Backup.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     MySQL REPLICATION TOPOLOGY                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌──────────────────┐              ┌──────────────────┐               │
│    │   PRIMARY        │              │   SECONDARY      │               │
│    │   192.168.1.1    │ ──────────── │   192.168.2.1    │               │
│    │   Port: 3301     │  Replication │   Port: 3301     │               │
│    └──────────────────┘              └──────────────────┘               │
│                                                                         │
│    • Receives writes                 • Read replicas                    │
│    • Source of truth                 • Disaster recovery                │
│    • Binlog enabled                  • Receives binlog events           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Server Configuration

| Server | IP Address | Port | Role |
|--------|------------|------|------|
| Primary | 192.168.1.1 | 3301 | Master/Source |
| Secondary | 192.168.2.1 | 3301 | Replica/Slave |

---

## Directory Structure

```
/u01/
└── data/
    ├── mysql1_binlog/       # Binary logs directory
    │   └── mysql-bin.*      # Binary log files
    └── mysqldata/
        ├── ebackup.mbi      # MySQL Enterprise Backup image
        └── backup-tmp1/     # Temporary backup extraction directory
```

---

## Step-by-Step Process

### STEP 1: Stop MySQL Instance on Secondary

**Description:** Stop the MySQL service on the secondary server before making any changes.

**Commands:**
```bash
# Check current status
sudo systemctl status mysqld@mysql1

# Stop the instance
sudo systemctl stop mysqld@mysql1

# Verify it's stopped
sudo systemctl status mysqld@mysql1
```

**Expected Output:**
- Service should show as "inactive (dead)"

---

### STEP 2: Delete Old Data and Binlog Directories

**Description:** Remove existing data to prepare for fresh restoration from backup.

**⚠️ WARNING:** This is a destructive operation! Ensure you have backups before proceeding.

**Commands:**
```bash
# Delete binlog directory
sudo rm -rf /u01/data/mysql1_binlog

# Delete data directory
sudo rm -rf /u01/data
```

**What This Does:**
- Removes all existing MySQL data files
- Removes all binary log files
- Prepares for clean restore from backup

---

### STEP 3: Create Directories with Permissions

**Description:** Create fresh directories with correct MySQL ownership and permissions.

**Commands:**
```bash
# Create main data directory
sudo mkdir /u01/data

# Set ownership (mysql user and group)
sudo chown -R mysql:mysql /u01/data

# Set permissions (rwxr-x---)
sudo chmod 750 /u01/data

# Create binlog directory
sudo mkdir /u01/data/mysql1_binlog

# Set binlog permissions
sudo chmod 750 /u01/data/mysql1_binlog

# Set binlog ownership
sudo chown -R mysql:mysql /u01/data/mysql1_binlog
```

**Permission Explanation:**
- `750` = Owner: rwx (read/write/execute), Group: r-x (read/execute), Others: --- (none)
- `mysql:mysql` = MySQL user and group ownership

---

### STEP 4: Restore Backup Using mysqlbackup

**Description:** Use MySQL Enterprise Backup to restore the backup image to the secondary server.

**Command:**
```bash
sudo mysqlbackup \
    --host=127.0.0.1 \
    --port=3301 \
    --datadir=/u01/data \
    --log_bin=/u01/data/mysql1_binlog/mysql-bin \
    --backup-image=/u01/data/mysqldata/ebackup.mbi \
    --backup-dir=/u01/data/mysqldata/backup-tmp1 \
    copy-back-and-apply-log
```

**Parameters Explained:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `--host` | 127.0.0.1 | Connect to localhost |
| `--port` | 3301 | MySQL port |
| `--datadir` | /u01/data | Target data directory |
| `--log_bin` | /u01/data/mysql1_binlog/mysql-bin | Binary log location |
| `--backup-image` | /u01/data/mysqldata/ebackup.mbi | Backup image file |
| `--backup-dir` | /u01/data/mysqldata/backup-tmp1 | Temp extraction directory |
| `copy-back-and-apply-log` | - | Restore and apply InnoDB logs |

**Backup Path:** `/u01/data/mysqldata/`

---

### STEP 5: Set Final Permissions

**Description:** After restoration, ensure all files have correct ownership and permissions.

**Commands:**
```bash
# Set ownership on data directory
sudo chown -R mysql:mysql /u01/data

# Set permissions on data directory
sudo chmod 750 /u01/data

# Set permissions on binlog directory
sudo chmod 750 /u01/data/mysql1_binlog

# Set ownership on binlog directory
sudo chown -R mysql:mysql /u01/data/mysql1_binlog
```

---

### STEP 6: Start MySQL Instance

**Description:** Start the MySQL service after backup restoration.

**Commands:**
```bash
# Start MySQL instance
sudo systemctl start mysqld@mysql1

# Check status
sudo systemctl status mysqld@mysql1
```

**Expected Output:**
- Service should show as "active (running)"
- No errors in journal logs

---

### STEP 7: Configure Replication

**Description:** Configure the secondary server to replicate from the primary server.

**Login to MySQL Workbench or CLI:**
```bash
mysql -h 127.0.0.1 -P 3301 -u root -p
```

**SQL Commands:**
```sql
-- Check current replica status
SHOW REPLICA STATUS;

-- Stop any existing replication
STOP REPLICA;

-- Reset replica configuration
RESET REPLICA ALL;

-- Configure replication source
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='192.168.1.1',
    SOURCE_PORT=3301,
    SOURCE_USER='replicationuser',
    SOURCE_PASSWORD='********',
    SOURCE_AUTO_POSITION=1,
    GET_SOURCE_PUBLIC_KEY=1;

-- Start replication
START REPLICA;

-- Verify replication is working
SHOW REPLICA STATUS\G
```

**Configuration Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `SOURCE_HOST` | 192.168.1.1 | Primary server IP |
| `SOURCE_PORT` | 3301 | Primary server port |
| `SOURCE_USER` | replicationuser | Replication account |
| `SOURCE_PASSWORD` | ******** | Account password |
| `SOURCE_AUTO_POSITION` | 1 | Use GTID auto-positioning |
| `GET_SOURCE_PUBLIC_KEY` | 1 | Get public key for caching_sha2_password |

---

## Verification

### Check Replication Status

```sql
SHOW REPLICA STATUS\G
```

**Key Fields to Check:**

| Field | Expected Value | Meaning |
|-------|---------------|---------|
| `Replica_IO_Running` | Yes | IO thread is running |
| `Replica_SQL_Running` | Yes | SQL thread is running |
| `Seconds_Behind_Source` | 0 | Replica is caught up |
| `Last_IO_Error` | (empty) | No IO errors |
| `Last_SQL_Error` | (empty) | No SQL errors |

### Healthy Replication Output Example:
```
*************************** 1. row ***************************
             Replica_IO_State: Waiting for source to send event
                  Source_Host: 192.168.1.1
                  Source_Port: 3301
              Replica_IO_Running: Yes
             Replica_SQL_Running: Yes
         Seconds_Behind_Source: 0
```

---

## Troubleshooting

### Issue: Replication Not Starting

**Check:**
1. Network connectivity between servers
2. Firewall rules (port 3301)
3. Replication user credentials
4. GTID configuration on both servers

```bash
# Test network connectivity
telnet 192.168.1.1 3301

# Check firewall
sudo firewall-cmd --list-ports
```

### Issue: Permission Denied Errors

**Solution:**
```bash
# Recursively fix ownership
sudo chown -R mysql:mysql /u01/data

# Check SELinux context (if applicable)
ls -laZ /u01/data
```

### Issue: Backup Restore Fails

**Check:**
1. Sufficient disk space
2. Backup file integrity
3. MySQL Enterprise Backup license

```bash
# Check disk space
df -h /u01

# Verify backup file exists
ls -la /u01/data/mysqldata/ebackup.mbi
```

---

## Python Script Usage

The accompanying Python script (`mysql_replication_setup.py`) automates all these steps.

### Run Full Workflow:
```bash
python mysql_replication_setup.py --full
```

### Run Specific Step:
```bash
# Step 1: Stop MySQL
python mysql_replication_setup.py --step 1

# Step 7: Configure replication (generate SQL)
python mysql_replication_setup.py --step 7
```

### Skip Certain Steps:
```bash
# Skip deletion and restore (useful for testing)
python mysql_replication_setup.py --full --skip-delete --skip-restore
```

### Generate SQL Only:
```bash
python mysql_replication_setup.py --sql-only
```

---

## Quick Reference Commands

```bash
# ═══════════════════════════════════════════════════════════
# COMPLETE WORKFLOW - COPY/PASTE READY
# ═══════════════════════════════════════════════════════════

# Step 1: Stop MySQL
sudo systemctl stop mysqld@mysql1
sudo systemctl status mysqld@mysql1

# Step 2: Delete old data
sudo rm -rf /u01/data/mysql1_binlog
sudo rm -rf /u01/data

# Step 3: Create directories
sudo mkdir /u01/data
sudo chown -R mysql:mysql /u01/data
sudo chmod 750 /u01/data
sudo mkdir /u01/data/mysql1_binlog
sudo chmod 750 /u01/data/mysql1_binlog
sudo chown -R mysql:mysql /u01/data/mysql1_binlog

# Step 4: Restore backup
sudo mysqlbackup --host=127.0.0.1 --port=3301 \
    --datadir=/u01/data \
    --log_bin=/u01/data/mysql1_binlog/mysql-bin \
    --backup-image=/u01/data/mysqldata/ebackup.mbi \
    --backup-dir=/u01/data/mysqldata/backup-tmp1 \
    copy-back-and-apply-log

# Step 5: Set permissions
sudo chown -R mysql:mysql /u01/data
sudo chmod 750 /u01/data
sudo chmod 750 /u01/data/mysql1_binlog
sudo chown -R mysql:mysql /u01/data/mysql1_binlog

# Step 6: Start MySQL
sudo systemctl start mysqld@mysql1
sudo systemctl status mysqld@mysql1

# Step 7: Configure replication (run in MySQL)
# STOP REPLICA;
# RESET REPLICA ALL;
# CHANGE REPLICATION SOURCE TO ...
# START REPLICA;
```

---

## Summary

| Step | Action | Server |
|------|--------|--------|
| 1 | Stop MySQL instance | Secondary (192.168.2.1) |
| 2 | Delete old directories | Secondary |
| 3 | Create new directories | Secondary |
| 4 | Restore from backup | Secondary |
| 5 | Set permissions | Secondary |
| 6 | Start MySQL instance | Secondary |
| 7 | Configure replication | Secondary (connects to Primary) |

---

*Document generated from MySQL DBA runbook*
*Last Updated: 2026-02-07*
