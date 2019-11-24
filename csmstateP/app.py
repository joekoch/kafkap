import json
import logging
import traceback
import kafka
import kafka.errors as er
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
rlogger = logging.getLogger()
rlogger.setLevel(logging.INFO)
rlogger.addHandler(logging.StreamHandler(sys.stdout))

success_count = 0


def on_send_success(record_metadata):
    try:
        global success_count
        success_count = success_count + 1
    except Exception as e:
        # Send some context about this error to Lambda Logs
        logger.error(e)
        logger.error(traceback.format_exc())

        raise e


def on_send_error(e):
    try:
        logger.error('Publishing failed ', exc_info=e)
    except Exception as e:
        # Send some context about this error to Lambda Logs
        logger.error(e)
        logger.error(traceback.format_exc())

        raise e


def lambda_handler(event, context):
    try:

        producer = kafka.KafkaProducer(
            bootstrap_servers=['ec2-52-14-87-233.us-east-2.compute.amazonaws.com:9092'],
            value_serializer=lambda x:
            json.dumps(x).encode('utf-8'),
            key_serializer=lambda x:
            json.dumps(x).encode('utf-8'),
            batch_size=0, request_timeout_ms=3000, api_version_auto_timeout_ms=30000,
            client_id='gstorauth', api_version=(1, 0, 0))

        producer.bootstrap_connected()

        for i, e in enumerate(range(10)):
            data = {'number': e}
            future = producer.send('test', key=i, value=data)
            future.add_callback(on_send_success).add_errback(on_send_error)

        producer.flush()

        producer.close()

    except er.KafkaError as e:
        logger.error(e)
        logger.error(traceback.format_exc())

        raise e
    except Exception as e:
        # Send some context about this error to Lambda Logs
        logger.error(e)
        logger.error(traceback.format_exc())

        raise e
    finally:
        logger.info('successfully published ' + str(success_count) + ' messages')
