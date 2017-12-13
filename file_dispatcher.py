import logging
import argparse
import sys
from os import path as osPath, makedirs, rename, listdir, rmdir, remove, environ
from time import time as ts
from glob import glob
from hashlib import md5
from gzip import GzipFile
import datetime

from memsql.common import database

# Custom common packages
#from common.memsql_cluster_old import MemsqlCluster, convertSqlValues, sqlStringify
#from common.config import getConfigAndSpecs

__appname__ = 'file_dispatcher'
__version__ = '0.9.0'
__authors__ = ['Glenn Fawcett']
__credits__ = ['Justin Benson', 'Jeremy Althouse']


log = logging.getLogger(__name__)


#   Globals and Constants
###############################################################################
class G: # pylint: disable=R0903
    """Batman Global & Constants"""
    CONFIG_DEFAULT_PATH = 'config/config.hjson'
    LOG_DIRECTORY_NAME = 'logs'

    CLUSTER_SYS_VAR_NAME = 'MEMSQL_CLUSTER'

    LAND_STATUS = 'land'
    DUPE_STATUS = 'duplicate'
    IMPORT_STATUS = 'import'
    DONE_STATUS = 'done'
    FAIL_STATUS = 'fail'

    UNDEFINED_STATUS = 'UNDEFINED'

    HEADER_PIPELINE_NAME = 'pipelineWindow'

    is_master = None
    pipelines_path = None
    pipeline_retries = None
    database_name = None
    root_source_dir = None
    cluster = None
    conn = None
    paired_cluster = None
    conn_pair = None
    is_paired_cluster_reachable = True

class SQL:
    pipeline_window_insert_query = """
        INSERT INTO pipelineWindow (pipelineName, startTime, isFinal, loadCount) 
        VALUES 
    """

    getCreatePipelineQuery = """
        SHOW CREATE PIPELINE {};
    """

#   Helper Functions
###############################################################################
def snakeToCamelCase(name):
    """ converst string from snake_case to camelCase """
    components = name.split('_')
    return components[0] + "".join(x.title() for x in components[1:])

def makeDirIfNeeded(d):
    """ create dir if is does not exist """
    if not osPath.exists(d):
        makedirs(d)
        # log.debug('Created needed directory at: {}'.format(d))







#   Main Function
###############################################################################
def getArgs():
    """ Get command line args """
    desc = 'Process specs (in the specs_path directory defined in config) on specified cluster)'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help='Verbose logging')
    parser.add_argument("-o", "--console-log", dest='console_log', action="store_true", default=True, help='send log output to console, as well as logfiles')
    parser.add_argument("-H", "--hostname", dest='hostname', help='hostname to connect')
    parser.add_argument("-n", "--portnum", dest='portnum', default=3306, help='port number')    
    parser.add_argument('-D', "--database", dest='database_name', help='database to connect')
    parser.add_argument("-s", "--source_dir", dest='source_dir', help='source directory for files')
    parser.add_argument("-p", "--pipeline_name", dest='pipeline_name', help='pipeline name')
    parser.add_argument("-d", "--done_dir", dest='done_dir', help='directory for pipeline files that have finished loading')    
    options = parser.parse_args()
    # TODO: ensure args inputs are value
    return options

