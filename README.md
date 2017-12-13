# file_dispatcher

This tool talkes files from a directory and moves them into MemSQL pipelines.


[glenn@localhost file_dispatcher]$
[glenn@localhost file_dispatcher]$ ls -l /var/lib/memsql/pipelines/inbound
total 12
-rwxr-xr-x 1 root root 38 Dec 12 15:18 f1.csv
-rwxr-xr-x 1 root root 47 Dec 12 15:18 f2.csv
-rwxr-xr-x 1 root root 12 Dec 12 15:18 f3.csv
[glenn@localhost file_dispatcher]$ memsql
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 90
Server version: 5.5.8 MemSQL source distribution (compatible; MySQL Enterprise & MySQL Commercial)

Copyright (c) 2000, 2016, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

memsql> use ssb;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
memsql> show create pipeline gpipe;
+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Pipeline | Create Pipeline                                                                                                                                                                                                                                        |
+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| gpipe    | CREATE PIPELINE `gpipe`
AS LOAD DATA FS '/var/lib/memsql/pipelines/gpipe/*'
BATCH_INTERVAL 0
INTO TABLE `glenntab`
FIELDS TERMINATED BY ',' ENCLOSED BY '' ESCAPED BY '\\'
LINES TERMINATED BY '\n' STARTING BY ''
(`glenntab`.`id`,`glenntab`.`name`) |
+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.01 sec)

memsql> quit
Bye
[glenn@localhost file_dispatcher]$ ls -l /var/lib/memsql/pipelines/gpipe/
total 0

[glenn@localhost file_dispatcher]$ python ./file_dispatcher.py -h
usage: file_dispatcher.py [-h] [-v] [-o] [-H HOSTNAME] [-n PORTNUM]
                          [-D DATABASE_NAME] [-s SOURCE_DIR]
                          [-p PIPELINE_NAME] [-d DONE_DIR]

Process specs (in the specs_path directory defined in config) on specified
cluster)

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose logging
  -o, --console-log     send log output to console, as well as logfiles
  -H HOSTNAME, --hostname HOSTNAME
                        hostname to connect
  -n PORTNUM, --portnum PORTNUM
                        port number
  -D DATABASE_NAME, --database DATABASE_NAME
                        database to connect
  -s SOURCE_DIR, --source_dir SOURCE_DIR
                        source directory for files
  -p PIPELINE_NAME, --pipeline_name PIPELINE_NAME
                        pipeline name
  -d DONE_DIR, --done_dir DONE_DIR
                        directory for pipeline files that have finished
                        loading
[glenn@localhost file_dispatcher]$ sudo python ./file_dispatcher.py -H localhost -n 3306 -D ssb -s /var/lib/memsql/pipelines/inbound -p gpipe -d /var/lib/memsql/pipelines/done
2017-12-12 15:19:37,202 INFO In the beginning...
2017-12-12 15:19:37,202 INFO Hostname : localhost
2017-12-12 15:19:37,202 INFO Port number : 3306
2017-12-12 15:19:37,202 INFO Database Target : ssb
2017-12-12 15:19:37,202 INFO Source Directory : /var/lib/memsql/pipelines/inbound
2017-12-12 15:19:37,202 INFO Pipeline Name : gpipe
2017-12-12 15:19:37,202 INFO Done Directory : /var/lib/memsql/pipelines/done
2017-12-12 15:19:37,205 INFO Pipelines will retry files 4 times before moving to Fail
2017-12-12 15:19:37,206 INFO Pipeline gpipe exists
2017-12-12 15:19:37,206 INFO /var/lib/memsql/pipelines/gpipe
2017-12-12 15:19:37,206 INFO Move /var/lib/memsql/pipelines/inbound/f1.csv to /var/lib/memsql/pipelines/gpipe/f1.csv
2017-12-12 15:19:37,206 INFO Move /var/lib/memsql/pipelines/inbound/f2.csv to /var/lib/memsql/pipelines/gpipe/f2.csv
2017-12-12 15:19:37,206 INFO Move /var/lib/memsql/pipelines/inbound/f3.csv to /var/lib/memsql/pipelines/gpipe/f3.csv
2017-12-12 15:19:37,207 INFO Full filename in Pipeline Directory: /var/lib/memsql/pipelines/gpipe/f1.csv
2017-12-12 15:19:37,207 INFO Files in Pipeline Directory: f1.csv
2017-12-12 15:19:37,208 INFO Full filename in Pipeline Directory: /var/lib/memsql/pipelines/gpipe/f2.csv
2017-12-12 15:19:37,208 INFO Files in Pipeline Directory: f2.csv
2017-12-12 15:19:37,209 INFO Full filename in Pipeline Directory: /var/lib/memsql/pipelines/gpipe/f3.csv
2017-12-12 15:19:37,209 INFO Files in Pipeline Directory: f3.csv

[glenn@localhost file_dispatcher]$ ls -l /var/lib/memsql/pipelines/gpipe/
total 12
-rwxr-xr-x 1 root root 38 Dec 12 15:18 f1.csv
-rwxr-xr-x 1 root root 47 Dec 12 15:18 f2.csv
-rwxr-xr-x 1 root root 12 Dec 12 15:18 f3.csv

