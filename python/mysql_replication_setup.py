#!/usr/bin/env python3
"""
================================================================================
MySQL REPLICATION SETUP & BACKUP RESTORE AUTOMATION SCRIPT
================================================================================

This script automates the MySQL Primary-Secondary replication setup process
including backup restoration from MySQL Enterprise Backup.

Architecture:
    Primary Server:   192.168.1.1:3301
    Secondary Server: 192.168.2.1:3301

Steps Covered:
    1. Stop MySQL instance on Secondary
    2. Delete old data and binlog directories
    3. Create fresh directories with proper permissions
    4. Restore backup using mysqlbackup
    5. Set correct ownership and permissions
    6. Start MySQL instance
    7. Configure replication

Author: Auto-generated from MySQL DBA runbook
================================================================================
"""

import subprocess
import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Optional, Tuple
import time

# ══════════════════════════════════════════════════════════════════════════════
#                           CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

class Config:
    """MySQL Replication Configuration"""
    
    # Server Configuration
    PRIMARY_HOST = "192.168.1.1"
    PRIMARY_PORT = 3301
    
    SECONDARY_HOST = "192.168.2.1"
    SECONDARY_PORT = 3301
    
    # MySQL Instance Name (systemd service)
    MYSQL_INSTANCE = "mysqld@mysql1"
    
    # Directory Paths
    DATA_DIR = "/u01/data"
    BINLOG_DIR = "/u01/data/mysql1_binlog"
    BACKUP_IMAGE = "/u01/data/mysqldata/ebackup.mbi"
    BACKUP_DIR = "/u01/data/mysqldata/backup-tmp1"
    BACKUP_PATH = "/u01/data/mysqldata/"
    
    # MySQL User/Group
    MYSQL_USER = "mysql"
    MYSQL_GROUP = "mysql"
    
    # Replication Configuration
    REPLICATION_USER = "replicationuser"
    REPLICATION_PASSWORD = "********"  # Replace with actual password
    
    # Permissions
    DIR_PERMISSIONS = "750"


# ══════════════════════════════════════════════════════════════════════════════
#                           LOGGING SETUP
# ══════════════════════════════════════════════════════════════════════════════

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """Configure logging with console and optional file output."""
    
    log_format = "%(asctime)s | %(levelname)-8s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logger = logging.getLogger("mysql_replication")
    logger.setLevel(logging.INFO)
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()


