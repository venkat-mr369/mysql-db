# MySQL Clusters — The Complete Comparison Guide

> Everything you need to know about Replication, InnoDB Cluster, Galera, Percona XtraDB, NDB Cluster & MariaDB Cluster — explained in simple English with architecture diagrams, examples, and comparisons.

---

## 1. MySQL Replication

**Built-in · Since MySQL 3.23**

MySQL Replication is the **simplest and oldest** way to copy data from one MySQL server to another. Think of it like a **teacher (Master) writing on a whiteboard** and **students (Slaves) copying** everything into their notebooks. The teacher writes, and the students follow — but the students can't write on the whiteboard.

### Architecture Diagram

```
                    ┌─────────────────┐
                    │   MASTER (Source)│
                    │  Read + Write    │
                    └────────┬────────┘
                             │
              Binary Log (binlog) streams changes
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  SLAVE #1    │  │  SLAVE #2    │  │  SLAVE #3    │
    │  Read Only   │  │  Read Only   │  │  Read Only   │
    └──────────────┘  └──────────────┘  └──────────────┘

    How it works:
      1. App writes data → Master
      2. Master records changes in Binary Log
      3. Slaves pull the log & replay the changes
      4. Apps can READ from any Slave
```

### Two Types of Replication

| Type | How it Works | Speed | Safety |
|------|-------------|-------|--------|
| **Asynchronous** | Master does NOT wait for slaves to confirm. Slaves may be a few seconds behind. | ⚡ Fast | ⚠️ Some data loss risk |
| **Semi-Synchronous** | Master waits for **at least 1 slave** to confirm it received the data. | 🔄 Slightly slower | ✅ Safer |

### 🏪 Real-World Example

An e-commerce website: All customer orders go to the **Master**. Product searches and catalog browsing read from **Slaves**. This splits the load — the Master handles writes, and Slaves handle millions of reads.

### Requirements to Install

#### Hardware (Minimum)
- 2 servers (1 master + 1 slave minimum)
- 2 CPU cores, 4 GB RAM per server
- 10 GB+ disk space
- Stable network between servers

#### Software
- MySQL 5.7+ or MySQL 8.0
- Linux (Ubuntu/CentOS recommended)
- Same MySQL version on all servers
- Unique `server-id` for each node

### Quick Setup Commands

```sql
-- On Master (my.cnf)
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log

-- Create replication user on Master
CREATE USER 'repl'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
SHOW MASTER STATUS;

-- On Slave (my.cnf)
[mysqld]
server-id = 2

-- Point Slave to Master
CHANGE MASTER TO MASTER_HOST='master_ip',
  MASTER_USER='repl', MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS=154;
START SLAVE;
```

### Advantages & Disadvantages

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Very easy to set up | No automatic failover (manual intervention) |
| Low overhead on performance | Slave lag (data delay) |
| Built into MySQL (no extra software) | Single point of failure (Master) |
| Great for read-heavy workloads | Slaves are read-only |
| Can chain slaves (Master → Slave → Slave) | No conflict resolution for multi-master |

---

## 2. MySQL InnoDB Cluster

**Official Oracle · Since MySQL 5.7.17**

InnoDB Cluster is Oracle's **official high-availability solution**. Think of it like a **team of pilots in a cockpit** — if one pilot faints, another immediately takes control. There's **no single point of failure**, and failover happens automatically.

### Architecture Diagram

```
                  MySQL InnoDB Cluster Architecture

  ┌──────────────────────────────────────────────────┐
  │              MySQL Router (Proxy)                │
  │     Routes traffic to correct node automatically │
  └────────────────────┬─────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
  ┌────────────┐ ┌────────────┐ ┌────────────┐
  │  PRIMARY   │ │ SECONDARY  │ │ SECONDARY  │
  │ Read+Write │ │ Read Only  │ │ Read Only  │
  └─────┬──────┘ └──────┬─────┘ └──────┬─────┘
        │               │              │
        └───────────────┼──────────────┘
                        │
          Group Replication Protocol
          (Paxos-based consensus)

   All 3 nodes agree before committing data.
   If Primary dies → a Secondary is auto-promoted.

  Three Components:
    1. MySQL Group Replication – syncs data between nodes
    2. MySQL Router – directs traffic automatically
    3. MySQL Shell – admin tool to set up & manage
```

