# file_dispatcher

This tool talkes files from a directory and moves them into MemSQL pipelines.

## Inbound Direcory

This directory is where the files land within your environment.  These files should be static when placed in this directory as the file_dispatcher doesn't know how to address files that are currently being modified.

```
$ ls -l /var/lib/memsql/pipelines/inbound
total 12
-rwxr-xr-x 1 root root 38 Dec 12 15:18 f1.csv
-rwxr-xr-x 1 root root 47 Dec 12 15:18 f2.csv
-rwxr-xr-x 1 root root 12 Dec 12 15:18 f3.csv
```

## MemSQL filesystem (FS) Pipelines

A MemSQL filesystem pipeline was created to map to this stream of CSV files.

```
memsql> 
  CREATE PIPELINE `gpipe`
  AS LOAD DATA FS '/var/lib/memsql/pipelines/gpipe/*'
  BATCH_INTERVAL 0
  INTO TABLE `glenntab`
  FIELDS TERMINATED BY ',' ENCLOSED BY '' ESCAPED BY '\\'
  LINES TERMINATED BY '\n' STARTING BY ''
  (`glenntab`.`id`,`glenntab`.`name`);
```


For this example, the MemSQL pipeline points to the `/var/lib/memsql/pipelines/gpipe/` directory.  There are no files currently in this direcory before `file_dispatcher` is run.
```
$ ls -l /var/lib/memsql/pipelines/gpipe/
total 0
```

## file_dispatcher syntax

The `file_dispatcher.py` tool is a python script which reads the pipeline definition from MemSQL and uses various parameters to move files from the inbound `SOURCE_DIR` to the directory identified by the MemSQL pipeline name `PIPELINE_NAME`.  File dispatcher also check to see which files in the pipeline have completed and moves those file into the `DONE_DIR` direcory.  If files are successful, the name will remain the same.  If they failed for any reason, a `.fail` postfix will be added to the filename.

```
$ python ./file_dispatcher.py -h
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
 ```

## file_dispatcher runtime example

The following example will move files from the `/var/lib/memsql/pipelines/inbound` directory into the MemSQL `gpipe` pipeline within the `ssb` database on the `localhost`.

```
$ sudo python ./file_dispatcher.py -H localhost -n 3306 -D ssb -s /var/lib/memsql/pipelines/inbound -p gpipe -d /var/lib/memsql/pipelines/done
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
```

Looking at the `gpipe` directory we now see the files within MemSQL.

```
$ ls -l /var/lib/memsql/pipelines/gpipe/
total 12
-rwxr-xr-x 1 root root 38 Dec 12 15:18 f1.csv
-rwxr-xr-x 1 root root 47 Dec 12 15:18 f2.csv
-rwxr-xr-x 1 root root 12 Dec 12 15:18 f3.csv

$ ls -l /var/lib/memsql/pipelines/done
total 0
```
Running the file_dispatcher.py again, we will see the completed files moved from the pipeline directory to the done directory.

```
$ sudo python ./file_dispatcher.py -H localhost -n 3306 -D ssb -s /var/lib/memsql/pipelines/inbound -p gpipe -d /var/lib/memsql/pipelines/done
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

]$ ls -l /var/lib/memsql/pipelines/gpipe/
total 0

$ ls -l /var/lib/memsql/pipelines/done/
total 12
-rwxr-xr-x 1 root root 38 Dec 12 15:18 f1.csv
-rwxr-xr-x 1 root root 47 Dec 12 15:18 f2.csv
-rwxr-xr-x 1 root root 12 Dec 12 15:18 f3.csv.fail
```

Notice that there was one file that falied to load `f3.csv.fail`.

```
$ head -2 /var/lib/memsql/pipelines/done/*
==> /var/lib/memsql/pipelines/done/f1.csv <==
1,glenn
2,ruby

==> /var/lib/memsql/pipelines/done/f2.csv <==
6,renie
7,mazie

==> /var/lib/memsql/pipelines/done/f3.csv.fail <==
jflksd
jlkj
```

The `pipelines_errors` table within the `information_schema` shows details regarding the load failures.

```
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
```

We notice that this file was tried 4 times.  Once the the number of attempts defined by the `PIPELINES_MAX_RETRIES_PER_BATCH_PARTITION` have been reached, MemSQL pipelines no longer attemp to load the failed files.

```
memsql> select @@PIPELINES_MAX_RETRIES_PER_BATCH_PARTITION;
+---------------------------------------------+
| @@PIPELINES_MAX_RETRIES_PER_BATCH_PARTITION |
+---------------------------------------------+
|                                           4 |
+---------------------------------------------+
1 row in set (0.31 sec)
```

Finally, by default, the cluster variable `pipelines_stop_on_error` will stop a pipeline if an error occurs.  This can be bypassed if you set this variable to true.  The example below sets this variable to false.

```
memsql> select @@pipelines_stop_on_error;

+---------------------------+
| @@pipelines_stop_on_error |
+---------------------------+
|                         1 |
+---------------------------+
1 row in set (0.07 sec)

$ memsql-ops memsql-update-config --set-global --key pipelines_stop_on_error --value false --all

memsql> select @@pipelines_stop_on_error;

+---------------------------+
| @@pipelines_stop_on_error |
+---------------------------+
|                         0 |
+---------------------------+
1 row in set (0.08 sec)
```

