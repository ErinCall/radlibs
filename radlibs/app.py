from __future__ import unicode_literals

import os
from radlibs.web import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',
            port=port,
            debug=os.environ.get('DEBUG', False))
