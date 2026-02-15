# MariaDB MaxScale — Complete In-Depth Guide

> What MaxScale is, how it works internally, all its features explained in simple English, and step-by-step implementation on Amazon Linux, CentOS & Ubuntu.

**MaxScale = Advanced Database Proxy · Load Balancer · Firewall · Failover Manager**

---

## What Exactly is MaxScale?

### MaxScale = Smart Middleman Between Your App and Database

Imagine you have a restaurant (your application) and multiple kitchens (your database servers). Instead of having your waiters (app connections) figure out which kitchen to go to, you hire a **smart manager (MaxScale)** who sits between the waiters and kitchens.

This manager **automatically decides**: "This order is just a question about the menu? Send it to any kitchen (READ). This order needs to cook food? Send it to the head kitchen (WRITE)." If the head kitchen catches fire (server crash), the manager **instantly promotes another kitchen** to be the head — and the waiters don't even notice anything changed!

**In technical terms:** MaxScale is a database proxy developed by MariaDB Corporation that sits between your application and your MariaDB/MySQL database servers. It understands SQL, can route queries intelligently, provides automatic failover, acts as a database firewall, and offers load balancing — all **transparently** (your app thinks it's talking to a single database).

### How MaxScale Fits In Your Architecture

```
                    YOUR APPLICATION
            (PHP, Python, Java, Node.js, etc.)
                         │
              Connects to port 3306
             (thinks it's one database)
                         │
  ┌──────────────────────▼────────────────────────────────────┐
  │                   MAXSCALE PROXY                          │
  │                                                           │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
  │  │ Protocol │  │  Router  │  │  Filter  │  │ Monitor  │  │
  │  │ Module   │  │  Module  │  │  Module  │  │ Module   │  │
  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
  │                                                           │
  │  Understands SQL │ Routes queries │ Filters  │ Monitors   │
  │  protocol        │ to right server│ traffic  │ server     │
  │                  │                │          │ health     │
  └───────┬──────────┴──────┬─────────┴──────┬───┴────────────┘
          │                 │                │
    SELECT goes to    INSERT/UPDATE to    Monitors all
    any replica       primary only        servers
          │                 │                │
          ▼                 ▼                ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │   PRIMARY    │  │  REPLICA #1  │  │  REPLICA #2  │
  │  Read+Write  │  │  Read Only   │  │  Read Only   │
  │  (Master)    │  │  (Slave)     │  │  (Slave)     │
  └──────────────┘  └──────────────┘  └──────────────┘
```

---

## MaxScale Internal Architecture

### The 4 Building Blocks (Plugin Modules)

```
  Client App
      │
      ▼
┌───────────────┐
│ 1. PROTOCOL    │  ← Speaks MariaDB/MySQL protocol to your app
│   Module       │     (MariaDBClient for frontend, MariaDBBackend for backend)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ 2. FILTER      │  ← Inspects/modifies queries passing through
│   Module(s)    │     (Firewall, Cache, Logging, Regex, Throttle)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ 3. ROUTER      │  ← Decides WHERE to send the query
│   Module       │     (ReadWriteSplit, ReadConnRoute, SchemaRouter)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ 4. MONITOR     │  ← Checks server health & triggers failover
│   Module       │     (MariaDBMon, GaleraMon, CsMonitor)
└───────────────┘

  Data flows: App → Protocol → Filter(s) → Router → Backend Servers
```

### 🔌 1. Protocol Module

**What it does:** Handles the communication language between your app and MaxScale, and between MaxScale and the backend databases. It speaks the MariaDB/MySQL wire protocol, so your app thinks it's talking directly to a database.

### 🔀 2. Router Module

**What it does:** The brain! It reads each SQL query and decides which backend server should execute it. A SELECT goes to a replica, an INSERT goes to the primary. This is where the "smart routing" magic happens.

### 🔍 3. Filter Module

**What it does:** Sits in the query pipeline and can inspect, modify, log, cache, or block queries. Think of it as security checkpoints at an airport — every query passes through before reaching the router.

### 💓 4. Monitor Module

**What it does:** Continuously pings all backend servers to check their health. If the primary dies, the monitor triggers automatic failover — promotes a replica and reconfigures replication. All without your app knowing.

---

## Router Types Explained

### 1. ReadWriteSplit Router (Most Popular)

This is the **most commonly used router**. It analyzes each SQL statement and routes it based on whether it's a read or write operation.

```
                   ReadWriteSplit Router Flow

     App sends: SELECT * FROM users WHERE id=5;
                                │
                    MaxScale parses the SQL
                    Detects: It's a SELECT (READ)
                                │
                     Routes to → Any Replica (load balanced)
     
     ─────────────────────────────────────────
     
     App sends: INSERT INTO orders VALUES (...);
                                │
                    MaxScale parses the SQL
                    Detects: It's an INSERT (WRITE)
                                │
                     Routes to → Primary Server Only
     
     ─────────────────────────────────────────
     
     App sends: BEGIN; SELECT ...; UPDATE ...; COMMIT;
                                │
                    MaxScale detects: TRANSACTION
                                │
                     Routes entire transaction → Primary
                     (to maintain ACID consistency)
```

> **🛒 Example Use Case:** Your e-commerce app does 90% reads (browsing products, checking prices) and 10% writes (placing orders). ReadWriteSplit sends the 90% reads across 3 replicas, reducing primary load by 90%. Your site gets 3x faster reads!

### 2. ReadConnRoute Router (Connection-Based)

Unlike ReadWriteSplit which routes per-query, ReadConnRoute routes the **entire connection** to one server. Once a client connects, ALL their queries go to that one server.

| When to Use | Options |
|---|---|
| Simple load balancing across servers | `router_options=master` → all to primary |
| When you don't need per-query routing | `router_options=slave` → all to replicas |
| Galera Cluster (all nodes are equal) | `router_options=synced` → Galera synced nodes |
| Lower overhead than ReadWriteSplit | `router_options=running` → any running server |

### 3. SchemaRouter (Database/Schema-Based)

Routes queries based on **which database/schema** they target. Perfect for sharding — different databases live on different servers.

```
   SchemaRouter Example:

     Server A has: users_db, auth_db
     Server B has: orders_db, inventory_db
     Server C has: analytics_db, logs_db

     App: USE users_db; SELECT * FROM users;   →  Routes to Server A
     App: USE orders_db; INSERT INTO orders;   →  Routes to Server B
     App: USE analytics_db; SELECT ...;        →  Routes to Server C
```

---

## Complete Feature Breakdown

### 🔄 Automatic Failover

This is MaxScale's **killer feature**. When the primary (master) database crashes, MaxScale automatically handles everything:

```
  STEP 1: Normal Operation
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ PRIMARY  │───►│ REPLICA1 │    │ REPLICA2 │
  │ (Master) │───►│ (Slave)  │    │ (Slave)  │
  └──────────┘    └──────────┘    └──────────┘
       ▲
    MaxScale Monitor pings every 2 seconds
    
  STEP 2: Primary Crashes! 💥
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ PRIMARY  │    │ REPLICA1 │    │ REPLICA2 │
  │  💀 DEAD │    │ (Slave)  │    │ (Slave)  │
  └──────────┘    └──────────┘    └──────────┘
       ▲
    Monitor detects: "Primary is DOWN!"
    
  STEP 3: Automatic Promotion (within seconds)
                   ┌──────────┐    ┌──────────┐
                   │ REPLICA1 │    │ REPLICA2 │
                   │ NEW      │◄───│ (Slave)  │
                   │ PRIMARY  │    │ Re-pointed│
                   │(Promoted)│    │          │
                   └──────────┘    └──────────┘
                        ▲
    MaxScale:
    ✦ Picks the most up-to-date replica
    ✦ Promotes it to Primary (STOP SLAVE; RESET SLAVE ALL;)
    ✦ Points other replicas to the new Primary
    ✦ Updates routing — app traffic goes to new Primary
    ✦ App doesn't know anything changed!

  STEP 4: Old Primary Comes Back
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ OLD      │───►│ REPLICA1 │    │ REPLICA2 │
  │ NOW SLAVE│    │ PRIMARY  │◄───│ (Slave)  │
  │(Rejoined)│    │          │    │          │
  └──────────┘    └──────────┘    └──────────┘
    MaxScale auto-rejoins it as a replica!
```

> **🔑 Key Configuration:** `auto_failover=true` enables this. `auto_rejoin=true` automatically brings back a recovered server as a replica. The `failcount` parameter sets how many failed health checks before triggering failover (default: 5 checks × 2 sec interval = 10 seconds).

---

### 🔁 Transaction Replay

If a server fails **during an active transaction**, MaxScale can automatically **replay that transaction** on another server instead of returning an error to the app.

```
  Without Transaction Replay:
    App: BEGIN → INSERT → UPDATE → SERVER CRASH → ❌ Error to App!
    
  With Transaction Replay (transaction_replay=true):
    App: BEGIN → INSERT → UPDATE → SERVER CRASH
    MaxScale: "I recorded this transaction, let me replay it..."
    MaxScale: BEGIN → INSERT → UPDATE → COMMIT on new server → ✅ Success to App!
```

---

### 🛡️ Database Firewall (DbFwFilter)

MaxScale can **block dangerous queries** before they reach your database. It's like a security guard checking every query.

**What You Can Block:**
- `DROP DATABASE` commands
- `DELETE` without WHERE clause
- Queries from specific IPs
- Queries at certain times (e.g., no writes at night)
- Queries returning too many rows
- SQL injection patterns (regex matching)

**Example Rule:**
```
# Block DROP commands
rule block_drops match regex 'DROP\s+TABLE|DROP\s+DATABASE'

# Block DELETE without WHERE
rule no_wild_delete match regex 'DELETE\s+FROM\s+\w+\s*$'

# Apply rules to all users
users %@% match any rules block_drops no_wild_delete
```

---

### ⚡ Query Result Cache

MaxScale can **cache SELECT results in memory**. If the same query comes again within a set time, MaxScale returns the cached result **without even touching the database**.

```
  First request:
    App → SELECT * FROM products → MaxScale → Database
                                                ↓
                                       MaxScale caches result
                                                ↓
                                       Returns to App

  Next identical request (within TTL):
    App → SELECT * FROM products → MaxScale
                                      ↓
                              Returns cached result instantly!
                              (Database is never touched)
```

---

### 🔗 Connection Pooling & Multiplexing

Without MaxScale, if 1000 users connect to your app, that means 1000 connections to your database (expensive!). MaxScale **shares and reuses** backend connections.

```
  Without MaxScale:
    1000 App Users → 1000 DB Connections → Database overwhelmed! 😱

  With MaxScale Connection Pooling:
    1000 App Users → MaxScale → ~50 shared DB Connections → Database happy! 😊
    
    MaxScale reuses idle connections for new requests
```

---

### Other Key Features

| Feature | Description |
|---------|-------------|
| **📊 MaxGUI (Web Interface)** | A visual dashboard at port 8989 to monitor servers, services, sessions, and perform admin tasks with clicks instead of commands. |
| **🔐 TLS/SSL Encryption** | Encrypts all traffic between app → MaxScale and MaxScale → databases. Protects data in transit. |
| **📝 Query Logging (QLA Filter)** | Logs every SQL query passing through MaxScale. Create audit trails for compliance, debug slow queries. |
| **🌊 Kafka Integration** | KafkaCDC router streams database changes to Apache Kafka for real-time analytics or event-driven architecture. |
| **🚦 Query Throttling** | Limits how many queries a single session can execute per second. Prevents DDoS attacks from overwhelming your database. |
| **🔄 Causal Reads** | After a write, ensures the next read returns updated data — even if routed to a replica. Uses GTID tracking. |

---

## MaxScale vs Other Proxies

| Feature | MaxScale | ProxySQL | HAProxy | MySQL Router |
|---------|----------|----------|---------|--------------|
| **SQL Aware?** | ✅ Yes (parses SQL) | ✅ Yes (parses SQL) | ❌ No (TCP level) | ⚠️ Partial |
| **Read/Write Split** | ✅ Built-in | ✅ Built-in (rules) | ❌ No | ✅ With Group Repl. |
| **Auto Failover** | ✅ Built-in | ❌ Needs external tool | ❌ No | ✅ With InnoDB Cluster |
| **Transaction Replay** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Database Firewall** | ✅ Built-in | ✅ Query rules | ❌ No | ❌ No |
| **Query Cache** | ✅ Built-in | ✅ Built-in | ❌ No | ❌ No |
| **Kafka Streaming** | ✅ KafkaCDC Router | ❌ No | ❌ No | ❌ No |
| **Web GUI** | ✅ MaxGUI | ✅ Admin interface | ✅ Stats page | ❌ No |
| **Best With** | MariaDB | MySQL / Percona | Any (TCP proxy) | MySQL InnoDB Cluster |
| **License** | BSL → GPL (v21.06) | GPL | GPL | GPL |

---

## Requirements Before You Start

### 🖥️ MaxScale Server
- **Separate server** (recommended — don't install on DB server)
- 2+ CPU cores (4 recommended)
- 4 GB+ RAM (8 GB for caching)
- Linux OS (Ubuntu 20.04+, CentOS 7+, Amazon Linux 2+)
- Open ports: 3306 (service), 8989 (MaxGUI), 27017 (REST API)

### 🗄️ Backend Database Servers
- MariaDB 10.4+ or MySQL 5.7+ (at least 2 servers)
- Replication already set up (Master-Slave or Galera)
- A dedicated MaxScale user with proper privileges
- Network connectivity between MaxScale and all DB servers

### 📋 Database Architecture Example
- **Server 1 (MaxScale):** 192.168.1.10
- **Server 2 (Primary/Master):** 192.168.1.20
- **Server 3 (Replica/Slave 1):** 192.168.1.30
- **Server 4 (Replica/Slave 2):** 192.168.1.40

### 👤 Required DB User Privileges
- SELECT on mysql.user, mysql.db, mysql.tables_priv
- SELECT on mysql.roles_mapping
- SHOW DATABASES ON \*.\*
- REPLICATION CLIENT ON \*.\*
- SUPER ON \*.\* (for failover)
- REPLICATION SLAVE ADMIN (MariaDB 10.5+)

---

## Step-by-Step Implementation

### Step 1: Create MaxScale User on Your Database (All OS — Run on Primary DB)

Before installing MaxScale, create a user on your PRIMARY database server that MaxScale will use to connect, monitor, and manage failover.

```sql
-- Connect to your PRIMARY MariaDB/MySQL server
mysql -u root -p

-- Create the MaxScale monitoring & routing user
CREATE USER 'maxscale_user'@'192.168.1.10' IDENTIFIED BY 'SecurePass123!';

-- Grant monitoring permissions
GRANT SELECT ON mysql.user TO 'maxscale_user'@'192.168.1.10';
GRANT SELECT ON mysql.db TO 'maxscale_user'@'192.168.1.10';
GRANT SELECT ON mysql.tables_priv TO 'maxscale_user'@'192.168.1.10';
GRANT SELECT ON mysql.roles_mapping TO 'maxscale_user'@'192.168.1.10';
GRANT SHOW DATABASES ON *.* TO 'maxscale_user'@'192.168.1.10';

-- Grant replication monitoring
GRANT REPLICATION CLIENT ON *.* TO 'maxscale_user'@'192.168.1.10';

-- Grant failover permissions (IMPORTANT for auto-failover)
GRANT SUPER ON *.* TO 'maxscale_user'@'192.168.1.10';
GRANT RELOAD ON *.* TO 'maxscale_user'@'192.168.1.10';

-- For MariaDB 10.5+ also grant:
GRANT REPLICATION SLAVE ADMIN ON *.* TO 'maxscale_user'@'192.168.1.10';
GRANT REPLICA MONITOR ON *.* TO 'maxscale_user'@'192.168.1.10';

FLUSH PRIVILEGES;
```

> **⚠️ Replace the IP:** Replace `192.168.1.10` with your MaxScale server's actual IP. Or use `'%'` to allow from any IP (less secure). For Galera Cluster, this user will replicate to all nodes automatically.

---

### Step 2: Install MaxScale (OS-Specific)

---

#### 🟠 Amazon Linux 2 / Amazon Linux 2023

**1. Update the system**
```bash
sudo yum update -y
```

**2. Add MariaDB Repository**
```bash
# Download and run the MariaDB repo setup script
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash

# For Amazon Linux 2 (uses RHEL 7 repos):
# The script auto-detects, but if it fails:
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup \
  | sudo bash -s -- --os-type=rhel --os-version=7

# For Amazon Linux 2023 (uses RHEL 9 repos):
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup \
  | sudo bash -s -- --os-type=rhel --os-version=9
```

**3. Install MaxScale**
```bash
# Amazon Linux 2
sudo yum install maxscale -y

# Amazon Linux 2023 (uses dnf)
sudo dnf install maxscale -y
```

**4. Verify Installation**
```bash
maxscale --version
# Output: MaxScale 24.02.x or similar
```

**5. Open Firewall Ports (Security Group on AWS)**
```bash
# In AWS Console → EC2 → Security Groups → Inbound Rules:
# Port 3306 (MySQL/MaxScale service) — from app servers
# Port 3307 (Read-Only service, if configured) — from app servers
# Port 8989 (MaxGUI web interface) — from your IP only

# If using iptables locally:
sudo iptables -I INPUT -p tcp --dport 3306 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 8989 -j ACCEPT
```

> **📌 Amazon Linux Note:** Amazon Linux 2 is based on RHEL 7, and Amazon Linux 2023 is based on RHEL 9 / Fedora. The MariaDB repo setup script may not always auto-detect correctly, so use the `--os-type` and `--os-version` flags to force the correct repos.

---

#### 🟣 CentOS 7 / CentOS Stream 8 / CentOS Stream 9

**1. Update the system**
```bash
sudo yum update -y   # CentOS 7
sudo dnf update -y   # CentOS 8/9
```

**2. Add MariaDB Repository**
```bash
# Method 1: Auto-setup script (Recommended)
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash

# Method 2: Manual repo file for CentOS 7
sudo tee /etc/yum.repos.d/mariadb-maxscale.repo <<EOF
[mariadb-maxscale]
name=MariaDB MaxScale
baseurl=https://dlm.mariadb.com/repo/maxscale/latest/yum/centos/7/x86_64
gpgkey=https://supplychain.mariadb.com/MariaDB-Server-GPG-KEY
gpgcheck=1
enabled=1
EOF
```

**3. Install MaxScale**
```bash
# CentOS 7
sudo yum install maxscale -y

# CentOS 8/9
sudo dnf install maxscale -y
```

**4. Open Firewall**
```bash
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --permanent --add-port=3307/tcp
sudo firewall-cmd --permanent --add-port=8989/tcp
sudo firewall-cmd --reload

# Verify
sudo firewall-cmd --list-ports
```

**5. Verify Installation**
```bash
maxscale --version
rpm -qi maxscale
```

---

#### 🟡 Ubuntu 20.04 (Focal) / 22.04 (Jammy) / 24.04 (Noble)

**1. Update the system**
```bash
sudo apt update && sudo apt upgrade -y
```

**2. Add MariaDB Repository**
```bash
# Method 1: Auto-setup script (Recommended)
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash

# Method 2: Manual (Ubuntu 22.04 example)
sudo apt install apt-transport-https curl -y

# Import MariaDB GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://supplychain.mariadb.com/MariaDB-Server-GPG-KEY \
  | sudo gpg --dearmor -o /etc/apt/keyrings/mariadb-keyring.gpg

# Add repository
echo "deb [signed-by=/etc/apt/keyrings/mariadb-keyring.gpg] \
  https://dlm.mariadb.com/repo/maxscale/latest/apt \
  jammy main" | sudo tee /etc/apt/sources.list.d/maxscale.list

sudo apt update
```

**3. Install MaxScale**
```bash
sudo apt install maxscale -y
```

**4. Open Firewall (UFW)**
```bash
sudo ufw allow 3306/tcp
sudo ufw allow 3307/tcp
sudo ufw allow 8989/tcp
sudo ufw reload
sudo ufw status
```

**5. Verify Installation**
```bash
maxscale --version
dpkg -l | grep maxscale
```

---

### Step 3: Configure MaxScale (Same for All OS)

The main configuration file is `/etc/maxscale.cnf`. Below is a **complete production-ready configuration** with Read/Write Splitting and Automatic Failover:

```ini
# ═══════════════════════════════════════════════════════
# /etc/maxscale.cnf — Complete MaxScale Configuration
# ═══════════════════════════════════════════════════════

# ─── GLOBAL SETTINGS ───
[maxscale]
threads         = auto           # Auto-detect CPU cores
log_augmentation = 1              # Add function names to logs
ms_timestamp     = 1              # Millisecond timestamps in logs
syslog           = 1              # Send logs to syslog
admin_host       = 0.0.0.0        # MaxGUI listens on all IPs
admin_port       = 8989            # MaxGUI port
admin_secure_gui = false          # Set true for HTTPS in production

# ─── DEFINE BACKEND SERVERS ───
[primary-server]
type     = server
address  = 192.168.1.20           # ← Your Primary/Master IP
port     = 3306
protocol = MariaDBBackend

[replica-1]
type     = server
address  = 192.168.1.30           # ← Your Replica/Slave 1 IP
port     = 3306
protocol = MariaDBBackend

[replica-2]
type     = server
address  = 192.168.1.40           # ← Your Replica/Slave 2 IP
port     = 3306
protocol = MariaDBBackend

# ─── MONITOR (Health Checker + Failover Engine) ───
[MariaDB-Monitor]
type                 = monitor
module               = mariadbmon
servers              = primary-server, replica-1, replica-2
user                 = maxscale_user
password             = SecurePass123!
monitor_interval     = 2000ms         # Check every 2 seconds
auto_failover        = true           # ✅ Enable automatic failover
auto_rejoin          = true           # ✅ Auto-rejoin recovered servers
failcount            = 5              # Fail 5 checks before failover
replication_user     = repl_user      # User for replication changes
replication_password = ReplPass123!

# ─── READ-WRITE SPLIT SERVICE ───
[Read-Write-Service]
type                  = service
router                = readwritesplit
servers               = primary-server, replica-1, replica-2
user                  = maxscale_user
password              = SecurePass123!
master_accept_reads   = true          # Primary also handles reads if needed
transaction_replay    = true          # ✅ Replay failed transactions
transaction_replay_max_size = 1Mi     # Max transaction size to replay
causal_reads          = true          # ✅ Read-your-own-writes consistency
causal_reads_timeout  = 10s

# ─── READ-ONLY SERVICE (Optional — separate port for reads) ───
[Read-Only-Service]
type            = service
router          = readconnroute
servers         = replica-1, replica-2
user            = maxscale_user
password        = SecurePass123!
router_options  = slave             # Only route to slaves

# ─── LISTENERS (Where apps connect) ───
[Read-Write-Listener]
type     = listener
service  = Read-Write-Service
protocol = MariaDBClient
port     = 3306                    # Apps connect here (main port)

[Read-Only-Listener]
type     = listener
service  = Read-Only-Service
protocol = MariaDBClient
port     = 3307                    # Optional read-only port
```

### 🔐 Encrypt Passwords!

In production, never store passwords in plain text. Use MaxScale's encryption:

```bash
# Generate encryption keys
sudo maxkeys /var/lib/maxscale/
sudo chown maxscale:maxscale /var/lib/maxscale/.secrets

# Encrypt your password
maxpasswd /var/lib/maxscale/ SecurePass123!
# Output: 96F99AA1315BDC3604B006F427DD9484

# Use the encrypted string in maxscale.cnf:
# password = 96F99AA1315BDC3604B006F427DD9484
```

---

### Step 4: Start & Enable MaxScale (All OS)

```bash
# Start MaxScale
sudo systemctl start maxscale

# Enable on boot
sudo systemctl enable maxscale

# Check status
sudo systemctl status maxscale

# View logs (troubleshooting)
sudo journalctl -u maxscale -f
# Or: sudo tail -f /var/log/maxscale/maxscale.log
```

---

### Step 5: Verify Everything is Working

```bash
# ─── Check server status with maxctrl ───
sudo maxctrl list servers
# Expected output:
# ┌────────────────┬───────────────┬──────┬─────────────────┬───────────────────┐
# │ Server         │ Address       │ Port │ Connections     │ State             │
# ├────────────────┼───────────────┼──────┼─────────────────┼───────────────────┤
# │ primary-server │ 192.168.1.20  │ 3306 │ 0               │ Master, Running   │
# │ replica-1      │ 192.168.1.30  │ 3306 │ 0               │ Slave, Running    │
# │ replica-2      │ 192.168.1.40  │ 3306 │ 0               │ Slave, Running    │
# └────────────────┴───────────────┴──────┴─────────────────┴───────────────────┘

# ─── Check services ───
sudo maxctrl list services

# ─── Check monitors ───
sudo maxctrl list monitors

# ─── Check listeners ───
sudo maxctrl list listeners Read-Write-Service

# ─── Test connection through MaxScale ───
mysql -h 192.168.1.10 -P 3306 -u your_app_user -p
# You should connect and see MaxScale routing queries!

# ─── Open MaxGUI in browser ───
# Visit: http://192.168.1.10:8989
# Default login: admin / mariadb
```

---

### Step 6: Essential MaxCtrl Commands (Cheat Sheet)

```bash
# ═══ MONITORING COMMANDS ═══
sudo maxctrl list servers                         # See all server states
sudo maxctrl list services                        # See all services
sudo maxctrl list sessions                        # See active client connections
sudo maxctrl list filters                         # See active filters
sudo maxctrl show server primary-server           # Detailed server info

# ═══ MAINTENANCE COMMANDS ═══
sudo maxctrl set server replica-1 maintenance     # Put in maintenance mode
sudo maxctrl clear server replica-1 maintenance   # Remove from maintenance

# ═══ MANUAL FAILOVER (if auto is off) ═══
sudo maxctrl call command mariadbmon failover MariaDB-Monitor

# ═══ MANUAL SWITCHOVER (planned, safe) ═══
sudo maxctrl call command mariadbmon switchover MariaDB-Monitor

# ═══ REJOIN a recovered server ═══
sudo maxctrl call command mariadbmon rejoin MariaDB-Monitor

# ═══ RELOAD CONFIG (no restart needed) ═══
sudo maxctrl alter maxscale threads 8             # Change on the fly

# ═══ ROTATE LOGS ═══
sudo maxctrl call command maxscale rotate logs
```

---

## Bonus: MaxScale Configuration for Galera Cluster

If you're using Galera instead of Master-Slave replication, use the `galeramon` monitor module instead of `mariadbmon`:

```ini
# ─── Galera Monitor ───
[Galera-Monitor]
type             = monitor
module           = galeramon
servers          = galera-1, galera-2, galera-3
user             = maxscale_user
password         = SecurePass123!
monitor_interval = 2000ms
disable_master_failback = false   # Allow master to move between nodes

# ─── Galera Service (ReadWriteSplit — picks one node for writes) ───
[Galera-RW-Service]
type            = service
router          = readwritesplit
servers         = galera-1, galera-2, galera-3
user            = maxscale_user
password        = SecurePass123!

# ─── OR use ReadConnRoute for round-robin ───
[Galera-RR-Service]
type            = service
router          = readconnroute
router_options  = synced         # Only send to synced nodes
servers         = galera-1, galera-2, galera-3
user            = maxscale_user
password        = SecurePass123!
```

---

## Complete Data Flow Summary

```
📱 Your App
    │
    │  Connects to MaxScale IP:3306
    ▼
🔀 MaxScale (Parses SQL, routes query)
    │
    ├── 📝 Writes (INSERT/UPDATE/DELETE) → Primary Server
    │
    └── 📖 Reads (SELECT) → Replica 1 or 2 (load balanced)
```

---

*MariaDB MaxScale In-Depth Guide · Complete Implementation Reference*
