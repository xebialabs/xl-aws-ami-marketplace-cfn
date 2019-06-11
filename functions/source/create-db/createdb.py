#!/usr/bin/python
import psycopg2
from cfn_lambda_handler import Handler, SUCCESS, FAILED
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.info("Started Lambda!")
physical_resource_id = "dummy-resource-id"

handler = Handler()

def fail(reason, physical_resource_id=physical_resource_id):
    logger.error("Failed [%s]: %s" % (physical_resource_id, reason))
    return {"Status": FAILED, "PhysicalResourceId": physical_resource_id, "Reason": reason}

def check_props(props, param):
    if param not in props or not props[param]:
        raise Exception('Parameter %s not found.' % param)
    return props[param]

@handler.create
def create_database(event, context):
    props = event['ResourceProperties']
    logger.info('Got event: %s' % event)
    try:
        db_names = check_props(props, 'DBNames')
        db_user = check_props(props, 'DBUser')
        db_password = check_props(props, 'DBPassword')
        db_host = check_props(props, 'DBHost')
        if 'PhysicalResourceId' in event:
            physical_resource_id = event['PhysicalResourceId']
        else:
            physical_resource_id = "%s_%s" % (db_host, db_names[0])
    except Exception as e:
        return fail(str(e), physical_resource_id="parameters-not-set")

    logger.info("Pre-connect to %s via Psycopg2" % db_host)
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(database='postgres', user=db_user, host=db_host, password=db_password)
        logger.info("Connected to Database %s" % db_host)
    except Exception as e:
        return fail('Could not connect to the Postgres DB: %s' % str(e))
    else:
        try:
            conn.set_session(autocommit=True)
            with conn.cursor() as cursor:
                create_databases(db_names, db_host, db_user, cursor)
            logger.info("All Databases created.")
        except Exception as e:
            return fail(str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    logger.info("Done!")
    return { "Status": SUCCESS, "PhysicalResourceId": physical_resource_id, "Reason": 'Successfully created databases %s' % db_names }

def create_databases(db_names, db_host, db_user, cursor):
    for db_name in db_names:
        cursor.execute("SELECT datname FROM pg_database")
        for dat_name in cursor:
            if dat_name[0] == db_name:
                logger.info("Database %s already exists, not (re-)creating it." % db_name)
                break
        else:
            logger.info("Creating database %s on %s" % (db_name, db_host))
            cursor.execute("CREATE DATABASE %s WITH OWNER %s" % (db_name, db_user))
            logger.info("Database %s created" % db_name)

@handler.delete
def delete(event, context):
    props = event['ResourceProperties']
    logger.info('Got event: %s' % event)
    try:
        db_names = check_props(props, 'DBNames')
        db_user = check_props(props, 'DBUser')
        db_password = check_props(props, 'DBPassword')
        db_host = check_props(props, 'DBHost')
        if 'PhysicalResourceId' in event:
            physical_resource_id = event['PhysicalResourceId']
        else:
            physical_resource_id = "%s_%s" % (db_host, db_names[0])
    except Exception as e:
        return fail(str(e), physical_resource_id="parameters-not-set")
    return {"Status": SUCCESS, "PhysicalResourceId": physical_resource_id, "Reason": 'Nothing to delete, keeping data intact'}
