import pip
from pip._internal import main as pipmain

def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pipmain(['install', package])

# Install required dependencies.
import_or_install('requests')
import_or_install('selenium')
import_or_install('flask')
import_or_install('flask_sslify')
import_or_install('PyJWT')

# Install chromedriver.
from chromedriver import get_driver
driver = get_driver()
if driver:
    print('Loaded chromedriver successfully.')
else:
    raise Exception("Error downloading chromedriver. If running on Windows, please run Python from a Windows Command Prompt (not WSL). See https://chromedriver.chromium.org/downloads")
