import streamlit as st
import pandas as pd
import numpy as np
import EnrollmentFn_Functions as ef


# title for main page and sidebar
st.title('Student Forecasing UMB')
st.sidebar.header('Forecast Parameters')

# st.subheader('Input DataFrame')
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("filename:", uploaded_file.name)

else:
    df = pd.read_csv('./Roster2.csv')
# st.write(df[:5])

# start year placed in side bar
start_year = int(st.sidebar.text_input('Start Year for survival study', '2710'))
# st.write('Start Year', start_year)

# end year placed in side bar
end_year = int(st.sidebar.text_input('End Year for survival study', '3230'))
# st.write('End Year', end_year)

# number of semesters
number_of_semesters = int(st.sidebar.text_input('Number of Semester', '14'))
# st.write('Number of Semesters', number_of_semesters)


# years to predict
years_to_predict = int(st.sidebar.text_input('Years to predict', '5'))
# st.write('Years to Predict', years_to_predict)

# # regression parameter
# student_type = st.sidebar.radio(
#         "Student Type",
#         ('UserInput' 'Regression')
#     )

# regression_var = 
# user_dict_va = 


# Student type
available_student_types = tuple(df['FIN_AID_FED_RES'].unique())
student_type = st.sidebar.radio(
        "Student Type",
        available_student_types
    )

# st.write(student_type)


user_input_df = pd.DataFrame({
            'Start Year': [start_year],
            'End Year': [end_year],
            'Number of Semester': [number_of_semesters],
            'Years to Predict': [years_to_predict],
            'Student Type': [student_type]

})

st.subheader('User Input')
st.write(user_input_df)


# # first year input test
# temp_dict = {
#     '3310': [2870],
#     '3330': [4799],
#     '3410': [2785],
#     '3430': [4579],
#     '3510': [2753],
#     '3530': [2342],
#     '3610': [2342],
#     '3630': [4435],
#     '3710': [4566],
#     '3730': [3242]}
# temp_df = pd.DataFrame(temp_dict)
# edited_df = st.sidebar.experimental_data_editor(temp_df)

# st.write(dict(zip(edited_df.columns, edited_df.values[0])))





# not a control variable:
forward_year_window = 1
df_is = df[df['FIN_AID_FED_RES'] == student_type]

# generating the matrix to work with
matrix_is = df_is.drop(['Term', 'FIN_AID_FED_RES'], axis=1).values

# generating index values for our year names 
try:
    start_year_index = list(df_is['Term'].values).index(start_year)
    end_year_index = list(df_is['Term'].values).index(end_year)
except:
    print('Year not available in the data')


# generating columns and rows for required data format
semester_names = ['Semester 0{num}'.format(num=i+1) if (i+1)<10 else 'Semester {num}'.format(num=i+1) for i in range(number_of_semesters)]
year_name = list(df_is['Term'].values[end_year_index: start_year_index+1])


# required Data Frame
# st.subheader('Required DataFrame for the study')
required_df = ef.required_data_format(df_is=df_is, semester_names=semester_names, year_name=year_name)
# st.write(required_df)


st.subheader('First Row values')
new_col_names = ef.generate_column_names(required_df=required_df, years_to_predict=years_to_predict)

# ------- test code block start -------- 
prediction_fall, query_years_fall = ef.regression_prediction(required_df, new_col_names, sem_type='Fall')
prediction_spring, query_years_spring = ef.regression_prediction(required_df, new_col_names, sem_type='Spring')

fall_year_prediction =  dict(zip(query_years_fall.flatten().astype(str), prediction_fall))
spring_year_prediction =  dict(zip(query_years_spring.flatten().astype(str), prediction_spring))

temp_dict = {}
for col in new_col_names:
    if col[-2:] == '10':
        temp_dict[str(col)] = [int(fall_year_prediction[col])]
    if col[-2:] == '30':
        temp_dict[str(col)] = [int(spring_year_prediction[col])]


# ------- test code block end -------

# temp_dict = {key:[value] for key,value in  zip(new_col_names, range(len(new_col_names)))}
temp_df = pd.DataFrame(temp_dict)
# this is the code showing first row df
edited_df = st.experimental_data_editor(temp_df)
first_row_dict = {key:[float(value)] for key,value in  zip(edited_df.columns, edited_df.values[0])}


st.subheader('Required DataFrame for the study')
st.write(required_df)




# final flow section
final_forecast_df = required_df.copy()

for i in range(years_to_predict):
        
    # survival calculation
    fall_survival_dict_1sem, spring_survival_dict_1sem = ef.Cohort_Survival(required_df, number_of_semesters, year_name, sem_gap=1)
    fall_survival_dict_2sem, spring_survival_dict_2sem = ef.Cohort_Survival(required_df, number_of_semesters, year_name, sem_gap=2)

    # generating new col names
    new_col_names = ef.generate_column_names(required_df=required_df, years_to_predict=forward_year_window)

    # regression prediction and zipping query years and predictions
    prediction_fall, query_years_fall = ef.regression_prediction(required_df, new_col_names, sem_type='Fall')
    prediction_spring, query_years_spring = ef.regression_prediction(required_df, new_col_names, sem_type='Spring')

    fall_year_prediction =  dict(zip(query_years_fall.flatten().astype(str), prediction_fall))
    spring_year_prediction =  dict(zip(query_years_spring.flatten().astype(str), prediction_spring))

    # creating final df and imputing the first row with regression
    final_df = ef.imputing_first_row(required_df, new_col_names, first_row_dict, regression=False, user_input=False, user_dict=True)

    # final forecast function
    final_df = ef.final_forecast(required_df, final_df, fall_survival_dict_1sem, spring_survival_dict_1sem, fall_survival_dict_2sem, spring_survival_dict_2sem)

    final_forecast_df = pd.concat((final_forecast_df, final_df.iloc[:,-2:]), axis=1)
    
    # generating new required df and calculating new survival
    new_start_idx = str(int(final_df.columns[-2]) - 5*100)
    required_df = final_df.loc[:, new_start_idx:]



st.subheader('Final Forecasted DataFrame')
st.write(final_forecast_df)


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(final_forecast_df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='FinalForecast.csv',
    mime='text/csv',
)

