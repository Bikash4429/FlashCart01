import os

# QuickCommerce API Configuration
# Website: https://quickcommerceapi.com/dashboard
QC_API_KEY = os.getenv("QC_API_KEY", "adc91f7a-afb3-46ca-b5a1-4f805b6d1324")
QC_BASE_URL = "https://api.quickcommerceapi.com"

# Default Coordinates for Quick Commerce Delivery (Bhubaneswar Core Hub)
DEFAULT_LAT = 20.2961
DEFAULT_LON = 85.8245
DEFAULT_PLATFORMS = ["BlinkIt", "Zepto", "Swiggy"]