### Key Concepts

| Concept | Explanation |
|---------|------------|
| **How Data Syncs** | Uses **Group Replication** with Paxos consensus — when a write happens, the majority of nodes (e.g., 2 out of 3) must agree before it's committed. This means **no data loss** if one node dies. |
| **Automatic Failover** | If the Primary node crashes, the remaining nodes **vote** and elect a new Primary within seconds. MySQL Router detects this and sends traffic to the new Primary — **your app doesn't need to change anything**. |

### 🏦 Real-World Example

A banking application: You cannot lose a single transaction. InnoDB Cluster ensures every transaction is confirmed by multiple servers before saying "success." If one server dies at 2 AM, the cluster automatically promotes another — zero downtime, zero data loss.

### Requirements to Install

#### Hardware (Minimum)
- **3 servers** (odd number required for voting)
- 4 CPU cores, 8 GB RAM per server
- SSD storage recommended
- Low-latency network (<10ms between nodes)

#### Software
- MySQL 8.0+ (recommended)
- MySQL Shell 8.0+
- MySQL Router 8.0+
- InnoDB storage engine (mandatory)
- Every table must have a Primary Key

### Quick Setup with MySQL Shell

```bash
# Step 1: Connect via MySQL Shell
mysqlsh root@node1

# Step 2: Configure each instance
dba.configureInstance('root@node1')
dba.configureInstance('root@node2')
dba.configureInstance('root@node3')

# Step 3: Create the cluster
var cluster = dba.createCluster('myCluster')

# Step 4: Add nodes
cluster.addInstance('root@node2')
cluster.addInstance('root@node3')

# Step 5: Check status
cluster.status()

# Step 6: Bootstrap Router
mysqlrouter --bootstrap root@node1 --user=mysqlrouter
```

### Advantages & Disadvantages

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Automatic failover (no human needed) | Needs minimum 3 nodes |
| No data loss (synchronous consensus) | Write performance is lower (consensus overhead) |
| Officially supported by Oracle | All tables MUST have primary keys |
| Built-in Router for traffic management | Only works with InnoDB engine |
| Easy setup via MySQL Shell | Requires low-latency network |

---

## 3. Galera Cluster

**Codership · Multi-Master**

Galera Cluster allows **every node to accept writes** — it's like having **3 whiteboards in 3 classrooms**, and anything written on one whiteboard **instantly appears on all others**. This is called **synchronous multi-master replication**.

### Architecture Diagram

```
              Galera Cluster — Multi-Master Architecture

         ┌────────────────┐       ┌────────────────┐
         │    NODE 1      │◄─────►│    NODE 2      │
         │  Read + Write  │       │  Read + Write  │
         └───────┬────────┘       └────────┬───────┘
                 │                          │
                 │    wsrep protocol        │
                 │  (write-set replication) │
                 │                          │
         ┌───────┴──────────────────┴───────┐
         │           NODE 3                 │
         │         Read + Write             │
         └──────────────────────────────────┘

  How a Write Works in Galera:
    1. App sends INSERT to Node 1
    2. Node 1 creates a "write-set" (bundle of changes)
    3. Write-set is broadcast to ALL nodes
    4. All nodes certify (check for conflicts)
    5. If no conflict → COMMIT on all nodes
    6. If conflict → ROLLBACK on the conflicting node
```

### 🌐 Real-World Example

A global content management system: Editors in India, USA, and Europe all need to update articles simultaneously. With Galera, each region has its own node — all writes are accepted locally and synced instantly to all other nodes. No single bottleneck!

### Requirements to Install

#### Hardware (Minimum)
- **3 nodes** minimum (odd number recommended)
- 4 CPU cores, 8 GB RAM per node
- SSD storage (high I/O needed)
- Low-latency network (<5ms ideal)
- Ports: 3306, 4567, 4568, 4444