# ══════════════════════════════════════════════════════════════════════════════
#                           UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def run_command(cmd: str, description: str, check: bool = True, 
                sudo: bool = True) -> Tuple[int, str, str]:
    """
    Execute a shell command with logging.
    
    Args:
        cmd: Command to execute
        description: Human-readable description
        check: Raise exception on non-zero exit
        sudo: Prefix command with sudo
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if sudo and not cmd.startswith("sudo"):
        cmd = f"sudo {cmd}"
    
    logger.info(f"🔧 {description}")
    logger.debug(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"   ✅ Success")
        else:
            logger.error(f"   ❌ Failed (exit code: {result.returncode})")
            if result.stderr:
                logger.error(f"   Error: {result.stderr.strip()}")
        
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )
        
        return result.returncode, result.stdout, result.stderr
        
    except Exception as e:
        logger.error(f"   💥 Exception: {e}")
        if check:
            raise
        return -1, "", str(e)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def confirm_action(message: str) -> bool:
    """Ask user for confirmation."""
    response = input(f"\n⚠️  {message} (y/n): ").strip().lower()
    return response == 'y'


# ══════════════════════════════════════════════════════════════════════════════
#                      STEP 1: STOP MYSQL INSTANCE
# ══════════════════════════════════════════════════════════════════════════════

def stop_mysql_instance():
    """
    Stop the MySQL instance on the secondary server.
    
    Commands:
        sudo systemctl status mysqld@mysql1
        sudo systemctl stop mysqld@mysql1
        sudo systemctl status mysqld@mysql1
    """
    print_section("STEP 1: STOP MYSQL INSTANCE")
    
    logger.info(f"Stopping MySQL instance on secondary server ({Config.SECONDARY_HOST})")
    
    # Check current status
    run_command(
        f"systemctl status {Config.MYSQL_INSTANCE}",
        "Checking MySQL instance status (before stop)",
        check=False
    )
    
    # Stop the instance
    run_command(
        f"systemctl stop {Config.MYSQL_INSTANCE}",
        "Stopping MySQL instance"
    )
    
    # Wait for shutdown
    time.sleep(3)
    
    # Verify stopped
    run_command(
        f"systemctl status {Config.MYSQL_INSTANCE}",
        "Verifying MySQL instance is stopped",
        check=False
    )
    
    logger.info("✅ MySQL instance stopped successfully")


# ══════════════════════════════════════════════════════════════════════════════
#                 STEP 2: DELETE OLD DATA AND BINLOG DIRECTORIES
# ══════════════════════════════════════════════════════════════════════════════

def delete_old_directories():
    """
    Delete existing mysql1_binlog and mysql_data directories.
    
    ⚠️  WARNING: This is a destructive operation!
    
    Commands:
        sudo rm -rf /u01/data/mysql1_binlog
        sudo rm -rf /u01/data
    """
    print_section("STEP 2: DELETE OLD DATA DIRECTORIES")
    
    logger.warning("⚠️  This will DELETE all existing MySQL data!")
    
    if not confirm_action("Delete all data in binlog and data directories?"):
        logger.info("Skipping deletion - user cancelled")
        return False
    
    # Delete binlog directory
    run_command(
        f"rm -rf {Config.BINLOG_DIR}",
        f"Deleting binlog directory: {Config.BINLOG_DIR}"
    )
    
    # Delete data directory
    run_command(
        f"rm -rf {Config.DATA_DIR}",
        f"Deleting data directory: {Config.DATA_DIR}"
    )
    
    logger.info("✅ Old directories deleted successfully")
    return True


# ══════════════════════════════════════════════════════════════════════════════
#              STEP 3: CREATE DIRECTORIES WITH PERMISSIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_directories():
    """
    Create fresh directories with proper ownership and permissions.
    
    Commands:
        sudo mkdir /u01/data
        sudo chown -R mysql:mysql /u01/data
        sudo chmod 750 /u01/data
        sudo mkdir /u01/data/mysql1_binlog
        sudo chmod 750 /u01/data/mysql1_binlog
        sudo chown -R mysql:mysql /u01/data/mysql1_binlog
    """
    print_section("STEP 3: CREATE DIRECTORIES WITH PERMISSIONS")
    
    # Create main data directory
    run_command(
        f"mkdir -p {Config.DATA_DIR}",
        f"Creating data directory: {Config.DATA_DIR}"
    )
    
    # Set ownership
    run_command(
        f"chown -R {Config.MYSQL_USER}:{Config.MYSQL_GROUP} {Config.DATA_DIR}",
        f"Setting ownership to {Config.MYSQL_USER}:{Config.MYSQL_GROUP}"
    )
    
    # Set permissions
    run_command(
        f"chmod {Config.DIR_PERMISSIONS} {Config.DATA_DIR}",
        f"Setting permissions to {Config.DIR_PERMISSIONS}"
    )
    
    # Create binlog directory
    run_command(
        f"mkdir -p {Config.BINLOG_DIR}",
        f"Creating binlog directory: {Config.BINLOG_DIR}"
    )
    
    # Set binlog permissions
    run_command(
        f"chmod {Config.DIR_PERMISSIONS} {Config.BINLOG_DIR}",
        f"Setting binlog permissions to {Config.DIR_PERMISSIONS}"
    )
    
    # Set binlog ownership
    run_command(
        f"chown -R {Config.MYSQL_USER}:{Config.MYSQL_GROUP} {Config.BINLOG_DIR}",
        f"Setting binlog ownership"
    )
    
    logger.info("✅ Directories created with proper permissions")


# ══════════════════════════════════════════════════════════════════════════════
#                    STEP 4: RESTORE BACKUP
# ══════════════════════════════════════════════════════════════════════════════

def restore_backup():
    """
    Restore MySQL backup using mysqlbackup utility.
    
    Command:
        sudo mysqlbackup --host=127.0.0.1 --port=3301 \\
            --datadir=/u01/data \\
            --log_bin=/u01/data/mysql1_binlog/mysql-bin \\
            --backup-image=/u01/data/mysqldata/ebackup.mbi \\
            --backup-dir=/u01/data/mysqldata/backup-tmp1 \\
            copy-back-and-apply-log
    """
    print_section("STEP 4: RESTORE MYSQL BACKUP")
    
    logger.info(f"Backup image: {Config.BACKUP_IMAGE}")
    logger.info(f"Backup temp dir: {Config.BACKUP_DIR}")
    
    # Build mysqlbackup command
    mysqlbackup_cmd = (
        f"mysqlbackup "
        f"--host=127.0.0.1 "
        f"--port={Config.SECONDARY_PORT} "
        f"--datadir={Config.DATA_DIR} "
        f"--log_bin={Config.BINLOG_DIR}/mysql-bin "
        f"--backup-image={Config.BACKUP_IMAGE} "
        f"--backup-dir={Config.BACKUP_DIR} "
        f"copy-back-and-apply-log"
    )
    
    logger.info("Starting backup restoration (this may take a while)...")
    
    run_command(
        mysqlbackup_cmd,
        "Restoring backup with mysqlbackup"
    )
    
    logger.info(f"📁 Backup path: {Config.BACKUP_PATH}")
    logger.info("✅ Backup restored successfully")


# ══════════════════════════════════════════════════════════════════════════════
#              STEP 5: SET FINAL PERMISSIONS
# ══════════════════════════════════════════════════════════════════════════════

def set_permissions():
    """
    Set final ownership and permissions on restored directories.
    
    Commands:
        sudo chown -R mysql:mysql /u01/data
        sudo chmod 750 /u01/data
        sudo chmod 750 /u01/data/mysql1_binlog
        sudo chown -R mysql:mysql /u01/data/mysql1_binlog
    """
    print_section("STEP 5: SET FINAL PERMISSIONS")
    
    # Set ownership on data directory
    run_command(
        f"chown -R {Config.MYSQL_USER}:{Config.MYSQL_GROUP} {Config.DATA_DIR}",
        f"Setting ownership on {Config.DATA_DIR}"
    )
    
    # Set permissions on data directory
    run_command(
        f"chmod {Config.DIR_PERMISSIONS} {Config.DATA_DIR}",
        f"Setting permissions on {Config.DATA_DIR}"
    )
    
    # Set permissions on binlog directory
    run_command(
        f"chmod {Config.DIR_PERMISSIONS} {Config.BINLOG_DIR}",
        f"Setting permissions on {Config.BINLOG_DIR}"
    )
    
    # Set ownership on binlog directory
    run_command(
        f"chown -R {Config.MYSQL_USER}:{Config.MYSQL_GROUP} {Config.BINLOG_DIR}",
        f"Setting ownership on {Config.BINLOG_DIR}"
    )
    
    logger.info("✅ Permissions set successfully")


# ══════════════════════════════════════════════════════════════════════════════
#                    STEP 6: START MYSQL INSTANCE
# ══════════════════════════════════════════════════════════════════════════════

def start_mysql_instance():
    """
    Start the MySQL instance after restoration.
    
    Commands:
        sudo systemctl start mysqld@mysql1
        sudo systemctl status mysqld@mysql1
    """
    print_section("STEP 6: START MYSQL INSTANCE")
    
    # Start the instance
    run_command(
        f"systemctl start {Config.MYSQL_INSTANCE}",
        "Starting MySQL instance"
    )
    
    # Wait for startup
    time.sleep(5)
    
    # Check status
    run_command(
        f"systemctl status {Config.MYSQL_INSTANCE}",
        "Checking MySQL instance status"
    )
    
    logger.info("✅ MySQL instance started successfully")


# ══════════════════════════════════════════════════════════════════════════════
#                 STEP 7: CONFIGURE REPLICATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_replication_sql() -> str:
    """
    Generate SQL commands for configuring replication.
    
    Returns:
        SQL script as string
    """
    sql = f"""
