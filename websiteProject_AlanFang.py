# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 13:01:07 2024

@author: Alanf
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

st.title("Alan's Curve/Data Fitter")

# Set default values
if "file_selection" not in st.session_state:
    st.session_state.file_selection = None
if "chart_type" not in st.session_state:
    st.session_state.chart_type = None
    
Bool = False
header_y = None
header_x = None

# def functions for later
def polynomial(x, *coeffs):
    y = np.polyval(coeffs, x)

    return y


def exponential(x, a, b, c):
    y = a * np.exp(b * x) + c
    return y 


def linear(x, m, b):
    y = m*x+b
    return y

# intilailize data
chart_data = pd.DataFrame()

# To get data input method
option = st.selectbox(
    "How would you like to input data?",
    ("By csv file", "By hand"),
    index=None,
    placeholder="Select input method",
    key="file_selection",
)


# Gets csv input
if st.session_state.file_selection == "By csv file":

    uploaded_file = st.file_uploader("Upload a csv file")
    if uploaded_file is not None:
        
        try:
            chart_data = pd.read_csv(uploaded_file)
    
            header_x, header_y = list(chart_data)
            
            header_g = st.text_input("Enter title of graph")
            
        except ValueError as e: 
            st.write("Too many data sets to unpack, can only accept two data sets")
            
# Get hand input
if st.session_state.file_selection == "By hand":
    
    left, middle, right = st.columns(3, vertical_alignment="bottom")
    
    with middle:
        header_x = st.text_input("Enter X header")

    with right:
        header_y = st.text_input("Enter Y header")
    
    with left:
        df = pd.DataFrame(
            [
                {header_x: "",
                 header_y: ""}
            ]
        )
        chart_data = st.data_editor(df, num_rows="dynamic")

    header_g = st.text_input("Enter title of graph")


#Gets chart type that the user wants to output
if not chart_data.empty and st.session_state.file_selection is not None and (header_y != None and header_x != None):

    st.selectbox(
        "What chart/curve would you like?",
        ("Bar Chart", "Polynomial", "Linear", "Exponential"),
        index=None,
        placeholder="Select Chart Type",
        key="chart_type",
    )

    #Checks for any errors within the csv fie or hand input 
    try:

        if chart_data[header_x].isnull().any() or chart_data[header_y].isnull().any():
            st.write("Your chart is missing some values")
            
        else:
            chart_data[header_y] = pd.to_numeric(chart_data[header_y]) 
            
            Bool = True
            
            if st.session_state.chart_type != "Bar Chart":
                try: 
                    chart_data[header_x] = pd.to_numeric(chart_data[header_x])
                    
                    Bool = True
                    
                except Exception as e:
                    Bool = False
                    st.write("Please make sure the data in " + header_x + " is numerical",)

    except: 
        st.write("Please make sure the data in " + header_y + " is numerical",)

#Displays Bar Chart
if st.session_state.chart_type == "Bar Chart" and Bool:
    st.bar_chart(chart_data, x=header_x, y=header_y, color=header_x)
            
#If not a bar chart displays other types of charts
if Bool and not st.session_state.chart_type == None and st.session_state.chart_type != "Bar Chart":

    params = []
    covariance = []
    x_data = chart_data[header_x].values
    y_data = chart_data[header_y].values    
    
    xfine = np.linspace(x_data.min(), x_data.max(), 50)
    
    fig, ax = plt.subplots()
    plt.scatter(x_data, y_data, label='Data', color='blue')
    ax.set_xlabel(header_x)
    ax.set_ylabel(header_y)
    
    try:
        if st.session_state.chart_type == "Polynomial":

            degree = st.number_input(
                    "Please input a degree",
                    step=1,
                    min_value=1,    
                    max_value=len(chart_data[header_x])-1
                               )
            initial_guesses = np.ones(degree + 1)
            params, covariance = curve_fit(polynomial, x_data, y_data, p0=initial_guesses)
            plt.plot(xfine, polynomial(xfine, *params), label='Fitted Line', color='red')
            y_ndata = polynomial(x_data, *params)
            
        if st.session_state.chart_type == "Linear":
            params, covariance = curve_fit(linear, x_data, y_data, p0=[1,1])
            plt.plot(xfine, linear(xfine, *params), label='Fitted Line', color='red')
            y_ndata = linear(x_data, *params)
     
        if st.session_state.chart_type == "Exponential":
            try: 
                params, covariance = curve_fit(exponential, x_data, y_data, p0=[0,0,0])
                y_ndata = exponential(x_data, *params)
                
            except: 
                params, covariance = curve_fit(exponential, x_data, y_data, p0=[0,-1,0])
                y_ndata = exponential(x_data, *params)
                
            plt.plot(xfine, exponential(xfine, *params), label='Fitted Line', color='red')

        st.header(header_g)
        st.pyplot(fig)
        
        covariance = np.where(np.isinf(covariance), 0, covariance)
        
        coeff = params.tolist()
        
        for i, val in enumerate(coeff):
            coeff[i] = str(round(val,5))
        
        st.write(f"Coeffiecents are {", ".join(coeff)} (Disclaimer: coeffiecents are rounded up to 5 decimal places)")
        
        mean_aveErr = (sum(abs((y_data-y_ndata)/y_data))*100)/len(x_data)
        
        maxErr = max(abs((y_data-y_ndata)/y_data))*100
        
        minErr = min(abs((y_data-y_ndata)/y_data))*100
            
        st.write(f" Mean absolute percentage error is {round(mean_aveErr,2)}% (Disclaimer: percentages are rounded to at most two decimal places)")
        
        st.write(f" Absolute max percentage error is {round(maxErr,2)}% (Disclaimer: percentages are rounded to at most two decimal places)")
        
        st.write(f" Absolute min percentage error is {round(minErr,2)}% (Disclaimer: percentages are rounded to at most two decimal places)")
    
    except RuntimeError as e: 
        st.write("An error occurred during curve fitting, sample data might be too small or the chart type may not work with data set")

    except : 
        st.write("Data is not proper or there are not enough data points")

    
    