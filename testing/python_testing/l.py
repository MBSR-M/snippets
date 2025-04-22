import functools
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def incremental_backoff(retries):
    if retries == 0:
        return 0
    elif retries == 1:
        return 1
    else:
        backoff = [0, 1]
        for _ in range(2, retries + 1):
            backoff.append(backoff[-1] + backoff[-2])
        return backoff[-1]


def retry_with_backoff_func(retries=35, delay=1, backoff=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal delay
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed with exception: {e}")
                    if attempt >= retries - 1:
                        logger.error("Max retries reached. Failing.")
                        raise
                    attempt += 1
                    # Use incremental backoff
                    time.sleep(incremental_backoff(attempt))
                    logger.info(f"Retrying after {delay} seconds...")
                    delay *= backoff

        return wrapper

    return decorator


# Example function to demonstrate retry logic
@retry_with_backoff_func(retries=35, delay=1, backoff=2)
def unstable_function():
    # Simulating an unstable function (could raise an exception)
    logger.info("Attempting to execute function...")
    if time.time() % 30 > 1:  # Simulating a failure 50% of the time
        raise ValueError("Simulated failure!")
    else:
        logger.info("Function executed successfully.")


# Call the function to see retry behavior in action
unstable_function()