#### Software
- MySQL 5.7/8.0 + Galera plugin OR MariaDB (Galera built-in) OR Percona XtraDB Cluster
- InnoDB engine only
- All tables MUST have Primary Keys
- `wsrep` provider library

### Advantages & Disadvantages

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| True multi-master (write anywhere) | Write conflicts cause rollbacks |
| Synchronous — no data lag | Slower writes (certification overhead) |
| Automatic node provisioning (SST/IST) | Sensitive to network latency |
| No single point of failure | Large transactions can block the cluster |
| Consistent reads from any node | More complex to tune and debug |

---

## 4. Percona XtraDB Cluster (PXC)

**Percona · Galera-Based**

PXC is basically **Galera Cluster with extra features**. Think of it like buying a car: Galera is the engine, and Percona wraps it in a **better body with added safety features** — like encryption, better monitoring, and enterprise-grade tools.

### Architecture Diagram

```
     Percona XtraDB Cluster = Percona Server + Galera Library

         ┌──────────────────┐     ┌──────────────────┐
         │  PXC Node 1      │◄───►│  PXC Node 2      │
         │  Percona Server  │     │  Percona Server  │
         │  + Galera Plugin │     │  + Galera Plugin │
         └────────┬─────────┘     └─────────┬────────┘
                  │                           │
                  └─────────┬─────────────────┘
                            │
                  ┌─────────┴────────┐
                  │  PXC Node 3      │
                  │  Percona Server  │
                  │  + Galera Plugin │
                  └──────────────────┘

  Extra features Percona adds on top of Galera:
    ✦ Percona XtraBackup — hot backups without locking
    ✦ Encryption — SSL for data in transit + at rest
    ✦ ProxySQL integration — smart query routing
    ✦ PMM (Percona Monitoring & Management) — dashboards
    ✦ Strict Mode — prevents unsafe operations
```

### 🏥 Real-World Example

A hospital records system: Patient data must be encrypted, always available, and consistent across all locations. PXC provides multi-master sync (Galera), built-in encryption, and Percona's monitoring tools to ensure everything runs smoothly 24/7.

### Requirements to Install

#### Hardware (Minimum)
- **3 nodes** minimum
- 4 CPU cores, 8 GB RAM per node
- SSD storage strongly recommended
- Low-latency network
- Same ports as Galera: 3306, 4567, 4568, 4444

#### Software
- Percona XtraDB Cluster 8.0
- Linux (Ubuntu 20.04+ / CentOS 7+)
- InnoDB engine only
- Primary keys on all tables
- Optional: ProxySQL, Percona PMM

### Quick Setup Commands

```bash
# Install on Ubuntu
sudo apt install percona-xtradb-cluster-80

# Bootstrap first node
sudo systemctl start mysql@bootstrap

# On Node 2 & 3, set cluster address in my.cnf
[mysqld]
wsrep_cluster_address = gcomm://node1_ip,node2_ip,node3_ip
wsrep_node_address    = this_node_ip
wsrep_sst_method      = xtrabackup-v2

# Start remaining nodes
sudo systemctl start mysql
```

### Advantages & Disadvantages

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| All Galera benefits + extras | Same Galera limitations (write conflicts) |
| Built-in encryption (transit + rest) | Not Oracle-supported (community) |
| Free & open source (enterprise-grade) | Slightly different from stock MySQL |
| Percona XtraBackup for hot backups | Requires Percona repositories |
| Excellent monitoring with PMM | |

---

## 5. MySQL NDB Cluster

**Oracle · In-Memory · Telecom-Grade**

NDB (Network DataBase) Cluster is designed for **extreme real-time performance**. It stores data **in memory (RAM)** distributed across multiple "data nodes." Think of it as a **Formula 1 car** — extremely fast but complex to maintain and expensive to run.

### Architecture Diagram

