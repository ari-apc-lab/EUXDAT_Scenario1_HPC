import pandas as pd
from sklearn.model_selection import train_test_split
import os
import numpy as np

cols=['band_'+str(band)+'bin_'+str(i) for band in (4,8,2) for i in range (0,5000,100)]
cols.append('lu_class')
values_folder='output_files/'
files=os.listdir(values_folder)
dataframes=[]
for file in files:
    if file.endswith('npy'):
        matrix=np.load(values_folder+file)
        df=pd.DataFrame(data=matrix[1:,:],columns=cols)
        dataframes.append(df)
df=pd.concat(dataframes)
df = df[df.lu_class != 0.0]
y = df['lu_class'].values
X_train, X_test, y_train, y_test = train_test_split(df.iloc[:,:150], y, test_size=0.05)
