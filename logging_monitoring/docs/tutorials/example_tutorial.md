# Logging Monitoring - Tutorial: Setting Up and Using Centralized Logging

This tutorial will guide you through the process of setting up and using the centralized logging feature of the Logging Monitoring module in your Codomyrmex project.

## 1. Prerequisites

Before you begin, ensure you have the following:

- A Codomyrmex project structure where the `logging_monitoring` module is present.
- Python installed, and your project environment set up (virtual environment activated).
- The `python-dotenv` library installed in your project's environment (it should be in the root `requirements.txt`).
- A basic understanding of Python modules and how to run Python scripts.

## 2. Goal

By the end of this tutorial, you will be able to:

- Configure the logging behavior (level, format, output file) for your application using a `.env` file.
- Initialize the logging system in your main application script.
- Obtain and use logger instances to record messages from different parts of your application.
- Understand how to view logs in both the console and a log file.

## 3. Steps

### Step 1: Prepare Your `.env` File

The logging module is configured using environment variables, which are conveniently managed using a `.env` file in the root directory of your Codomyrmex project.

1.  **Create or Open `.env` file**:
    Navigate to your project's root directory. If you don't have a `.env` file, create one. Otherwise, open the existing one.

2.  **Add Logging Configuration**:
    Add the following lines to your `.env` file. You can customize these values.

    ```env
    # .env (in project root)

    # --- Logging Configuration ---
    CODOMYRMEX_LOG_LEVEL=DEBUG
    # Log messages at DEBUG level and above (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    CODOMYRMEX_LOG_FILE=tutorial_app.log
    # Path to the log file. If you want console-only logging, comment out or remove this line.
    # Make sure the directory for the log file exists or your app has permission to create files here.

    CODOMYRMEX_LOG_FORMAT="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    # Custom format for log messages. You can also use "DETAILED" for a more verbose default.
    ```

### Step 2: Create a Main Application Script

Let's create a simple main script that will initialize logging and simulate some application work.

1.  **Create `main_app.py`** (e.g., in your project root or a `src` directory):

    ```python
    # main_app.py
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    import time

    # It's good practice to have a helper module for other functionalities
    # Let's imagine we have a 'worker.py'
    try:
        import worker
    except ImportError:
        print("Please create worker.py as described in the tutorial.")
        worker = None 

    def run_application():
        # Crucial Step: Initialize logging ONCE at the very beginning.
        setup_logging()

        # Get a logger for this main script.
        # __name__ will be '__main__' if this script is run directly.
        logger = get_logger(__name__)

        logger.info("Application starting up...")
        logger.debug("Configuration: Log Level=%s, Log File=%s", 
                     logger.getEffectiveLevel(), 
                     [h.baseFilename for h in logger.handlers if hasattr(h, 'baseFilename')])

        for i in range(3):
            logger.info(f"Main loop iteration {i + 1}")
            if worker:
                worker.perform_task(f"Task {i + 1}")
            time.sleep(0.5)
        
        logger.warning("A sample warning event occurred.")
        logger.info("Application shutting down.")

    if __name__ == "__main__":
        run_application()
    ```

### Step 3: Create a Helper Module

Let's create the `worker.py` module that our `main_app.py` will use. This module will also use the logging system.

1.  **Create `worker.py`** (in the same directory as `main_app.py` or ensure it's importable):

    ```python
    # worker.py
    from codomyrmex.logging_monitoring import get_logger

    # Get a logger specific to this module. __name__ will be 'worker'.
    logger = get_logger(__name__)

    def perform_task(task_name: str):
        logger.info(f"Starting task: {task_name}")
        try:
            # Simulate some work that might fail
            if task_name == "Task 2":
                result = 10 / 0 # This will cause an error
            logger.debug(f"Successfully completed task: {task_name}")
        except ZeroDivisionError as e:
            logger.error(f"Error performing task '{task_name}': {e}", exc_info=True)
            # exc_info=True will include stack trace information in the log
        except Exception as e:
            logger.error(f"An unexpected error in task '{task_name}': {e}", exc_info=True)
    ```

### Step 4: Run the Application and Verify Output

1.  **Run `main_app.py`** from your terminal:
    ```bash
    python main_app.py
    ```
    (Ensure you are in the directory containing `main_app.py` and `worker.py`, or adjust the python path if needed, and that your virtual environment with dependencies is active.)

2.  **Check Console Output**:
    You should see log messages printed to your console, formatted according to `CODOMYRMEX_LOG_FORMAT`. Messages from `main_app.py` will have `__main__` as the logger name, and messages from `worker.py` will have `worker`.
    You should see INFO, DEBUG, WARNING, and ERROR messages (including a stack trace for the `ZeroDivisionError` in "Task 2").

3.  **Examine the Log File**:
    Open the `tutorial_app.log` file (or whatever you named it in `.env`). It should contain the same log messages that were printed to the console.

    Example content of `tutorial_app.log` (timestamps will vary):
    ```log
    2023-10-27 10:00:00,123 [INFO] __main__: Application starting up...
    2023-10-27 10:00:00,124 [DEBUG] __main__: Configuration: Log Level=10, Log File=['tutorial_app.log']
    2023-10-27 10:00:00,125 [INFO] __main__: Main loop iteration 1
    2023-10-27 10:00:00,126 [INFO] worker: Starting task: Task 1
    2023-10-27 10:00:00,127 [DEBUG] worker: Successfully completed task: Task 1
    ...
    2023-10-27 10:00:01,000 [INFO] worker: Starting task: Task 2
    2023-10-27 10:00:01,001 [ERROR] worker: Error performing task 'Task 2': division by zero
    Traceback (most recent call last):
      File "worker.py", line 12, in perform_task
        result = 10 / 0
    ZeroDivisionError: division by zero
    ...
    2023-10-27 10:00:01,500 [WARNING] __main__: A sample warning event occurred.
    2023-10-27 10:00:01,501 [INFO] __main__: Application shutting down.
    ```

## 4. Understanding the Results

- You have successfully configured the logging system using a `.env` file.
- `setup_logging()` initialized the system based on your configuration.
- Both `main_app.py` and `worker.py` used `get_logger(__name__)` to get distinct logger instances, allowing you to trace message origins.
- Log messages were output to both the console and the specified log file, with the defined format and level.
- `exc_info=True` in `logger.error()` automatically included stack trace information for exceptions.

## 5. Troubleshooting

- **No logs appear / Incorrect level**: 
  - Double-check `.env` for typos in variable names (`CODOMYRMEX_LOG_LEVEL`, etc.) or values.
  - Ensure `setup_logging()` is called *before* any `get_logger()` calls and only once.
  - Make sure your `.env` file is in the directory from which your application is effectively running (usually the project root).
- **Log file not created/written**: 
  - Verify `CODOMYRMEX_LOG_FILE` path and permissions. The directory must exist.
  - Check console for any error messages during `setup_logging()` (e.g., "Could not open log file").
- **"No handlers could be found for logger..."**: This means `setup_logging()` was likely not called or failed. Check its placement and any console errors.

## 6. Next Steps

Congratulations on completing this tutorial!

Now you can try:
- Changing `CODOMYRMEX_LOG_LEVEL` in `.env` to `INFO` or `WARNING` and observe how fewer messages are logged.
- Modifying `CODOMYRMEX_LOG_FORMAT` to experiment with different log appearances.
- Commenting out `CODOMYRMEX_LOG_FILE` to see console-only logging.
- Integrating this logging into more complex parts of your Codomyrmex project.
- Reviewing the [API Specification](../API_SPECIFICATION.md) for more details on configuration options. 