```
              MySQL NDB Cluster Architecture

┌──────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                      │
│         App connects via MySQL Server (SQL Node)         │
└─────────────┬────────────────────────┬───────────────────┘
              │                        │
       ┌──────┴──────┐          ┌──────┴──────┐
       │  SQL Node 1 │          │  SQL Node 2 │
       │  (mysqld)   │          │  (mysqld)   │
       └──────┬──────┘          └──────┬──────┘
              │                        │
   ───────────┴────────────────────────┴──────────────
                NDB API (Internal Protocol)
   ────────────┬───────────┬───────────┬──────────────
               │           │           │
       ┌───────┴───┐  ┌────┴──────┐  ┌───┴───────┐
       │ Data Node │  │ Data Node │  │ Data Node │
       │  (ndbd)   │  │  (ndbd)   │  │  (ndbd)   │
       │  RAM ⚡  │   │  RAM ⚡  │  │  RAM ⚡   │
       └───────────┘  └───────────┘  └───────────┘

       ┌───────────┐
       │ Mgmt Node │  ← Controls config (the brain)
       │ (ndb_mgmd) │
       └───────────┘

  Three Types of Nodes:
    1. SQL Nodes     — MySQL servers (user-facing)
    2. Data Nodes    — Store data in RAM (the muscle)
    3. Management Node — Controls config (the brain)
```

### 📱 Real-World Example

Telecom companies like Ericsson use NDB Cluster to handle **millions of phone calls per second**. When you make a call, the routing data needs to be fetched in **microseconds** — NDB stores this in RAM with zero downtime guarantee.

### Requirements to Install

#### Hardware (Minimum)
- **4+ servers** (1 mgmt + 2 data + 1 SQL minimum)
- Data nodes: 8+ CPU cores, **32+ GB RAM**
- SQL nodes: 4 cores, 8 GB RAM
- Ultra-low latency network (<1ms)
- Dedicated network recommended

#### Software
- MySQL NDB Cluster 8.0 (separate download)
- Linux only (no Windows support for production)
- **NDB storage engine** (NOT InnoDB)
- config.ini for management node
- All data must fit in RAM (or use disk tables)

### Advantages & Disadvantages

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| 99.999% uptime (designed for telecom) | Very complex to set up and manage |
| In-memory = blazing fast reads | Expensive (needs lots of RAM) |
| Auto-sharding (data distributed automatically) | Not all SQL features supported |
| True horizontal scaling | JOINs across nodes are slow |
| Can handle millions of operations/sec | Different storage engine (NDB, not InnoDB) |

---

## 6. MariaDB Galera Cluster

**MariaDB Foundation · Galera Built-In**

MariaDB is a **fork of MySQL** (created by the original MySQL founder). MariaDB comes with **Galera Cluster built right in** — no need to install extra plugins! It's like getting a car with **GPS navigation included for free**, whereas MySQL Galera is like buying the GPS separately.

### Architecture Diagram

```
         MariaDB Galera Cluster = MariaDB + Galera (built-in)

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  MariaDB #1  │  │  MariaDB #2  │  │  MariaDB #3  │
  │  Read+Write  │  │  Read+Write  │  │  Read+Write  │
  │  Galera ✓    │  │  Galera ✓    │  │  Galera ✓   │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
              Synchronous Replication (wsrep)
              Same as Galera but pre-integrated

  Unique MariaDB additions:
    ✦ Galera is included — just enable in config
    ✦ MaxScale — MariaDB's own proxy/router
    ✦ MariaDB Backup — mariabackup for SST
    ✦ Extra engines — Aria, ColumnStore, Spider
    ✦ Better optimizer — often faster queries
```

### 📰 Real-World Example

Wikipedia runs on MariaDB. They need a database that's free, reliable, and handles massive read traffic across multiple data centers. MariaDB's Galera integration makes multi-datacenter sync straightforward.

### Requirements to Install

#### Hardware (Minimum)
- **3 nodes** minimum
- 4 CPU cores, 8 GB RAM per node
- Same as Galera requirements
- Ports: 3306, 4567, 4568, 4444

#### Software
- MariaDB 10.4+ (Galera 4 included)
- Linux (Ubuntu/CentOS/Debian)
- No extra Galera download needed
- Optional: MaxScale for routing

### Advantages & Disadvantages

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Galera comes pre-installed | Diverging from MySQL compatibility |
| Truly free & open source | Some MySQL 8.0 features missing |
| MySQL compatible (drop-in replacement) | Enterprise support costs money |
| Extra features over stock MySQL | Same Galera write-conflict limitations |
| Active community development | |

