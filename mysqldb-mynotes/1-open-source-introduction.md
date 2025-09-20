#### Overview of MySQL


Introduction to MySQL by showing how to use the mysql client program to create and use a simple database. mysql (sometimes referred to as the “terminal monitor” or just “monitor”) is an interactive program that enables you to connect to a MySQL server, run queries, and view the results. mysql may also be used in batch mode: you place your queries in a file beforehand, then tell mysql to execute the contents of the file. Both ways of using mysql are covered here.

To see a list of options provided by mysql, invoke it with the --help option:
```bash
shell> mysql –help
```

This assumes that mysql is installed on your machine and that a MySQL server is available to which you can connect. 

Connecting to and disconnecting from the Server To connect to the server, you will usually need to provide a MySQL user name when you invoke mysql and, most likely, a password. If the server runs on a machine other than the one where you log in, you will also need to specify a host name. Contact your administrator to find out what connection parameters you should use to connect (that is, what host, user name, and password to use). Once you know the proper parameters, you should be able to connect like this:
```bash
shell> mysql -h host -u user –p
```
```bash
Enter password: ********host and user represent the host name where your MySQL server is running and the user name of your MySQL account. Substitute appropriate values for your setup. The ******** represents your password; enter it when mysql displays the Enter password: prompt. If that works, you should see some introductory information followed by a
```
```bash
mysql> prompt:
```
```bash
shell> mysql -h host -u user –p
```
# MySQL Overview

### Connecting to MySQL

* The `mysql>` prompt indicates that MySQL is ready to accept SQL statements.

* If you are logging in on the **same machine** where MySQL is running, you can omit the host option:

  ```bash
  shell> mysql -u user -p
  ```

* If you see an error like:

  ```
  ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/tmp/mysql.sock' (2)
  ```

  it means the **MySQL server daemon (on Unix)** or **service (on Windows)** is not running.

* Some installations allow connections as the **anonymous (unnamed) user** on the local host. In that case, you may connect simply with:

  ```bash
  shell> mysql
  ```

* After connecting successfully, you can disconnect with:

  ```sql
  mysql> QUIT
  ```

  or

  ```sql
  mysql> \q
  ```

  On Unix, you can also exit using **Control + D**.

---

### History of MySQL

* **Founded:** 1995 (by Michael “Monty” Widenius and David Axmark)
* **First internal release:** May 23, 1995
* **Age:** \~26+ years old database system
* **License:** Free and open-source under the GNU GPL, with proprietary licensing options
* **Initial ownership:** MySQL AB (a Swedish company)
* **Acquisitions:**

  * Acquired by **Sun Microsystems** in 2008
  * Sun acquired by **Oracle** in 2010
* **MariaDB fork:** Started in 2009 by the original authors of MySQL (to ensure continuity of open-source development).

  * MariaDB Foundation established: December 2012
  * SkySQL renamed to **MariaDB Corporation Ab** in October 2014
  * Naming: **MySQL** was named after Monty’s daughter *My*; **MariaDB** after his other daughter *Maria*.

---

### Major Release Background

* **Windows version** released: January 8, 1998 (Windows 95/NT)
* **Version 3.23** – January 2001
* **Version 4.0** – March 2003 (introduced unions)
* **Version 4.1** – October 2004 (R-trees, B-trees, subqueries, prepared statements)
* **Version 5.0** – October 2005 (cursors, stored procedures, triggers, views)
* **Version 5.1** – November 2008 (event scheduler, partitioning, plugin API, row-based replication, server log tables)

  * Performance note: MySQL 5.1 performed poorly in data warehousing due to limited multi-core query execution.

---

### Technology

* **MySQL**

  * Written in: C, C++
  * Supported OS: Linux, Solaris, macOS, Windows, FreeBSD

* **MariaDB**

  * Written in: C, C++, Perl, Bash
  * Supported OS: Linux, macOS, Windows

---

### Editions and Backup Options