[glenn@localhost file_dispatcher]$ ls -l /var/lib/memsql/pipelines/done
total 0


[glenn@localhost file_dispatcher]$ sudo python ./file_dispatcher.py -H localhost -n 3306 -D ssb -s /var/lib/memsql/pipelines/inbound -p gpipe -d /var/lib/memsql/pipelines/done
2017-12-12 15:19:57,506 INFO In the beginning...
2017-12-12 15:19:57,506 INFO Hostname : localhost
2017-12-12 15:19:57,506 INFO Port number : 3306
2017-12-12 15:19:57,507 INFO Database Target : ssb
2017-12-12 15:19:57,507 INFO Source Directory : /var/lib/memsql/pipelines/inbound
2017-12-12 15:19:57,507 INFO Pipeline Name : gpipe
2017-12-12 15:19:57,507 INFO Done Directory : /var/lib/memsql/pipelines/done
2017-12-12 15:19:57,509 INFO Pipelines will retry files 4 times before moving to Fail
2017-12-12 15:19:57,510 INFO Pipeline gpipe exists
2017-12-12 15:19:57,510 INFO /var/lib/memsql/pipelines/gpipe
2017-12-12 15:19:57,511 INFO Full filename in Pipeline Directory: /var/lib/memsql/pipelines/gpipe/f1.csv
2017-12-12 15:19:57,511 INFO Files in Pipeline Directory: f1.csv
2017-12-12 15:19:57,512 INFO File /var/lib/memsql/pipelines/gpipe/f1.csv of Pipeline gpipe has finished loading!!
2017-12-12 15:19:57,513 INFO Moving file /var/lib/memsql/pipelines/gpipe/f1.csv to /var/lib/memsql/pipelines/done/f1.csv
2017-12-12 15:19:57,513 INFO Full filename in Pipeline Directory: /var/lib/memsql/pipelines/gpipe/f2.csv
2017-12-12 15:19:57,513 INFO Files in Pipeline Directory: f2.csv
2017-12-12 15:19:57,515 INFO File /var/lib/memsql/pipelines/gpipe/f2.csv of Pipeline gpipe has finished loading!!
2017-12-12 15:19:57,515 INFO Moving file /var/lib/memsql/pipelines/gpipe/f2.csv to /var/lib/memsql/pipelines/done/f2.csv
2017-12-12 15:19:57,515 INFO Full filename in Pipeline Directory: /var/lib/memsql/pipelines/gpipe/f3.csv
2017-12-12 15:19:57,515 INFO Files in Pipeline Directory: f3.csv
2017-12-12 15:19:57,519 INFO File /var/lib/memsql/pipelines/gpipe/f3.csv of Pipeline gpipe has FAILED loading 4 times!!
2017-12-12 15:19:57,519 INFO Moving file /var/lib/memsql/pipelines/gpipe/f3.csv to /var/lib/memsql/pipelines/done/f3.csv.fail

[glenn@localhost file_dispatcher]$ ls -l /var/lib/memsql/pipelines/gpipe/
total 0

[glenn@localhost file_dispatcher]$ ls -l /var/lib/memsql/pipelines/done/
total 12
-rwxr-xr-x 1 root root 38 Dec 12 15:18 f1.csv
-rwxr-xr-x 1 root root 47 Dec 12 15:18 f2.csv
-rwxr-xr-x 1 root root 12 Dec 12 15:18 f3.csv.fail

[glenn@localhost file_dispatcher]$ head -2 /var/lib/memsql/pipelines/done/*
==> /var/lib/memsql/pipelines/done/f1.csv <==
1,glenn
2,ruby

==> /var/lib/memsql/pipelines/done/f2.csv <==
6,renie
7,mazie

==> /var/lib/memsql/pipelines/done/f3.csv.fail <==
jflksd
jlkj


memsql> select database_name, pipeline_name, error_message
    -> from pipelines_errors
    -> where database_name='ssb' and pipeline_name='gpipe' and batch_source_partition_id like '%f3.csv';
+---------------+---------------+--------------------------------------------+
| database_name | pipeline_name | error_message                              |
+---------------+---------------+--------------------------------------------+
| ssb           | gpipe         | Row 1 doesn't contain data for all columns |
| ssb           | gpipe         | Row 1 doesn't contain data for all columns |
| ssb           | gpipe         | Row 1 doesn't contain data for all columns |
| ssb           | gpipe         | Row 1 doesn't contain data for all columns |
+---------------+---------------+--------------------------------------------+
4 rows in set (1.18 sec)

memsql> select @@PIPELINES_MAX_RETRIES_PER_BATCH_PARTITION;
+---------------------------------------------+
| @@PIPELINES_MAX_RETRIES_PER_BATCH_PARTITION |
+---------------------------------------------+
|                                           4 |
+---------------------------------------------+
1 row in set (0.31 sec)

memsql> select @@pipelines_stop_on_error;

## DON"T STOP ON ERROR
+---------------------------+
| @@pipelines_stop_on_error |
+---------------------------+
|                         0 |
+---------------------------+
1 row in set (0.07 sec)
