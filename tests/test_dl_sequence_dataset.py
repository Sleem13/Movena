import numpy as np
from models.dl.sequence_dataset import SequenceDataset
def test_sequence_dataset_synthetic_cpu_data():
 d=SequenceDataset([np.zeros((3,6)),np.ones((4,6))],[0,1]);assert len(d)==2;assert d[0][0].shape==(3,6) and d[1][1]==1
