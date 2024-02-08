# Student-Forecasting-App

![image](https://github.com/ramangarg007/Student-Forecasting-App/assets/15136599/4a563651-314b-4e1c-aa50-447ed124a991)

Application URL: https://student-forecasting-app-umass.streamlit.app/

The "Student Forecasting UMB" application is designed to provide insights into student enrollment trends and forecast future enrollment numbers based on user-defined parameters. This application leverages Streamlit, a powerful tool for creating interactive web applications with Python, along with pandas for data manipulation.

Upon launching the application, users are greeted with a main page displaying the title "Student Forecasting UMB" and a sidebar containing various forecast parameters. These parameters include the start and end years for survival studies, the number of semesters, the years to predict, and the student type based on available data.

Users have the option to upload their own data file or utilize a default dataset provided within the application. Once the data is loaded, the user input section displays the chosen parameters for review.

The application then processes the input data, generating the required DataFrame for analysis. It calculates survival rates based on cohort data and performs regression predictions to forecast enrollment numbers for the specified years.

Finally, the application presents the forecasted DataFrame, allowing users to download the data as a CSV file for further analysis and reporting. This application serves as a valuable tool for educational institutions and researchers seeking to understand and anticipate student enrollment patterns.




