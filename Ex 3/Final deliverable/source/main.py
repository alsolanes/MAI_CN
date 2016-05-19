#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tqdm import tqdm
import random
import pickle
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from model_sis_epidemic import *
from MC_sim import *
from execution import *

MainExecution = MainExecution()
MainExecution.main_run()