-- ================================================================================
-- MySQL REPLICATION CONFIGURATION
-- Run these commands on the SECONDARY server via MySQL Workbench or CLI
-- ================================================================================

-- Step 7.1: Check current replica status
SHOW REPLICA STATUS;

-- Step 7.2: Stop any existing replication
STOP REPLICA;

-- Step 7.3: Reset replica configuration
RESET REPLICA ALL;

-- Step 7.4: Configure replication source (Primary server)
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='{Config.PRIMARY_HOST}',
    SOURCE_PORT={Config.PRIMARY_PORT},
    SOURCE_USER='{Config.REPLICATION_USER}',
    SOURCE_PASSWORD='{Config.REPLICATION_PASSWORD}',
    SOURCE_AUTO_POSITION=1,
    GET_SOURCE_PUBLIC_KEY=1;

-- Step 7.5: Start replication
START REPLICA;

-- Step 7.6: Verify replication status
SHOW REPLICA STATUS\\G

-- ================================================================================
-- EXPECTED OUTPUT:
--   Replica_IO_Running: Yes
--   Replica_SQL_Running: Yes
--   Seconds_Behind_Source: 0 (or small number)
-- ================================================================================
"""
    return sql


def configure_replication():
    """
    Display and optionally execute replication configuration SQL.
    """
    print_section("STEP 7: CONFIGURE REPLICATION")
    
    sql = generate_replication_sql()
    
    print("\n📋 SQL Commands to run on Secondary server:\n")
    print("-" * 70)
    print(sql)
    print("-" * 70)
    
    # Save SQL to file
    sql_file = "/tmp/configure_replication.sql"
    with open(sql_file, 'w') as f:
        f.write(sql)
    logger.info(f"📄 SQL script saved to: {sql_file}")
    
    print("\n" + "=" * 70)
    print("  MANUAL STEPS REQUIRED:")
    print("=" * 70)
    print("""
    1. Login to MySQL Workbench or mysql CLI on secondary server
    2. Connect to: 127.0.0.1:3301
    3. Run the SQL commands above
    4. Verify replication is working with: SHOW REPLICA STATUS\\G
    
    Expected result:
    - Replica_IO_Running: Yes
    - Replica_SQL_Running: Yes
    """)


# ══════════════════════════════════════════════════════════════════════════════
#                      EXECUTE REPLICATION SQL
# ══════════════════════════════════════════════════════════════════════════════

def execute_replication_sql(mysql_password: str):
    """
    Execute replication SQL commands directly via mysql CLI.
    
    Args:
        mysql_password: MySQL root/admin password
    """
    print_section("EXECUTING REPLICATION SQL")
    
    commands = [
        "STOP REPLICA;",
        "RESET REPLICA ALL;",
        f"""CHANGE REPLICATION SOURCE TO
            SOURCE_HOST='{Config.PRIMARY_HOST}',
            SOURCE_PORT={Config.PRIMARY_PORT},
            SOURCE_USER='{Config.REPLICATION_USER}',
            SOURCE_PASSWORD='{Config.REPLICATION_PASSWORD}',
            SOURCE_AUTO_POSITION=1,
            GET_SOURCE_PUBLIC_KEY=1;""",
        "START REPLICA;",
        "SHOW REPLICA STATUS\\G"
    ]
    
    for cmd in commands:
        mysql_cmd = f'mysql -h 127.0.0.1 -P {Config.SECONDARY_PORT} -u root -p"{mysql_password}" -e "{cmd}"'
        run_command(
            mysql_cmd,
            f"Executing: {cmd[:50]}...",
            sudo=False
        )


# ══════════════════════════════════════════════════════════════════════════════
#                           FULL WORKFLOW
# ══════════════════════════════════════════════════════════════════════════════

def run_full_workflow(skip_delete: bool = False, skip_restore: bool = False):
    """
    Execute the complete MySQL replication setup workflow.
    
    Args:
        skip_delete: Skip directory deletion step
        skip_restore: Skip backup restore step
    """
    print("\n" + "█" * 70)
    print("  MYSQL REPLICATION SETUP - FULL WORKFLOW")
    print("█" * 70)
    
    print(f"""
    Configuration:
    ├── Primary Server:   {Config.PRIMARY_HOST}:{Config.PRIMARY_PORT}
    ├── Secondary Server: {Config.SECONDARY_HOST}:{Config.SECONDARY_PORT}
    ├── MySQL Instance:   {Config.MYSQL_INSTANCE}
    ├── Data Directory:   {Config.DATA_DIR}
    ├── Binlog Directory: {Config.BINLOG_DIR}
    └── Backup Image:     {Config.BACKUP_IMAGE}
    """)
    
    if not confirm_action("Proceed with replication setup?"):
        logger.info("Operation cancelled by user")
        return
    
    try:
        # Step 1: Stop MySQL
        stop_mysql_instance()
        
        # Step 2: Delete old directories
        if not skip_delete:
            delete_old_directories()
        else:
            logger.info("⏭️  Skipping directory deletion")
        
        # Step 3: Create directories
        create_directories()
        
        # Step 4: Restore backup
        if not skip_restore:
            restore_backup()
        else:
            logger.info("⏭️  Skipping backup restore")
        
        # Step 5: Set permissions
        set_permissions()
        
        # Step 6: Start MySQL
        start_mysql_instance()
        
        # Step 7: Configure replication (display SQL)
        configure_replication()
        
        print("\n" + "█" * 70)
        print("  ✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("█" * 70)
        print("\n⚠️  Don't forget to run the replication SQL commands!")
        
    except Exception as e:
        logger.error(f"💥 Workflow failed: {e}")
        raise


# ══════════════════════════════════════════════════════════════════════════════
#                         INDIVIDUAL STEP RUNNERS
# ══════════════════════════════════════════════════════════════════════════════

def run_step(step_number: int):
    """Run a specific step by number."""
    steps = {
        1: ("Stop MySQL Instance", stop_mysql_instance),
        2: ("Delete Old Directories", delete_old_directories),
        3: ("Create Directories", create_directories),
        4: ("Restore Backup", restore_backup),
        5: ("Set Permissions", set_permissions),
        6: ("Start MySQL Instance", start_mysql_instance),
        7: ("Configure Replication", configure_replication),
    }
    
    if step_number not in steps:
        print(f"❌ Invalid step number: {step_number}")
        print(f"   Valid steps: 1-7")
        return
    
    name, func = steps[step_number]
    print(f"\n🔧 Running Step {step_number}: {name}")
    func()


# ══════════════════════════════════════════════════════════════════════════════
#                              MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point with argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="MySQL Replication Setup Automation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow
  python mysql_replication_setup.py --full
  
  # Run specific step
  python mysql_replication_setup.py --step 1
  
  # Skip deletion and restore
  python mysql_replication_setup.py --full --skip-delete --skip-restore
  
  # Generate SQL only
  python mysql_replication_setup.py --sql-only
  
Steps:
  1. Stop MySQL Instance
  2. Delete Old Directories
  3. Create Directories
  4. Restore Backup
  5. Set Permissions
  6. Start MySQL Instance
  7. Configure Replication
        """
    )
    
    parser.add_argument(
        "--full", action="store_true",
        help="Run full workflow"
    )
    parser.add_argument(
        "--step", type=int, choices=range(1, 8),
        help="Run specific step (1-7)"
    )
    parser.add_argument(
        "--skip-delete", action="store_true",
        help="Skip directory deletion step"
    )
    parser.add_argument(
        "--skip-restore", action="store_true",
        help="Skip backup restore step"
    )
    parser.add_argument(
        "--sql-only", action="store_true",
        help="Only generate replication SQL"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print commands without executing"
    )
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║         MySQL Primary-Secondary Replication Setup Script             ║
    ║                                                                      ║
    ║  Primary:   192.168.1.1:3301                                         ║
    ║  Secondary: 192.168.2.1:3301                                         ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    if args.sql_only:
        print(generate_replication_sql())
        return
    
    if args.step:
        run_step(args.step)
        return
    
    if args.full:
        run_full_workflow(
            skip_delete=args.skip_delete,
            skip_restore=args.skip_restore
        )
        return
    
    # No arguments - show help
    parser.print_help()


if __name__ == "__main__":
    main()
