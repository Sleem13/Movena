WARNING="DL model validation scope must be reported with every artifact."
try:
 import torch.nn as nn
 class LSTMClassifier(nn.Module):
  def __init__(self,input_size,hidden_size,num_classes):
   super().__init__();self.lstm=nn.LSTM(input_size,hidden_size,batch_first=True);self.head=nn.Linear(hidden_size,num_classes)
  def forward(self,x):return self.head(self.lstm(x)[0][:,-1,:])
except ImportError:
 class LSTMClassifier:
  def __init__(self,*_a,**_k):raise RuntimeError("PyTorch is optional. Install requirements-ml.txt to enable DL training.")
