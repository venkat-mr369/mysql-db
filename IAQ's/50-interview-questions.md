## 50 MySQL Server DBA Interview Use Case Questions and Solutions


### Administration & Configuration

1. **How do you install MySQL on Linux using Yum?**  
   *Solution:*  
   ```
   sudo yum install mysql-server
   sudo systemctl start mysqld
   ```

2. **How can you find the MySQL configuration file location?**  
   *Solution:*  
   ```
   mysql --help | grep my.cnf
   ```
   or  
   ```
   SHOW VARIABLES LIKE 'config%';
   ```

3. **How do you create a new MySQL user with all privileges?**  
   *Solution:*  
   ```sql
   CREATE USER 'admin'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;
   FLUSH PRIVILEGES;
   ```

4. **How do you reset a forgotten root password on MySQL?**  
   *Solution:*
   Stop MySQL, start in safe mode with `--skip-grant-tables`, log in, and update via:
   ```sql
   UPDATE mysql.user SET authentication_string=PASSWORD('newpass') WHERE User='root';
   FLUSH PRIVILEGES;
   ```

5. **Explain how you enable binary logging for point-in-time recovery.**  
   *Solution:*  
   Add `log_bin = mysql-bin` in my.cnf and restart MySQL.

***

### Backup and Restore

6. **How do you perform a full backup using mysqldump?**  
   *Solution:*  
   ```
   mysqldump -u root -p --all-databases > all_backup.sql
   ```

7. **How can you restore a single database from a mysqldump file?**  
   *Solution:*  
   ```
   mysql -u root -p mydb < mydb_backup.sql
   ```

8. **How do you take a hot backup of a large InnoDB database?**  
   *Solution:*  
   Use Percona XtraBackup tool.

9. **Explain how you would automate nightly backups.**  
   *Solution:*  
   Create a shell script with `mysqldump`, schedule via cron.

10. **What’s the best way to backup databases on a replication master and why?**  
    *Solution:*  
    Use mysqldump with `--single-transaction` to ensure consistency.

***

### Performance & Monitoring

11. **How do you find slow queries in MySQL?**  
    *Solution:*  
    Enable slow_query_log in my.cnf, review queries in the log.

12. **How do you identify which table has the most writes?**  
    *Solution:*  
    Use `SHOW TABLE STATUS` or the Performance Schema.

13. **How can you check current MySQL connections?**  
    *Solution:*  
    ```sql
    SHOW PROCESSLIST;
    ```

14. **Name common causes of performance issues with ORDER BY.**  
    *Solution:*  
    Missing indexes, large data sets, sorting on non-indexed columns.

15. **How do you add an index to improve SELECT performance?**  
    *Solution:*  
    ```sql
    CREATE INDEX idx_col ON tablename(column_name);
    ```

16. **If a query runs slowly, how would you tune it?**  
    *Solution:*  
    Use EXPLAIN, optimize schema, add indexes, or rewrite the query.

17. **How can you reduce MySQL memory usage?**  
    *Solution:*  
    Tune `innodb_buffer_pool_size`, `key_buffer_size`, etc., in my.cnf.

18. **How do you enable and use the Performance Schema?**  
    *Solution:*  
    Set `performance_schema=ON` in my.cnf, restart, query its tables.

***

### Security

19. **How do you revoke all privileges from a user?**  
    *Solution:*  
    ```sql
    REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'user'@'host';
    ```

20. **How can you check for users with blank passwords?**  
    *Solution:*  
    ```sql
    SELECT host, user FROM mysql.user WHERE authentication_string='';
    ```

21. **How do you enforce password policies?**  
    *Solution:*  
    Use `validate_password` plugin and set policies in my.cnf.

22. **How can you allow only SSL connections for a user?**  
    *Solution:*  
    ```sql
    CREATE USER 'user'@'%' REQUIRE SSL;
    ```

23. **How would you detect SQL injection attempts?**  
    *Solution:*  
    Monitor logs; use prepared statements in applications.

***

### Replication & High Availability

24. **How do you set up replication between a master and slave?**  
    *Solution:*  
    Configure `log_bin` and `server-id`, create a replication user, run `CHANGE MASTER TO`, start `START SLAVE`.

