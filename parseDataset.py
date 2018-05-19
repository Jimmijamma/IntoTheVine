'''
Created on 09 mag 2018

@author: jimmijamma
'''
import pandas as pd
import numpy as np
from sklearn import datasets, linear_model, neural_network
from sklearn.metrics import mean_squared_error, r2_score

if __name__ == '__main__':

    mat=pd.read_excel("/Users/jimmijamma/Desktop/Dataset.xlsx")
    mat.as_matrix()
    mat=np.array(mat[2:])
    #col0=mat[:,0].astype(str)
    for ii, el in enumerate(mat[:,0]):
        mat[:,0][ii]=el.month
    mat=mat.astype(float)
    
    '''
    col1 = mat['T']
    col2 = mat['U']
    col3 = mat['P']
    col4 = mat['B']
    T=col1[2:]
    T=np.array(list(map(float,T)))
    U=col2[2:]
    U=list(map(float,U))
    P=col3[2:]
    P=list(map(float,P))
    B=col4[2:]
    B=np.array(list(map(float,B)))/1000
    '''
    
    X=mat[:,:4] # Month,Temperature,Humidity,RainQuantity
    B=mat[:,-1]/1000 # Leaf Wetness
    # Create linear regression object
    regr = neural_network.MLPRegressor(max_iter=20000)
    
    '''
    regr = neural_network.MLPClassifier(max_iter=20000)
    B=pd.cut(B,bins=[-np.inf,120,600,np.inf], labels=[0,1,2])
    B=np.array(B)
    '''
    
    lim= int(np.shape(B)[0]*0.9)
    X_train=X[:lim]
    X_test=X[lim:]
    y_train=B[:lim]
    y_test=B[lim:]
    
    
    
    # Train the model using the training sets
    regr.fit(X_train, y_train)
    
    # Make predictions using the testing set
    y_pred = regr.predict(X_test)
    
    
    

    # The mean squared error
    print("Mean squared error: %.2f"
          % mean_squared_error(y_test, y_pred))
    # Explained variance score: 1 is perfect prediction
    print('Variance score: %.2f' % r2_score(y_test, y_pred))
    
    print y_test
    print y_pred
    
    error_list=[]
    for i in range(len(y_test)):
        error_list.append(abs(y_test[i]-y_pred[i]))
        
    print np.mean(error_list)
    print np.std(error_list)
    
    