👍 **MariaDB vs MySQL** —

---

# 📌 1. MariaDB Versions (Major Releases)

MariaDB is a **community-driven fork of MySQL (since 2010)**. Key stable releases:

| Version                     | Release Year | Key Features                                                                                              |
| --------------------------- | ------------ | --------------------------------------------------------------------------------------------------------- |
| **MariaDB 5.1 / 5.2 / 5.3** | 2010–2012    | Fork of MySQL 5.1, added new storage engines (Aria, XtraDB), microsecond support, optimizer improvements. |
| **MariaDB 5.5**             | 2012         | First *drop-in replacement* for MySQL 5.5, added subquery optimizations.                                  |
| **MariaDB 10.0**            | 2014         | Multi-source replication, GTID support, parallel replication.                                             |
| **MariaDB 10.1**            | 2015         | Galera Cluster built-in, encryption at rest, dynamic columns.                                             |
| **MariaDB 10.2**            | 2017         | Window functions, common table expressions (CTEs), JSON functions.                                        |
| **MariaDB 10.3**            | 2018         | System-versioned tables (temporal), SEQUENCEs, Oracle compatibility.                                      |
| **MariaDB 10.4**            | 2019         | Invisible columns, instant ADD COLUMN, user password history.                                             |
| **MariaDB 10.5**            | 2020         | ColumnStore updates, S3 storage, new replication modes.                                                   |
| **MariaDB 10.6 (LTS)**      | 2021         | JSON\_TABLE(), table cache, optimizer improvements.                                                       |
| **MariaDB 10.9–10.11**      | 2022–2023    | New features merged faster, cloud enhancements.                                                           |
| **MariaDB 11.x**            | 2023+        | Current active development, performance + distributed SQL features.                                       |

---

# 📌 2. MariaDB Editions

MariaDB now has **different editions**, unlike MySQL’s split into Community vs Enterprise.

### **MariaDB Community Edition (Open Source)**

* Free forever.
* Includes core DB engine + pluggable storage engines (InnoDB/XtraDB, Aria, MyRocks, ColumnStore, Spider, etc.).
* Built-in Galera Cluster for synchronous replication.
* Advanced SQL features (window functions, CTEs, temporal tables, invisible columns, SEQUENCEs).

### **MariaDB Enterprise Edition**

* Paid subscription.
* Includes all community features **+ support + certified builds**.
* Additional features:

  * **Enterprise ColumnStore** (HTAP: Hybrid Transactional/Analytical).
  * **Enterprise Cluster** (Galera certified).
  * **Enterprise Spider** (sharding/federation).
  * **Enterprise Encryption & Security** (LDAP/Kerberos, FIPS, auditing).
  * **Enterprise Backup** (faster, consistent, parallel).
  * **Enterprise Observability** (monitoring + troubleshooting).
* SLAs and vendor support.

### **MariaDB SkySQL (Cloud Edition)**

* Fully managed DBaaS (Database as a Service).
* Runs on **multi-cloud (AWS, GCP, Azure)**.
* Options for:

  * Single-node transactional
  * Distributed SQL
  * Analytical (ColumnStore HTAP)
  * Auto-scaling, HA, and global clusters.

---

# 📌 3. Feature Comparison: **MariaDB vs MySQL**

