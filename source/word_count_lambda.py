import logging
from os.path import join
from tempfile import mkdtemp

import boto3
import pymysql

import rds_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Execute outside the handler for reuse
#rds settings
rds_host  = "test-mysql.cqzgi25d6is8.us-east-1.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger.info('Attempting to connect to {}@{}'.format(name, rds_host))
conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
# try:
#     conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
# except:
#     logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
#     sys.exit()
logger.info("SUCCESS: Connection to RDS mysql instance succeeded")

def lambda_handler(event, context):
    s3_bucket, s3_key = get_bucket_key_from_event(event)
    logger.info(event)
    logger.info("s3://{}/{}".format(s3_bucket, s3_key))
    output = process_file(s3_bucket, s3_key)
    return output


def get_bucket_key_from_event(event):
    records = event.get('Records', [])
    assert(len(records)==1)
    s3_json = records[0].get("s3", {})
    bucket = s3_json.get('bucket', {}).get('name')
    key = s3_json.get('object', {}).get('key')
    return bucket, key


def process_file(s3_bucket, s3_key):
    word_count = get_word_count_from_file(s3_bucket, s3_key)
    output = output_word_count(word_count, s3_bucket, s3_key)
    return output


def get_word_count_from_file(s3_bucket, s3_key):
    line_iter = get_line_iterator_from_file(s3_bucket, s3_key)
    word_count = 0
    for line in line_iter:
        word_count += get_word_count_for_line(line)
    return word_count


def get_word_count_for_line(line):
    if not line:
        return 0
    return len(line.split())


def get_line_iterator_from_file(s3_bucket, s3_key):
    temp_dir = mkdtemp()
    temp_file = join(temp_dir, 'tmp.txt')
    s3 = boto3.resource('s3')
    logger.info('Downloading {} to {}'.format(s3_key, temp_file))
    s3.Bucket(s3_bucket).download_file(s3_key, temp_file)
    logger.info('Successfully downloaded')
    with open(temp_file, 'r') as f:
        line_list = f.readlines()
    return line_list


def output_word_count(word_count, s3_bucket, s3_key):
    s3_url = 's3://{}/{}'.format(s3_bucket, s3_key)
    with conn.cursor() as cur:
        cur.execute(
            'insert into file_word_count (s3_url, word_count) values("{}", {})'.format(
                s3_url, word_count
            )
        )
        conn.commit()
    logger.info(word_count)
    return word_count