* **MySQL Editions**:

  * Enterprise Edition
  * Standard Edition
  * Community Edition

* **Backup Support**:

  * Online backups **not supported** in Community Edition
  * Physical backups supported with:

    * **MySQL Enterprise Backup (MEB)** → Paid
    * **Percona XtraBackup** → GPL (open-source alternative)

---

Perfect 👍 — here’s a clean **comparison table between MySQL and MariaDB** to complement the improved notes:

---

# MySQL vs MariaDB – Comparison

| Feature / Aspect          | **MySQL**                                                       | **MariaDB**                                                                                       |
| ------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Origin**                | Created by Michael Widenius & David Axmark in 1995              | Forked from MySQL in 2009 by the original authors                                                 |
| **Ownership**             | Oracle Corporation (since 2010)                                 | MariaDB Foundation & MariaDB Corporation                                                          |
| **License**               | Dual-licensed: GPL + proprietary                                | GPL (open-source)                                                                                 |
| **Naming**                | Named after Monty’s daughter **My**                             | Named after Monty’s daughter **Maria**                                                            |
| **Programming Languages** | C, C++                                                          | C, C++, Perl, Bash                                                                                |
| **Supported OS**          | Linux, Solaris, macOS, Windows, FreeBSD                         | Linux, macOS, Windows                                                                             |
| **Storage Engines**       | InnoDB (default), MyISAM, etc.                                  | InnoDB (XtraDB), MyRocks, Aria, ColumnStore, Cassandra, etc. (more variety)                       |
| **Performance**           | Stable, but slower in some complex queries (e.g., DW/Analytics) | Faster for certain workloads (parallel replication, thread pool, optimizer improvements)          |
| **Replication**           | Asynchronous & semi-synchronous replication                     | Asynchronous, semi-synchronous, and **parallel replication** (multi-source replication supported) |
| **JSON Support**          | Native JSON data type (5.7+)                                    | JSON functions but stored as LONGTEXT (not native type)                                           |
| **Backup Tools**          | Enterprise Backup (MEB – Paid), Percona XtraBackup (Community)  | MariaDB Backup (open-source), Percona XtraBackup                                                  |
| **Cluster Solutions**     | MySQL NDB Cluster                                               | Galera Cluster (built-in for synchronous multi-master replication)                                |
| **Editions**              | Enterprise, Standard, Community                                 | Community (all features open-source)                                                              |
| **Popularity**            | Widely used in enterprise (due to Oracle support)               | Growing rapidly in open-source and cloud-native environments                                      |
| **Notable Users**         | Facebook, Twitter, YouTube, Booking.com                         | Wikipedia, Google, Red Hat, Alibaba, Wikimedia Foundation                                         |

---

👉 **Summary**:

* Use **MySQL** if you need Oracle support, enterprise features, or integration with Oracle ecosystem.
* Use **MariaDB** if you want **fully open-source, more storage engines, better replication, and faster performance** for analytics/OLAP.

---

📌 1995 → MySQL founded

📌 1998 → Windows version released

📌 2001–2005 → Major releases (3.23, 4.0, 4.1, 5.0)

📌 2008 → Sun Microsystems acquires MySQL AB

📌 2009 → MariaDB fork created

📌 2010 → Oracle acquires Sun (and MySQL)

📌 2012 → MariaDB Foundation established

📌 2014 → SkySQL renamed MariaDB Corporation Ab

### MySQL Features
---

# ✅ Improved Features of MySQL

1. **Relational Database Management System (RDBMS)**

   * MySQL is a widely used RDBMS that organizes data into structured **tables with rows and columns**, supporting relationships via **foreign keys**.

2. **Ease of Use**

   * Requires only basic SQL knowledge to get started.
   * Comes with tools like **MySQL Workbench** for GUI-based management.
   * Quick learning curve compared to enterprise databases like Oracle or DB2.

