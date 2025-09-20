Overview of MySQL
Introduction to MySQL by showing how to use the mysql client program to create and use a simple database. mysql (sometimes referred to as the “terminal monitor” or just “monitor”) is an interactive program that enables you to connect to a MySQL server, run queries, and view the results. mysql may also be used in batch mode: you place your queries in a file beforehand, then tell mysql to execute the contents of the file. Both ways of using mysql are covered here.

To see a list of options provided by mysql, invoke it with the --help option:
shell> mysql –help

This assumes that mysql is installed on your machine and that a MySQL server is available to which you can connect. 

Connecting to and disconnecting from the Server To connect to the server, you will usually need to provide a MySQL user name when you invoke mysql and, most likely, a password. If the server runs on a machine other than the one where you log in, you will also need to specify a host name. Contact your administrator to find out what connection parameters you should use to connect (that is, what host, user name, and password to use). Once you know the proper parameters, you should be able to connect like this:

shell> mysql -h host -u user –p
Enter password: ********host and user represent the host name where your MySQL server is running and the user name of your MySQL account. Substitute appropriate values for your setup. The ******** represents your password; enter it when mysql displays the Enter password: prompt. If that works, you should see some introductory information followed by a mysql> prompt:

shell> mysql -h host -u user –p

  

The mysql> prompt tells you that mysql is ready for you to enter SQL statements.
If you are logging in on the same machine that MySQL is running on, you can omit the host, and simply use the following:
shell> mysql -u user –p

If, when you attempt to log in, you get an error message such as ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/tmp/mysql.sock' (2), it means that the MySQL server daemon (Unix) or service (Windows) is not running. 
Some MySQL installations permit users to connect as the anonymous (unnamed) user to the server running on the local host. If this is the case on your machine, you should be able to connect to that server by invoking mysql without any options: shell> mysql


After you have connected successfully, you can disconnect any time by typing QUIT (or \q) at the mysql>prompt:
mysql> QUIT
Bye
On Unix, you can also disconnect by pressing Control+D

MySQL History
MySQL   -     MySQL founded 1995

26 years old Database 

1994 - MySQL by Michael (Monty) Widenius and David Axmark
First internal release on 23 May 1995

MySQL is free and open-source software under the terms of the GNU General Public License, and is also available under a variety of proprietary licenses. MySQL was owned and sponsored by the Swedish company MySQL AB.

Acquired by Sun Microsystems 2008 [JAVA, SUN SOLARIS, MYSQL SERVER]
Oracle acquired Sun Microsystems on January 2010. 

Soon after MariaDB started by original authors of MySQL Initial release on 2009

Release Background :-

 Windows version was released on 8 January 1998 for Windows 95 and NT
 Version 3.23 January 2001
 Version 4.0 March 2003 (unions)
 Version 4.1 October 2004 (R-trees and B-trees, Sub queries, prepared statements)
 Version 5.0 October 2005 (cursors, stored procedures, triggers, views)
 Sun Microsystems acquired MySQL AB on 26 February 2008.
 Version 5.1 November 2008 (Event scheduler, partitioning, plugin API, row-based replication, server log tables)
 MySQL 5.1 showed poor performance when used for data warehousing — partly due to its inability to utilize multiple CPU cores for processing a single query

 December 2012 - MariaDB foundation has been established
 On October 1, 2014, SkySQL Corporation Ab changed its name to MariaDB Corporation Ab

MariaDB is named after Monty's younger daughter Maria, similar to how MySQL is named after his other daughter My.




MySQL
Written in	C, C++
Operating system	Linux, Solaris, macOS, Windows, FreeBSD

MariaDB
Written in	C, C++, Perl, Bash
Operating system	Linux, Windows, macOS

Enterprise Edition , Standard Edition
Community Edition - Online Backups – Won’t Support - Physical Backups.
MySQL Enterprise Backup [MEB] Paid ( or ) Xtrabackup Percona GPL

MySQL Features

Relational Database Management System (RDBMS): MySQL is a relational database management system.
Easy to use: MySQL is easy to use. You have to get only the basic knowledge of SQL. You can build and interact with MySQL with only a few simple SQL statements.
It is secure: MySQL consist of a solid data security layer that protects sensitive data from intruders. Passwords are encrypted in MySQL.
Client/ Server Architecture: MySQL follows a client /server architecture. There is a database server (MySQL) and arbitrarily many clients (application programs), which communicate with the server; that is, they query data, save changes, etc.
Free to download: MySQL is free to use and you can download it from MySQL official website.
It is scalable: MySQL can handle almost any amount of data, up to as much as 50 million rows or more. The default file size limit is about 4 GB. However, you can increase this number to a theoretical limit of 8 TB of data.
Compatibale on many operating systems: MySQL is compatible to run on many operating systems, like Novell NetWare, Windows* Linux*, many varieties of UNIX* (such as Sun* Solaris*, AIX, and DEC* UNIX), OS/2, FreeBSD*, and others. MySQL also provides a facility that the clients can run on the same computer as the server or on another computer (communication via a local network or the Internet).
Allows roll-back: MySQL allows transactions to be rolled back, commit and crash recovery.
High Performance: MySQL is faster, more reliable and cheaper because of its unique storage engine architecture.
High Flexibility: MySQL supports a large number of embedded applications which makes MySQL very flexible.
High Productivity: MySQL uses Triggers, Stored procedures and views which allows the developer to give a higher productivity.
