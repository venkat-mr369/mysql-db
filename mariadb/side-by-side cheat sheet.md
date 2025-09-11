 **side-by-side cheat sheet**:

👉 Versions (chronological)
👉 Key features per version
👉 MariaDB vs MySQL difference
👉 Advantage summary

---

# 📌 MariaDB vs MySQL – Version Feature Cheat Sheet

| Release                     | MySQL Features                                                                                            | MariaDB Features                                                                                                                                                                | Advantage                                                                                                  |
| --------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **5.1 (2008)**              | Partitioning, event scheduler, row-based replication.                                                     | Fork started from MySQL 5.1; MariaDB added **Aria engine**, optimizer fixes, microsecond support.                                                                               | MariaDB improved base reliability + crash recovery.                                                        |
| **5.5 (2012)**              | InnoDB default, semi-sync replication, performance schema.                                                | MariaDB 5.5 fully drop-in replacement, added **subquery optimizer improvements**.                                                                                               | MariaDB more performant with complex queries.                                                              |
| **5.6 (2013)**              | GTIDs, parallel replication, improved InnoDB, memcached API, full-text search in InnoDB.                  | MariaDB 10.0: **multi-source replication**, GTIDs, **parallel replication (advanced)**.                                                                                         | MariaDB offered **multi-source** first; better replication flexibility.                                    |
| **5.7 (2015)**              | Native JSON data type, generated (virtual) columns, improved replication, sys schema.                     | MariaDB 10.1: **Galera Cluster built-in**, **data-at-rest encryption**, **dynamic columns**.                                                                                    | MySQL: JSON first. MariaDB: built-in clustering + security.                                                |
| **8.0 (2018)**              | Roles, window functions, CTEs, histograms, invisible indexes, transactional data dictionary, JSON\_TABLE. | MariaDB 10.2: **Window functions, CTEs** (earlier than MySQL), JSON functions, Oracle SQL mode. <br> MariaDB 10.3: **temporal tables, SEQUENCEs, Oracle PL/SQL compatibility**. | MariaDB: faster to adopt **advanced SQL features**, Oracle compatibility. MySQL: **better JSON (binary)**. |
| **8.0 Updates (2019–2020)** | Clone plugin, InnoDB enhancements, security (caching\_sha2 auth).                                         | MariaDB 10.4: **Invisible columns, instant ALTER TABLE**, user password history. <br> MariaDB 10.5: **S3 engine, MyRocks integration, ColumnStore updates**.                    | MariaDB = **cloud-ready features** (S3, MyRocks), MySQL = **security/auth maturity**.                      |
| **HeatWave Era (2021+)**    | MySQL 8.0 + **HeatWave** (in-memory analytics, ML). Only on Oracle Cloud.                                 | MariaDB 10.6 LTS: **JSON\_TABLE, optimizer improvements, ColumnStore HTAP built-in**. <br> MariaDB 10.9–10.11: Kubernetes operators, cloud-native features.                     | MariaDB = **open HTAP, multi-cloud**. MySQL HeatWave = powerful but **Oracle Cloud lock-in**.              |
| **Latest (2023–2025)**      | MySQL 8.0 stable, MySQL 9.x (early dev, focus on HeatWave & ML).                                          | MariaDB 11.x: **distributed SQL, Spider engine for sharding, ColumnStore scale-out**.                                                                                           | MariaDB evolving towards **Postgres-style distributed SQL**, MySQL evolving **Oracle-centric analytics**.  |

---

# 📌 Editions Comparison (Cheat Sheet)

| Category              | MariaDB                                                                              | MySQL                                                                           |
| --------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Community (Free)**  | All storage engines, Galera Cluster, ColumnStore (HTAP), Spider, MaxScale (basic).   | Limited to InnoDB, replication, JSON. No HA cluster (except Group Replication). |
| **Enterprise (Paid)** | Enterprise Backup, Security (LDAP, Kerberos, FIPS), Observability, certified builds. | Enterprise Backup, Firewall, TDE, Audit, Enterprise Monitor.                    |
| **Cloud**             | **SkySQL (multi-cloud)** – supports OLTP, OLAP, distributed SQL.                     | **HeatWave (Oracle Cloud)** – OLTP + in-memory OLAP/ML.                         |
| **Clustering/HA**     | Galera built-in, Spider for sharding, MaxScale proxy.                                | InnoDB Cluster (GR + Router), NDB Cluster (separate product).                   |
| **Storage Engines**   | Aria, XtraDB, InnoDB, MyRocks, ColumnStore, Spider, S3, TokuDB.                      | InnoDB, NDB, MyISAM (deprecated).                                               |
| **Backup**            | **MariaDB Backup (free)** + Enterprise Backup.                                       | `mysqldump`, Clone Plugin, Enterprise Backup (paid).                            |

---

# 📌 Key Advantages (One-Liners for Interviews)

* **MariaDB = True Open Source**; MySQL = Oracle controlled.
* **MariaDB = Built-in Galera Cluster**; MySQL = Group Replication (newer, less battle-tested).
* **MariaDB = HTAP (ColumnStore) free**; MySQL = HeatWave (Oracle Cloud only).
* **MariaDB = More storage engines**; MySQL = Mostly InnoDB.
* **MySQL = Better JSON implementation**; MariaDB catching up.
* **MariaDB = Oracle compatibility mode**; MySQL = Oracle ecosystem integration.

---

# 📌 Migration Insight

* **MySQL → MariaDB**: Easy (drop-in until MariaDB 10.6).
* **MariaDB → MySQL**: Harder (missing temporal tables, sequences, PL/SQL mode).
* **Cloud**: MariaDB = **SkySQL (multi-cloud)**, MySQL = **HeatWave (Oracle-only)**.

---

🔥 With this **cheat sheet**, you can **answer interview questions** like:

* “Why should we migrate to MariaDB from MySQL?”
* “Which one is better for HTAP workloads?”
* “How does MariaDB handle HA compared to MySQL?”

---