25. **How do you show replication status on a slave?**  
    *Solution:*  
    ```sql
    SHOW SLAVE STATUS\G
    ```

26. **How do you skip a single replication error and resume?**  
    *Solution:*  
    ```sql
    SET GLOBAL sql_slave_skip_counter = 1; START SLAVE;
    ```

27. **How do you monitor replication lag?**  
    *Solution:*  
    Check `Seconds_Behind_Master` in `SHOW SLAVE STATUS`.

28. **Explain GTID-based replication.**  
    *Solution:*  
    Uses global transaction IDs for easy failover and consistency.

29. **How do you promote a replica to master?**  
    *Solution:*  
    STOP SLAVE; reset master; update other replicas' settings.

***

### Maintenance, Upgrades, Migration

30. **How do you safely upgrade MySQL from 5.7 to 8.0?**  
    *Solution:*  
    Backup everything, check for deprecated features, run `mysql_upgrade`, test before switching production.

31. **How do you migrate data from MySQL to PostgreSQL?**  
    *Solution:*  
    Use tools like `pgloader` or export via CSV for import.

32. **How do you move a MySQL database between servers?**  
    *Solution:*  
    Use `mysqldump` or cold copy data files if versions match.

33. **How do you find and drop unused indexes?**  
    *Solution:*  
    Use Performance Schema and Information Schema to identify, then drop with `DROP INDEX`.

***

### Troubleshooting & Recovery

34. **If MySQL won’t start, what logs do you check first?**  
    *Solution:*  
    MySQL error log (`/var/log/mysqld.log`), system logs.

35. **How do you repair a corrupted InnoDB table?**  
    *Solution:*  
    Run `innodb_force_recovery` in my.cnf, then dump table and recreate.

36. **How do you recover a deleted table?**  
    *Solution:*  
    Restore backup or use point-in-time recovery with binary logs.

37. **What do you do if replication stops due to a duplicate entry?**  
    *Solution:*  
    Skip error, fix data inconsistency, resume replication.

38. **How do you reset the autoincrement value for a table?**  
    *Solution:*  
    ```sql
    ALTER TABLE mytable AUTO_INCREMENT = 100;
    ```

39. **What steps do you follow if disk space runs out?**  
    *Solution:*  
    Free up space, move logs, rotate or purge large tables.

40. **How can you check for blocked or locked queries?**  
    *Solution:*  
    Query `INFORMATION_SCHEMA.PROCESSLIST` for locks.

***

### Advanced Features & Optimization

41. **How do you partition a large table?**  
    *Solution:*  
    Use `ALTER TABLE ... PARTITION BY ...`.

42. **How do you enable and use fulltext search in MySQL?**  
    *Solution:*  
    Create FULLTEXT index, use `MATCH ... AGAINST` in queries.

43. **How do you define and use triggers?**  
    *Solution:*  
    ```sql
    CREATE TRIGGER my_trigger AFTER INSERT ON mytable
      FOR EACH ROW SET NEW.status = 'active';
    ```

44. **How do you store and retrieve JSON data?**  
    *Solution:*  
    Use `JSON` column type and functions like `JSON_EXTRACT`.

45. **How do you enforce referential integrity?**  
    *Solution:*  
    Use `FOREIGN KEY` constraints.

***

### Miscellaneous Real-World Scenarios

46. **How do you allow remote connections to MySQL securely?**  
    *Solution:*  
    Open port 3306, firewall policy, require SSL connections.

47. **How do you mask sensitive data in a SELECT result?**  
    *Solution:*  
    Use functions (e.g., substring, replace), views for limited access.

48. **How can you detect orphaned records (foreign key mismatches)?**  
    *Solution:*  
    Use `LEFT JOIN ... WHERE child_table.col IS NULL`.

49. **How do you schedule database jobs (backups, reports) on MySQL?**  
    *Solution:*  
    Use event scheduler or external cron jobs.

50. **How do you audit user activity in MySQL?**  
    *Solution:*  
    Enable general log or use MySQL Audit Plugin, analyze log files.

***