---

## Side-by-Side Comparison Table

| Feature | MySQL Replication | InnoDB Cluster | Galera Cluster | Percona XtraDB | NDB Cluster | MariaDB Galera |
|---------|-------------------|----------------|----------------|----------------|-------------|----------------|
| **Replication Type** | Async / Semi-Sync | Virtually Sync (Paxos) | Synchronous (wsrep) | Synchronous (wsrep) | Synchronous (2-phase) | Synchronous (wsrep) |
| **Multi-Master Writes** | ❌ No | ⚠️ Optional | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Automatic Failover** | ❌ No (manual) | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Data Consistency** | ⚠️ Eventual | ✅ Strong | ✅ Strong | ✅ Strong | ✅ Strong | ✅ Strong |
| **Min. Nodes Required** | 2 | 3 | 3 | 3 | 4 (different types) | 3 |
| **Storage Engine** | Any | InnoDB only | InnoDB only | InnoDB (XtraDB) | NDB only | InnoDB only |
| **Data in Memory?** | Disk-based | Disk-based | Disk-based | Disk-based | ✅ In-Memory (RAM) | Disk-based |
| **Auto-Sharding** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Write Performance** | ⚡ Fast (async) | 🔄 Medium | 🔄 Medium | 🔄 Medium | ⚡ Very Fast (RAM) | 🔄 Medium |
| **Read Scaling** | ✅ Excellent | ✅ Good | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Complexity** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Medium-Hard | ⭐⭐⭐ Medium-Hard | ⭐⭐⭐⭐⭐ Very Hard | ⭐⭐ Medium |
| **RAM Requirement** | 4 GB+ | 8 GB+ | 8 GB+ | 8 GB+ | 32 GB+ | 8 GB+ |
| **Cost** | Free | Free / Paid Enterprise | Free | Free | Free / Paid CGE | Free |
| **Primary Key Required?** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Proxy / Router** | ProxySQL / HAProxy | MySQL Router | ProxySQL / HAProxy | ProxySQL | Built-in | MaxScale / ProxySQL |
| **Vendor** | Oracle | Oracle | Codership | Percona | Oracle | MariaDB Foundation |
| **Best For** | Read scaling, backups | HA with Oracle support | Multi-master writes | Galera + enterprise tools | Telecom, real-time apps | Open-source multi-master |

---

## Which Cluster Should You Choose?

| Question | Answer |
|----------|--------|
| **Q1:** Do you just need to scale reads (more people reading data)? | → **MySQL Replication** |
| **Q2:** Need automatic failover with Oracle support? | → **InnoDB Cluster** |
| **Q3:** Need to write to any node (multi-master)? | → **Galera Cluster** |
| **Q4:** Want Galera + encryption + monitoring tools? | → **Percona XtraDB** |
| **Q5:** Need extreme speed (microseconds) & 99.999% uptime? | → **NDB Cluster** |
| **Q6:** Want fully open-source with Galera built-in? | → **MariaDB Galera** |

---

## Quick Summary: How Each One Works

### MySQL Replication
> Master copies data to Slaves

1. App writes to **Master**
2. Master logs changes in **Binary Log**
3. Slaves **pull & replay** changes
4. Apps read from **Slaves**

### InnoDB Cluster
> Consensus-based with auto-failover

1. App connects via **MySQL Router**
2. Router sends writes to **Primary**
3. Primary gets **majority agreement**
4. If Primary dies → **auto election**

### Galera / PXC / MariaDB
> Write anywhere, sync everywhere

1. App writes to **any node**
2. Node creates **write-set**
3. All nodes **certify** (check conflicts)
4. **Commit** on all or **rollback**

### NDB Cluster
> In-memory distributed database

1. App connects to **SQL Node**
2. SQL Node talks to **Data Nodes**
3. Data stored in **RAM (partitioned)**
4. **Mgmt Node** monitors everything

---

*MySQL Clusters Comparison Guide · Created for learning purposes*
