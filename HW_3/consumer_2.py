import time
from functools import wraps
import random
from kafka import KafkaConsumer

def backoff(tries: int, sleep: int, max_jitter: int = 0) -> callable:
    """
    Decorator implementing a Kafka consumer retry mechanism with exponential backoff and jitter.

    Args:
    - tries: Maximum number of retry attempts.
    - base_sleep: Initial sleep duration between retries (in seconds).
    - max_jitter: Maximum additional random jitter to be added to sleep duration (in seconds). Default is 0.

    Returns:
    - callable: Decorator to handle Kafka consumer retry logic.
    """

    if not isinstance(tries, int) or tries <= 0:
        raise ValueError("Tries should be a positive integer")

    if not isinstance(sleep, int) or sleep <= 0:
        raise ValueError("Base sleep should be a positive integer")

    if not isinstance(max_jitter, int) or max_jitter < 0:
        raise ValueError("Max jitter should be a non-negative integer")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sleep_duration = sleep
            for attempt in range(tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < tries - 1:
                        sleep_with_jitter = sleep_duration + random.randint(0, max_jitter)
                        time.sleep(sleep_with_jitter)
                        sleep_duration *= 2  
                    else:
                        raise e
        return wrapper
    return decorator


@backoff(tries=10,sleep=60)
def message_handler(value)->None:
    print(value)


def create_consumer():
    print("Connecting to Kafka brokers")
    consumer = KafkaConsumer("itmo2023",
                             group_id='itmo_group2',
                             bootstrap_servers='localhost:29092',
                             auto_offset_reset='earliest',
                             enable_auto_commit=True)

    for message in consumer:
        # send to http get (rest api) to get response
        # save to db message (kafka) + external
        message_handler(message)
        print(message)


if __name__ == '__main__':
    create_consumer()
