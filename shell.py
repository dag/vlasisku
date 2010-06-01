#!/usr/bin/env python

import os
import readline
from pprint import pprint

from flask import *

from vlasisku import *
from vlasisku.utils import *
from vlasisku.database import *
from vlasisku.models import *


os.environ['PYTHONINSPECT'] = 'True'

