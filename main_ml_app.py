# -*- coding: utf-8 -*-
"""Copy of ML_project_V4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yEkCVLzKqI_YfFX4trdwXUbAxM779oLB
"""
### Importing requirements

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("train.csv")
df_test = pd.read_csv("test.csv")

### Handling null data

df['Gender'] = df['Gender'].fillna(df['Gender'].mode().iloc[0])

df["Self_Employed"].fillna(df['Self_Employed'].mode()[0], inplace = True)

df = df[df['Married'].notna()]

df['Loan_Amount_Term'] = df['Loan_Amount_Term'].fillna(df['Loan_Amount_Term'].mode().iloc[0]).astype(int)

df['Credit_History'] = df['Credit_History'].fillna(df['Credit_History'].mode().iloc[0]).astype(int)

df['Dependents'] = df['Dependents'].replace(['0', '1', '2', '3+'], [0,1,2,3,])
df['Dependents'] = df['Dependents'].fillna(df['Dependents'].mode().iloc[0])

#df['CoapplicantIncome'] = df['CoapplicantIncome'].astype(int)
df['LoanAmount'].fillna(value = df['LoanAmount'].mean(), inplace=True)

### Handling outliers

out_df = df[df['ApplicantIncome']>=20000].index
df.drop(out_df, inplace=True)

out_df = df[df['CoapplicantIncome']>=7000].index
df.drop(out_df, inplace = True)

df.drop(columns = ['Loan_ID'], inplace = True)

### Handling unbalanced data by resampling

from sklearn.utils import resample

df_major = df[(df['Loan_Status']=='Y')]
df_minor = df[(df['Loan_Status']=='N')]

df_minor_upsample = resample(df_minor, replace = True, n_samples = 419, random_state = 42)

df_upsampled = pd.concat([df_minor_upsample, df_major])

### Encoding

# Importing labelencoder from sklearn
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()

# encoding all text data in numerical data using labelencoder by fit_transform

df_upsampled["Gender"] = le.fit_transform(df_upsampled["Gender"])
# female = 0 , male = 1
df_upsampled["Married"] = le.fit_transform(df_upsampled["Married"])
# yes = 1, no = 0
df_upsampled["Education"] = le.fit_transform(df_upsampled["Education"])
# Graduate = 0 , Not Graduate = 1
df_upsampled["Self_Employed"] = le.fit_transform(df_upsampled["Self_Employed"])
# no = 0, yes = 1
df_upsampled["Property_Area"] = le.fit_transform(df_upsampled["Property_Area"])
# urban = 2, semiurban = 1, rural = 0


numerical_columns = ['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount']


### Splitting

x = df_upsampled.drop(['Loan_Status'], axis = 1)
y = df_upsampled['Loan_Status']

#x.shape, y.shape

from sklearn.model_selection import train_test_split
xtrain,xtest,ytrain,ytest = train_test_split(x,y, test_size=0.2, random_state=True,stratify=y)

### Scaling

from sklearn.preprocessing import StandardScaler

sc = StandardScaler()

xtrain = sc.fit_transform(xtrain)
xtest = sc.fit_transform(xtest)

### Random Forrest

from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.ensemble import RandomForestClassifier

rfc = RandomForestClassifier(n_estimators=50)
rfc.fit(xtrain, ytrain)
prediction = rfc.predict(xtest)

### checking accuracy

print(confusion_matrix(ytest,prediction))
print(classification_report(ytest,prediction))

# pickling the model
import pickle
pickle_out = open("ml_classifier.pkl","wb")
pickle.dump(rfc, pickle_out)
pickle_out.close()

# a file ml_classifer will be created

#streamlit code:

pickle_in = open("ml_classifier.pkl","rb")
rfc = pickle.load(pickle_in)

# defining the function which will make predictions using
# the data which user inputs

def predictor(Gender,Married,Dependents,Education,Self_Employed,ApplicantIncome,CoapplicantIncome,LoanAmount,Loan_Amount_Term,Credit_History,Property_Area):
    predicted = rfc.predict([[Gender,Married,Dependents,Education,Self_Employed,ApplicantIncome,CoapplicantIncome,LoanAmount,Loan_Amount_Term,Credit_History,Property_Area]])

    return predicted

import streamlit as st
from PIL import Image

# This is main function we define our webpage
def main():
    # giving the webpage a little
    st.title("Loan Approval Prediction")

    # here we define some front end elements of the web page like
    # here we define some some of the front end elements of the web page like
    # the font and bg color, the padding and text color

    html_temp = """
    <div style = background-color: green; padding: 15px>
    <h2 style = color:gray; text_align:center; padding: 15px;>Streamlit Loan Approval Prediction ML App </h2>
    </div>
    """

    # this line allows us to display the front end aspects we have
    # defined in the above code

    st.markdown(html_temp, unsafe_allow_html = True)

    # the following lines create text boxes in which the user can enter  
    # the data required to make the prediction

    Gender = st.selectbox("Gender",("Female","Male"))
    Gender = (0 if Gender=="Female" else 1)
    Married = st.selectbox("Are You married or not ?", ("yes","no"))
    Married =(1 if Married=="yes" else 0)
    Dependents = st.selectbox("Number of Dependents", (0,1,2,3))
    Education = st.selectbox("Education",("Graduate","Not Graduate"))
    Education = (0 if Education=="Graduate" else 1)
    S_employed = st.selectbox("Are you self employed ?",("Yes","No"))
    S_employed= (1 if S_employed=="Yes" else 0)
    A_income = st.number_input("Applicant's monthly Income", value = 0.0)
    CoA_income = st.number_input("Coapplicant's monthly Income", value = 0.0)
    L_amount = st.number_input("Loan Amount in thousands", value = 0.0, placeholder = 'Eg. for 1,50,000 enter 150') 
    L_amount_term = st.number_input("Term of loan in months", value = 0.0)
    C_history = st.selectbox("Credit History meets guildlines",(0,1), placeholder = "If credit history mmets guidlines select 1")
    P_area= st.selectbox("Property Area",("Rural","Semiurban","Urban"))
    P_area = (0 if P_area=="Rural" else 1 if P_area=="Semiurban" else 2)
    
    result = ""
    

    if st.button("predict"):
        result = predictor(Gender,Married,Dependents,Education,S_employed,A_income,CoA_income,L_amount,L_amount_term,C_history,P_area)

    if result=='Y':
        st.success(f"{result} Loan is Approved to you !")
    else:
        st.success(f"{result} Loan is not approved to you.")


if __name__=="__main__":
               main()
    
    
