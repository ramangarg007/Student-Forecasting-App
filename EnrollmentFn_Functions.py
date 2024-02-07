# all the functions in one place
import pandas as pd
import numpy as np

def test_fn():
    return 'HELLO'


def required_data_format(df_is, semester_names, year_name):
    matrix_is = df_is.drop(['Term', 'FIN_AID_FED_RES'], axis=1).values
    final_data = []
    for semester in semester_names:
        sem_no = int(semester[-2:])
        # print(sem_no)

        row_data = []
        for year in year_name[::-1]:
            try:
                # print(year)
                temp_start_index = list(df_is['Term'].values).index(year)
                index_value = temp_start_index + (sem_no - 1)
                col_value = sem_no
                # print(index_value, col_value)
                # we are using -1 in the below equation because the indexing starts from 0, 1st sem is at index 0
                row_data.append(matrix_is[index_value, col_value-1])
            except:
                row_data.append(0)    
            # print('\n')
        final_data.append(row_data)


    required_df = pd.DataFrame(final_data, index=semester_names, columns=year_name[::-1])
    return required_df




def Cohort_Survival(required_df, number_of_semesters, year_name, sem_gap = 1):
    '''
    required_df -> the required transformed data for cohort survival calculation
    sem_gap(takes int(1) or int(2) as value) -> the number of semesters gap you want to use for the survival calculation, one gap implies 
    one semester back and two implies 1 year gap or two semesters gap

    the function returns two dictionaries, one for fall cohort and other for spring cohort 
    dictionary format -> {'Semester number': (average survial+1, average survial)}
    average survival denotes the amount of students lost or gained
    average survial + 1 denotes the ammount of students retained
    ''' 
    col_names = required_df.columns.astype(str).values
    fall_survival_dict = {}
    spring_survival_dict = {}

    # outer loop goes over the rows(semesters)
    # inner loop goe over the columns(years)

    for i in range(sem_gap, number_of_semesters):
        # print(i)
        avg_surviavl_fall = 0
        avg_surviavl_spring = 0
        count_fall = 0
        count_sprirng = 0

        for j in range(sem_gap, len(year_name)):
            if required_df.iloc[i-sem_gap,j-sem_gap] > 0:
                # cheking if the year is fall
                if col_names[j-sem_gap][-2:] == '10':
                    survival = (required_df.iloc[i,j] - required_df.iloc[i-sem_gap,j-sem_gap]) / required_df.iloc[i-sem_gap,j-sem_gap]
                    avg_surviavl_fall += survival
                    count_fall += 1

                # checking if the value is spring
                if col_names[j-sem_gap][-2:] == '30':
                    survival = (required_df.iloc[i,j] - required_df.iloc[i-sem_gap,j-sem_gap]) / required_df.iloc[i-sem_gap,j-sem_gap]
                    avg_surviavl_spring += survival
                    count_sprirng += 1
        # update in max part
        avg_surviavl_fall = avg_surviavl_fall/np.max((count_fall, 1))
        avg_surviavl_spring = avg_surviavl_spring/ np.max((count_sprirng, 1))   
        fall_survival_dict[i+1] = (avg_surviavl_fall+1, avg_surviavl_fall)
        spring_survival_dict[i+1] = (avg_surviavl_spring+1, avg_surviavl_spring)
    return (fall_survival_dict, spring_survival_dict)


# generating the required column value

def generate_column_names(required_df, years_to_predict):
    col_names = required_df.columns.astype(str).values
    last_col = col_names[-1]
    new_col_names = []

    if last_col[-2:] == '10':
        new_col_names.append(last_col[:2]+'30')
    for i in range(years_to_predict):
        last_col = int(last_col) + 100
        latest_col_prefix = str(last_col)[:2]
        # print(latest_col_prefix)
        new_col_names.append(latest_col_prefix + '10')
        new_col_names.append(latest_col_prefix + '30')
    return new_col_names  
# new_col_names = generate_column_names(required_df=required_df, years_to_predict=years_to_predict)


# regression for fall sem 1 prediction


