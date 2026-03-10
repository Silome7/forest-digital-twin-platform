import ee

SERVICE_ACCOUNT = 'forest-digital-twin-sa@forest-digital-twin.iam.gserviceaccount.com'
KEY_FILE = '/home/lonkou/Forest-digital-twin/forest-digital-twin-bc19e8eeed98.json'

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
ee.Initialize(credentials)

print("✓ Earth Engine authenticated!")
