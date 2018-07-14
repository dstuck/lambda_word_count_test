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


def get_word_count_from_file(s3_bucket, s3_key, log_freq=500000):
    line_iter = get_line_iterator_from_file(s3_bucket, s3_key)
    word_count = 0
    for i, line in enumerate(line_iter):
        if (i+1) % log_freq == 0:
            logger.info("Processed {} lines".format(i+1))
        word_count += get_word_count_for_line(line)
    return word_count


def get_word_count_for_line(line):
    if not line:
        return 0
    return len(line.split())


def get_line_iterator_from_file(s3_bucket, s3_key):
    s3_client = boto3.client('s3')
    s3_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    return iter_lines(s3_object['Body'], chunk_size=1024*10)

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


## Because of stupid old version of boto3, do not have access to StreamingBody.iter_lines
#  code taken from botocore version 1.10.48
def iter_chunks(streaming_body, chunk_size=1024):
    """Return an iterator to yield chunks of chunk_size bytes from the raw
    stream.
    """
    while True:
        current_chunk = streaming_body.read(chunk_size)
        if current_chunk == b"":
            break
        yield current_chunk

def iter_lines(streaming_body, chunk_size=1024):
    """Return an iterator to yield lines from the raw stream.

    This is achieved by reading chunk of bytes (of size chunk_size) at a
    time from the raw stream, and then yielding lines from there.
    """
    pending = None
    for chunk in iter_chunks(streaming_body, chunk_size):
        if pending is not None:
            chunk = pending + chunk

        lines = chunk.splitlines()

        if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
            # We might be in the 'middle' of a line. Hence we keep the
            # last line as pending.
            pending = lines.pop()
        else:
            pending = None

        for line in lines:
            yield line

    if pending is not None:
        yield pending