| Feature                          | MariaDB                                                                                         | MySQL                                                                      | Advantage                                                                            |
| -------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **License**                      | GPL v2 (community)                                                                              | Oracle: Community (GPL v2) + Enterprise (commercial)                       | MariaDB is fully open-source.                                                        |
| **Storage Engines**              | Aria, XtraDB, MyRocks, ColumnStore, Spider, S3, TokuDB (deprecated), InnoDB                     | InnoDB (main), MyISAM (deprecated), NDB (Cluster), MyRocks (Facebook fork) | MariaDB offers **more engines**, flexible workloads (OLTP + OLAP + distributed SQL). |
| **Replication**                  | Built-in Galera Cluster (sync, multi-master), async/semisync replication, multi-source          | Async, Group Replication, InnoDB Cluster, NDB Cluster                      | MariaDB’s **Galera is battle-tested** for HA, MySQL’s Group Replication is newer.    |
| **JSON Support**                 | JSON functions (real JSON type in 10.2+). JSON\_TABLE in 10.6                                   | JSON type native (binary optimized), rich functions                        | MySQL has **better native JSON**, but MariaDB closing gap.                           |
| **SQL Features**                 | Window functions, CTEs, temporal tables, SEQUENCEs, invisible columns, Oracle-style PL/SQL mode | Window functions, CTEs, JSON\_TABLE, Histograms                            | MariaDB often **adds features earlier** and focuses on Oracle compatibility.         |
| **Optimizer**                    | Cost-based + advanced subquery optimization                                                     | Cost-based optimizer, histogram stats                                      | MariaDB faster for **complex joins/subqueries**.                                     |
| **Clustering/HA**                | Galera built-in, Spider for sharding, MaxScale proxy                                            | InnoDB Cluster (Group Replication), MySQL Router, NDB Cluster              | MariaDB has **simpler built-in clustering**.                                         |
| **Backup**                       | MariaDB Backup (free), Enterprise Backup (paid, parallel)                                       | `mysqldump`, MySQL Enterprise Backup (paid), clone plugin                  | MariaDB offers **free hot backup**.                                                  |
| **Cloud**                        | SkySQL (multi-cloud), Kubernetes support                                                        | MySQL HeatWave (Oracle Cloud), AWS RDS/Aurora MySQL, GCP SQL               | MySQL integrates best with **Oracle HeatWave**, MariaDB is **cloud-agnostic**.       |
| **Performance (OLTP)**           | Very fast on mixed workloads due to pluggable engines (Aria, MyRocks)                           | Strong OLTP on InnoDB                                                      | MariaDB better for **flexible workloads**.                                           |
| **Performance (Analytics/HTAP)** | ColumnStore (distributed, columnar), OLAP queries                                               | MySQL HeatWave (in-memory analytics, but Oracle-only)                      | MariaDB’s **HTAP is cloud-portable**.                                                |
| **Ecosystem**                    | MaxScale (routing, firewall, sharding), SkySQL                                                  | MySQL Router, MySQL Shell, Oracle-only ecosystem                           | MariaDB more **open ecosystem**.                                                     |

---

# 📌 4. Deep Advantages of MariaDB over MySQL

### 🔹 **1. Openness**

* 100% community-driven (MariaDB Foundation).
* MySQL roadmap controlled by Oracle → features often go Enterprise-only.

### 🔹 **2. Built-in Clustering**

* Galera Cluster integrated, no extra licenses.
* MySQL requires **Group Replication** or NDB Cluster (complex setup, enterprise-heavy).

### 🔹 **3. Storage Engine Flexibility**

* MariaDB supports **transactional, analytical, and distributed engines** in one DB.
* MySQL mainly tied to InnoDB.

### 🔹 **4. Performance Optimizations**

* MariaDB query optimizer better for **complex joins/subqueries**.
* Parallel replication outperforms MySQL in some workloads.

### 🔹 **5. Enterprise Features for Free**

* MariaDB Backup, Galera, MaxScale (community), Oracle compatibility → included.
* MySQL puts many features behind Enterprise edition.

### 🔹 **6. Hybrid Workloads (HTAP)**

* ColumnStore allows **OLTP + OLAP in same DB**.
* MySQL HeatWave (only Oracle Cloud, not free).

---

# 📌 5. When to Choose MariaDB vs MySQL?

✅ **MariaDB is better if:**

* You want **full open source** (no vendor lock-in).
* You need **Galera Cluster** (multi-master HA).
* You run **mixed workloads** (OLTP + OLAP).
* You want **more flexibility with engines**.
* You need **Oracle compatibility (PL/SQL-like syntax)**.

✅ **MySQL is better if:**

* You use **AWS RDS/Aurora, GCP SQL, or Oracle Cloud** (native support).
* You rely heavily on **JSON workloads** (MySQL JSON is stronger).
* You want **HeatWave analytics** (but tied to Oracle Cloud).
* Your apps depend on **Oracle’s MySQL Enterprise features**.

---

