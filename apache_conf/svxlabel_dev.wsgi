import sys

# Print error messages
sys.stdout = sys.stderr

# Setup application
sys.path.insert(0, '/projects/svxlabel_dev/site/')
from svxlabel import app as application