3. **Security**

   * Solid data security layer with **user privilege management** and **role-based access**.
   * Passwords encrypted using **SHA-256 / caching\_sha2\_password** (MySQL 8.x).
   * Supports **SSL/TLS connections** for secure client-server communication.

4. **Client/Server Architecture**

   * MySQL follows a **multi-tier architecture**:

     * **Server:** MySQL Daemon (mysqld).
     * **Clients:** Applications, scripts, or users connecting via SQL or APIs.
     * **APIs:** Connectors for Java, Python, C/C++, PHP, Node.js, Go, etc.

5. **Open Source & Free to Download**

   * Community Edition is **free under GPL license**.
   * Enterprise Edition (paid) adds features like **MySQL Enterprise Backup, monitoring, security plugins**.

6. **Scalability**

   * Can handle **billions of rows** with proper indexing and sharding.
   * Default table size limit is \~4 GB, extendable up to **64 TB (InnoDB)** depending on OS and hardware.
   * Used in large-scale applications (e.g., Facebook, Uber).

7. **Cross-Platform Compatibility**

   * Runs on **Windows, Linux, macOS, FreeBSD, Solaris, AIX, NetWare, and others**.
   * Supports both **on-premises** and **cloud-native** deployments (Google Cloud SQL, AWS RDS, Azure Database for MySQL).

8. **Transaction Support**

   * Full **ACID compliance** (Atomicity, Consistency, Isolation, Durability) with the **InnoDB engine**.
   * Supports **commit, rollback, and crash recovery**.
   * Advanced isolation levels: READ COMMITTED, REPEATABLE READ, SERIALIZABLE.

9. **Performance**

   * Optimized storage engines (InnoDB, MyISAM, Memory, NDB, etc.).
   * **Query optimizer** and indexing (BTREE, HASH, FULLTEXT, SPATIAL).
   * Supports **partitioning, replication, and sharding** for horizontal scaling.

10. **Flexibility**

    * Embeddable in applications (via libmysqld).
    * Supports both **OLTP (transactions)** and some **OLAP (analytics)** workloads.
    * JSON, spatial (GIS), and full-text search support.

11. **Developer Productivity**

    * Features like **Stored Procedures, Triggers, Views, Cursors, Events**.
    * **Window functions** and **CTEs (Common Table Expressions)** in MySQL 8.x.
    * Rich ecosystem of connectors, drivers, and frameworks (Spring Boot, Django, Laravel, Node.js, etc.).

---

# 🚀 Newer Features in MySQL 8.x

* **Native JSON support** → JSON data type + indexing.
* **CTEs & Window Functions** → Recursive queries, analytics functions.
* **Role-Based Access Control (RBAC)** → Simplified user management.
* **Invisible Indexes** → Test indexes without using them in queries.
* **Histograms** → Better query optimization with non-indexed columns.
* **GIS Enhancements** → Spatial indexes for location-based applications.
* **Data Dictionary** → Replaced old metadata storage with transactional dictionary.
* **Replication Enhancements** → Group replication, multi-source replication, auto-failover.

---

# 🌍 Common Use Cases

1. **Web Applications**

   * Powering **LAMP/LEMP stacks** (Linux, Apache/Nginx, MySQL, PHP/Python/Perl).
   * Popular in **WordPress, Drupal, Joomla, Magento**.

2. **E-commerce Platforms**

   * Used by Amazon, Shopify, Flipkart-like platforms for **catalogs, transactions, and customer data**.

3. **Banking & FinTech**

   * Secure transaction management with **ACID compliance**.

4. **Cloud & SaaS Applications**

   * Deployed in **AWS RDS, Google Cloud SQL, Azure Database for MySQL**.

5. **Big Data & Analytics**

   * With **replication + sharding**, MySQL can handle **analytics workloads**.
   * Often paired with **Hadoop, Spark, or BI tools**.

6. **Social Media & Streaming**

   * Used in **Facebook, Twitter, YouTube** for messaging, user profiles, and logging systems.

---