def main():
    # load the config and get cluster name and db connection
    options = getArgs()
    #config, specs = getConfigAndSpecs(options.config_path)

    config = {}
    config['scripts_path'] = '/tmp'
    # logging configuration
    base_logging_path = osPath.join(config['scripts_path'], G.LOG_DIRECTORY_NAME, __appname__)
    makeDirIfNeeded(base_logging_path)
    general_logging_path = osPath.join(base_logging_path, 'GENERAL')
    makeDirIfNeeded(general_logging_path)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    level = logging.DEBUG if options.verbose else logging.INFO
    handler = logging.FileHandler(osPath.join(general_logging_path, 'general_{}.log'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3])))
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)

    if options.console_log:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        log.addHandler(console_handler)

    log.info("In the beginning...")
    log.info("Hostname : {}".format(options.hostname))
    log.info("Port number : {}".format(options.portnum))
    log.info("Database Target : {}".format(options.database_name))
    log.info("Source Directory : {}".format(options.source_dir))
    log.info("Pipeline Name : {}".format(options.pipeline_name))
    log.info("Done Directory : {}".format(options.done_dir))
    
    conn_params = {
        'user': 'root',
        'password': '',
        'host': '0.0.0.0',
        'port': 3306,
        'database': 'ssb'
    }

    conn = database.connect(**conn_params)    

    if not osPath.exists(options.source_dir):
        log.error("Source directory does not exhist!")
        exit(1)

    
    # look up pipeline_retries
    select_sql = '''
    SELECT variable_value 
    FROM information_schema.global_variables
    WHERE variable_name = 'PIPELINES_MAX_RETRIES_PER_BATCH_PARTITION'
    '''
    log.debug('Pipeline retries query : ' + select_sql)
    row = conn.get(select_sql)
    pipeline_retries = int(row['variable_value'])
    log.info('Pipelines will retry files {} times before moving to Fail'.format(pipeline_retries))

    # look up pipeline_name, state, and pipeline directory
    select_sql = '''
    SELECT pipeline_name, state, config_json::$connection_string constr
    FROM information_schema.pipelines
    WHERE pipeline_name = '{}' and database_name = '{}'
    '''.format(options.pipeline_name, options.database_name)
    log.debug('Pipeline retries query : ' + select_sql)

    row2 = conn.get(select_sql)
    if row2:
        log.info('Pipeline {} exists'.format(row2['pipeline_name']))
        pipeline_directory = osPath.dirname(row2['constr'].decode('utf-8'))
        log.info(pipeline_directory)
    else:
        log.error('Pipeline {} does NOT exist!'.format(options.pipeline_name))
        return(-1)
    
    # Check to see if pipeline is running
    if row2['state'] != 'Running':
        log.error('Pipeline {} is not Running!!'.format(options.pipeline_name))
        return(-1)

    # Move files to pipeline directory
    files = [f for f in glob(osPath.join(options.source_dir, "*")) if True]
    for f in files:
        bfile = osPath.basename(f)
        destfullfile = osPath.join(pipeline_directory, bfile)
        log.info ("Move {} to {}".format(f, destfullfile))
        rename(f, destfullfile)

    # Find files that have loaded
    files = [f for f in glob(osPath.join(pipeline_directory, "*")) if True]
    for f in files:
        log.info ("Full filename in Pipeline Directory: {}".format(f))
        bfile = osPath.basename(f)
        log.info ("Files in Pipeline Directory: {}".format(bfile))

        # lookup file load status in pipelines_offsets table
        select_sql = '''
        SELECT pipeline_name, database_name, source_partition_id, latest_loaded_offset
        FROM information_schema.pipelines_offsets
        WHERE database_name = '{}' and pipeline_name = '{}' and source_partition_id like '%{}'
        '''.format(options.database_name, options.pipeline_name, bfile)
        log.debug('Pipeline retries query : ' + select_sql)

        row = conn.get(select_sql)

        # check for errors in the pipeline
        select_sql = '''
        SELECT count(*) error_count 
        FROM information_schema.pipelines_errors
        WHERE database_name = '{}' and pipeline_name = '{}' and batch_source_partition_id like '%{}'
        '''.format(options.database_name, options.pipeline_name, bfile)
        log.debug('Pipeline retries query : ' + select_sql)

        row2 = conn.get(select_sql)

        if row:
            if row['latest_loaded_offset'] == 0:
		if row2['error_count'] == 0:
                	log.info('File {} of Pipeline {} has finished loading!!'.format(row['source_partition_id'], row['pipeline_name']))
                	destfullfile = osPath.join(options.done_dir, bfile)
                	log.info('Moving file {} to {}'.format(f, destfullfile))
                	rename(f,destfullfile)
		if row2['error_count'] >= pipeline_retries:
                	log.info('File {} of Pipeline {} has FAILED loading {} times!!'.format(row['source_partition_id'], row['pipeline_name'], pipeline_retries ))
			destfullfile = osPath.join(options.done_dir, bfile + '.fail')
                	log.info('Moving file {} to {}'.format(f, destfullfile))
                	rename(f,destfullfile)
            else:
                log.info('File {} of Pipeline {} in process'.format(row['source_partition_id'], row['pipeline_name']))

            
    conn.close()


#   Runs everything above here
###############################################################################
if __name__ == '__main__':
    main()