def regression_prediction(required_df, new_col_names, sem_type='Fall'):
    '''
    Please note that the sem type takes either Fall or Spring
    '''
    from sklearn.linear_model import LinearRegression
    if sem_type == 'Fall':
        sem = '10'
    elif sem_type == 'Spring':
        sem = '30'
    else:
        print('Wrong input for sem_type')

    sem1_values = required_df.iloc[0].values
    col_names = required_df.columns.astype(str).values
    x = [int(col) for col in col_names if col[-2:]==sem]
    x = np.array(x).reshape(-1,1)

    y = [sem1_values[i] for i in range(len(col_names)) if col_names[i][-2:]==sem]
    y = np.array(y)


    query_years = np.array([int(col) for col in new_col_names if col[-2:]==sem]).reshape(-1,1)
    # print(query_years_fall)


    reg_model = LinearRegression()
    reg_model.fit(x,y)
    prediction_fall = np.round(reg_model.predict(query_years))

    return (prediction_fall, query_years)




# imputing the regression prediction in the 1st sem row

def imputing_first_row(required_df, new_col_names, first_row_dict, regression=True, user_input=False, user_dict=False):
    '''
    The function allows for two input method for the values of 1st semester
    1. Regression
    2. Manual Input

    Return: it will return the final df with the first row imputed.
    '''    
    if regression:
        final_df = required_df.rename(columns=str).copy()
        for col in new_col_names:
            final_df[col] = np.nan
            if col[-2:] == '10':
                final_df.loc['Semester 01', col] = int(fall_year_prediction[col])
            if col[-2:] == '30':
                final_df.loc['Semester 01', col] = int(spring_year_prediction[col])

        return final_df
    
    if user_input:
        # template for self input
        final_df = required_df.rename(columns=str).copy()
        for col in new_col_names:
            final_df[col] = np.nan
            val = input('Enter the value for year: {a}'.format(a=col))
            final_df.loc['Semester 01', col] = float(val)
        return final_df
    
    if user_dict:
        final_df = required_df.rename(columns=str).copy()
        for col in new_col_names:
            final_df[col] = np.nan
            val = first_row_dict[col][0]
            final_df.loc['Semester 01', col] = float(val)
        return final_df 



# one sem approach (trying to combine both the approaches in one function)


def final_forecast(required_df, final_df, fall_survival_dict_1sem, spring_survival_dict_1sem, fall_survival_dict_2sem, spring_survival_dict_2sem):
    new_col_start_ind = required_df.columns.shape[0]
    final_df_col_names = final_df.columns.values
    # print(new_col_start_ind)
    sem_gap = 2


    # consider calling survival calculation function here itself
    if sem_gap == 1:
        fall_survival_dict = fall_survival_dict_1sem
        spring_survival_dict = spring_survival_dict_1sem
    if sem_gap == 2:
        fall_survival_dict = fall_survival_dict_2sem
        spring_survival_dict = spring_survival_dict_2sem

    for row_idx in range(1, final_df.shape[0]):
        # print(row_idx)
        if row_idx < 2:
            for col_idx in range(new_col_start_ind, final_df.shape[1]):
                # print(final_df_col_names[col_idx])
                if final_df_col_names[col_idx-1][-2:] == '10':
                    final_df.iloc[row_idx, col_idx] = np.max((np.round(final_df.iloc[row_idx-1, col_idx-1] * fall_survival_dict_1sem[row_idx+1][0]),1))
                if final_df_col_names[col_idx-1][-2:] == '30':
                    final_df.iloc[row_idx, col_idx] = np.max((np.round(final_df.iloc[row_idx-1, col_idx-1] * spring_survival_dict_1sem[row_idx+1][0]),1))    
        if row_idx >= 2:
            for col_idx in range(new_col_start_ind, final_df.shape[1]):
                # print(final_df_col_names[col_idx])
                if final_df_col_names[col_idx-sem_gap][-2:] == '10':
                    final_df.iloc[row_idx, col_idx] = np.max((np.round(final_df.iloc[row_idx-sem_gap, col_idx-sem_gap] * fall_survival_dict[row_idx+1][0]), 1))
                if final_df_col_names[col_idx-sem_gap][-2:] == '30':
                    final_df.iloc[row_idx, col_idx] = np.max((np.round(final_df.iloc[row_idx-sem_gap, col_idx-sem_gap] * spring_survival_dict[row_idx+1][0]), 1))  
        # print(final_df.iloc[:6, :])
    return final_df



