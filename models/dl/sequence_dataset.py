import numpy as np
try:
    from torch.utils.data import Dataset
except ImportError:
    class Dataset: pass
class SequenceDataset(Dataset):
    def __init__(self,sequences,labels):
        if len(sequences)!=len(labels):raise ValueError("sequences and labels must have equal length")
        self.sequences=[np.asarray(x,dtype=np.float32) for x in sequences];self.labels=list(labels)
    def __len__(self):return len(self.sequences)
    def __getitem__(self,index):return self.sequences[index],self.labels[index]
