import logging

# Create a logger
logger = logging.getLogger('lms_app')
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Function to set up logging
def setup_logging():
    """Configure logging for the application"""
    pass  # Main setup is already done above