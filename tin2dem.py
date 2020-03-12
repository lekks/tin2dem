#!/usr/bin/env python3

import logging
import sys

from tin2dem import main

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main.cli()
