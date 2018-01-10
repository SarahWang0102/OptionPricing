import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import pickle
import QuantLib as ql

from OptionStrategyLib.calibration import SVICalibration

# calendar = ql.China()
# daycounter = ql.ActualActual()


evalDate = datetime.date(2017,12,8)

svicalibration = SVICalibration()
