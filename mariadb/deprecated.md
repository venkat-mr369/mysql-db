**deprecated and removed features/storage engines** in **MariaDB vs MySQL** 

---

# 📌 1. Deprecated & Removed Storage Engines

### 🔹 **MySQL**

| Engine                  | Status                                  | Details                                                     |
| ----------------------- | --------------------------------------- | ----------------------------------------------------------- |
| **MyISAM**              | Deprecated (8.0), not default since 5.5 | No transactions, not crash-safe. InnoDB replaced it.        |
| **ARCHIVE**             | Deprecated (8.0), removed in MySQL 8.0. | Used for compressed storage of logs, limited functionality. |
| **FEDERATED**           | Deprecated in 5.1, disabled by default. | Connects to remote tables, limited reliability.             |
| **CSV**                 | Deprecated in 8.0.                      | Stores tables as CSV files, very limited.                   |
| **MERGE (MRG\_MyISAM)** | Deprecated, removed in 8.0.             | Used for merging multiple MyISAM tables.                    |
| **NDB Cluster**         | Still supported, but separate product.  | Not deprecated, but only for special workloads (telecom).   |

---

### 🔹 **MariaDB**

| Engine                   | Status                                           | Details                                                          |
| ------------------------ | ------------------------------------------------ | ---------------------------------------------------------------- |
| **XtraDB (InnoDB fork)** | Deprecated since 10.2, removed in 10.5.          | Replaced by InnoDB (Oracle’s).                                   |
| **TokuDB**               | Deprecated in 10.5, removed in 10.6.             | Good for compression & write-heavy, but Percona stopped support. |
| **FederatedX**           | Community engine, deprecated in favor of Spider. | Better sharding support via **Spider** engine.                   |
| **Aria**                 | Still maintained but not default.                | Originally meant to replace MyISAM; limited adoption.            |
| **MyISAM**               | Still available but **not recommended**.         | Only used for legacy apps.                                       |
| **PBXT**                 | Experimental, **removed** in later versions.     | Never matured.                                                   |

---

# 📌 2. Deprecated / Removed Features

### 🔹 **MySQL**

| Feature                                     | Status                             | Details                                |
| ------------------------------------------- | ---------------------------------- | -------------------------------------- |
| **query\_cache**                            | Deprecated in 5.7, removed in 8.0. | Often caused performance bottlenecks.  |
| **password hashing (mysql\_old\_password)** | Removed in 5.7+.                   | Weak authentication.                   |
| **`--skip-locking`** option                 | Deprecated, removed.               | Obsolete due to better InnoDB locking. |
| **`innodb_file_format`**                    | Deprecated in 5.7, removed in 8.0. | Barracuda format became default.       |
| **`TIMESTAMP(N)` fractions**                | Simplified in 8.0.                 | Use `DATETIME` with precision.         |
| **`YEAR(2)` data type**                     | Removed in 5.7.                    | Only YEAR(4) supported now.            |
| **`NO_AUTO_CREATE_USER` SQL mode**          | Removed in 8.0.                    | User creation changed.                 |

---

### 🔹 **MariaDB**

| Feature                                      | Status                                     | Details                                    |
| -------------------------------------------- | ------------------------------------------ | ------------------------------------------ |
| **query\_cache**                             | Deprecated (10.1+), removed (10.6).        | Same reason as MySQL (scalability issues). |
| **mysql\_old\_password**                     | Deprecated, removed.                       | Same as MySQL.                             |
| **`SLAVE` keyword**                          | Deprecated, replaced by `REPLICA` (10.5+). | Aligning with modern terminology.          |
| **XtraDB**                                   | Deprecated in 10.2, removed 10.5.          | Fell back to Oracle’s InnoDB.              |
| **TokuDB**                                   | Deprecated 10.5, removed 10.6.             | Dropped by Percona.                        |
| **FederatedX**                               | Deprecated in favor of Spider engine.      |                                            |
| **HandlerSocket plugin**                     | Deprecated.                                | No longer needed (better JSON and APIs).   |
| **`mysql_secure_installation` old defaults** | Changed in 10.4+.                          | More secure password defaults.             |

---

# 📌 3. Practical DBA Use Cases (Impact of Deprecation)

* **Migrating from MySQL 5.7 → 8.0**:

  * If your app uses **MyISAM or MERGE tables**, they will break.
  * If you relied on **query\_cache**, need to redesign caching (use ProxySQL, Redis).
  * If you use **old authentication plugins**, users won’t connect.

* **Migrating from MariaDB 10.3 → 10.6**:

  * If using **TokuDB**, must migrate to MyRocks or InnoDB.
  * If using **XtraDB**, silently switched to InnoDB (possible behavior differences).
  * If relying on **query\_cache**, performance tuning required.

---

# 📌 4. Migration/Upgrade Strategy

✅ **For MySQL:**

* Replace **MyISAM → InnoDB**.
* Replace **query\_cache → ProxySQL / Redis caching**.
* Migrate **ARCHIVE → ColumnStore or external cold storage**.
* Update **authentication plugins** (use `caching_sha2_password`).

✅ **For MariaDB:**

* Replace **XtraDB → InnoDB** (automatic in 10.5+).
* Replace **TokuDB → MyRocks or InnoDB**.
* Replace **FederatedX → Spider**.
* Remove reliance on **query\_cache**.

---

