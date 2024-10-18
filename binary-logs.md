## Binary Logs
~~~
show binary logs;
~~~

Example, based on your server. mention the binlog.file name
~~~
show binlog events in 'binlog.000005';
~~~

## PURGE
~~~
PURGE BINARY LOGS TO 'mysql-bin.000007';
~~~
