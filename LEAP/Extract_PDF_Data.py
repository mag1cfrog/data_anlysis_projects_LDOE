import os
import pandas as pd
import re
import time
import fitz
import winsound
import concurrent.futures
from tqdm import tqdm
import cProfile
import traceback
import numpy as np
from process_file2 import process_file, process_file_wrapper
from multiprocessing import Pool, cpu_count
from multiprocessing import Value
from multiprocessing import Manager, Queue
from pdfrw import PdfReader, PdfWriter




def combine_pdfs(Directory, Subjects_in_Headlines, Report_Type):
    
    start_time = time.time()
    
    # Get a list of all the PDF files in the directory
    pdf_files = [f for f in os.listdir(Directory) if f.endswith('.pdf') and any(Subject in f for Subject in Subjects_in_Headlines) and Report_Type in f]

    # Create a new PDF writer object
    writer = PdfWriter()

    # Iterate over the PDF files
    for filename in tqdm(pdf_files, desc="Combining PDFs"):
        # Open the PDF file
        reader = PdfReader(os.path.join(Directory, filename))
       
        # Append the pages to the new PDF file
        writer.addpages(reader.pages)

    # Create the cache directory if it doesn't exist
    os.makedirs(os.path.join(Directory, 'cache'), exist_ok=True)

    # Save the new PDF file
    writer.write(os.path.join(Directory, 'cache', 'combined.pdf'))
    
    # Get the end time
    end_time = time.time()

    # Print the running time
    print(f"Running time: {end_time - start_time} seconds")





if __name__ == "__main__":

    # specify the directory where the PDF files are stored
    Directory = r'E:\testing\pdf'

    # Initialize an empty DataFrame
    Variable_List = ['If_Voided', 'Report_Title', 'Report_Subject', 'Report_Type', 'Report_Year','Report_Season',
                    'Report_Date', 'Student_Name', 'LASID', 'DoB', 'Grade', 'School', 'School_System', 'Overview',
                    'State_Average_Score', 'State_Average_Level',  'State_Average_Achievement_Level',
                    'Student_Performance_Score', 'Student_Performance_Level', 'Student_Performance_Achievement_Level',
                    'School_System_Average_Score', 'School_System_Average_Level', 'School_System_Average_Achievement_Level',
                    'Overall_Student_Performance']


    # Coordinate Dictionary
    C_dict = {
        'If_Voided': (100.99799346923828, 240.17391967773438, 364.7249450683594, 304.9959716796875),
        'Report_Title_Section':(268.41949462890625, 24.466045379638672, 388.220458984375, 60.76609420776367),
        'Report_Title': (299.8905029296875, 24.466045379638672, 356.7494812011719, 35.46604537963867), 
        'Report_Subject': (307.530029296875, 37.11606979370117, 349.1100158691406, 48.11606979370117),
        'Report_Time':(297.1405029296875, 49.76609420776367, 359.4995422363281, 60.76609420776367),
        'Personal_Information': (36.0, 81.936432, 555.31427, 119.298805),
        'Overview': (36.0, 154.26290893554688, 573.7233276367188, 217.44131469726562),
        'Student_Performance_Score': (99.5, 272.1, 134.5139923095703, 304.9959716796875),
        'School_System_Average_Score': (437.9, 272.0903015136719, 472.9139709472656, 304.9959716796875),
        'State_Average_Score': (534.4, 272.0903015136719, 569.39404296875, 304.9959716796875),
        'Student_Performance_Level': (48.6, 276.0442199707031, 77.60700225830078, 306.5198974609375),
        'School_System_Average_Level': (392.8, 276.0442199707031, 421.7669982910156, 306.5198974609375),
        'State_Average_Level': (489.24, 276.0442199707031, 518.2470092773438, 306.5198974609375),
        'Overall_Student_Performance': (159.12, 240.17391967773438, 373.2570495605469, 311.8724365234375),
        'Achievement_Levels':(48.5, 313.1333312988281, 541.7593994140625, 332.9332275390625),
        'Achievement_Levels_Fixed':(48.5, 313.1333312988281, 561.5098876953125, 332.9332275390625),
        'Student_Achievement_Level':(48.5, 313.1333312988281, 138.4506072998047, 332.9332275390625),
        'School_System_Average_Achievement_Level':(431.37921142578125, 313.1333312988281, 475.8841552734375, 332.9332275390625),
        'State_Average_Achievement_Level':(522.6917724609375, 313.1333312988281, 567.1967163085938, 332.9332275390625),
        'State_Average_Achievement_Level_Fixed':(480, 313.1333312988281, 567.1967163085938, 332.9332275390625),
        'Investigate_Level': (47.3, 361.6931457519531, 109.95957946777344, 377.6131591796875),
        'Investigate_Rating': (121.3, 349.7764587402344, 565.6683959960938, 386.82415771484375),
        'Evaluate_Level': (47.3, 411.753173828125, 109.95957946777344, 427.6731872558594),
        'Evaluate_Level_Fixed':(47.3, 398, 109.9595718383789, 440.3182067871094),
        'Evaluate_Rating':(121.3, 399.83648681640625, 575.6884765625, 454.1341857910156),
        'Reason_Scientifically_Level': (47.3, 474.4582214355469, 109.95957946777344, 490.37823486328125),
        'Reason_Scientifically_Level_Fixed':(47.3, 468, 109.95957946777344, 521),
        'Reason_Scientifically_Rating': (121.3, 462.5415344238281, 572.3583984375, 499.5892333984375),
        'Percent_Achievement_Level_Advanced': (90.60675048828125, 669.9880981445312, 551.4429321289062, 678.0706176757812),
        'Percent_Achievement_Level_Mastery': (90.60675048828125, 683.6680908203125, 553.6669311523438, 691.6680908203125),
        'Percent_Achievement_Level_Basic': (90.60675048828125, 697.3480834960938, 553.6669311523438, 705.3480834960938),
        'Percent_Achievement_Level_Approaching_Basic': (90.60675048828125, 711.028076171875, 553.6669311523438, 719.028076171875),
        'Percent_Achievement_Level_Unsatisfactory': (90.60675048828125, 724.7080688476562, 553.6669311523438, 732.7080688476562),
        'Reading_Performance_Achievement_Level':(39.1879997253418, 387.57275390625, 94.01200103759766, 402.62274169921875),
        'Literary_Text_Achievement_Level':(39.57841873168945, 431.7209777832031, 94.40242004394531, 461.5955810546875),
        'Informational_Text_Achievement_Level':(39.57841491699219, 486.1009826660156, 94.40241241455078, 515.9755859375),
        'Vocabulary_Achievement_Level':(39.57841491699219, 540.4810180664062, 94.40241241455078, 570.3556518554688),
        'Reading_Performance_Achievement_Level_State_Percentages':(128.6118927001953, 407.6592102050781, 276.72808837890625, 417.1592102050781),
        'Writing_Performance_Achievement_Level':(317.1080017089844, 373.46807861328125, 371.9320373535156, 403.34271240234375),
        'Writing_Performance_Achievement_Level_State_Percentages':(404.37164306640625, 409.0992126464844, 552.4866943359375, 418.5992126464844),
        'Written_Expression_Achievement_Level':(317.33111572265625, 431.72100830078125, 372.15509033203125, 461.5956115722656),
        'Knowledge&Use_of_Language_Conventions':(317.33111572265625, 486.1009826660156, 372.15509033203125, 515.9755859375)
    }


    VS = pd.Series(Variable_List)

    Subjects_in_Headlines = ['ELA']


    Report_Type = 'StudentReport'
    
    start_time = time.time()

    combine_pdfs(Directory, Subjects_in_Headlines, Report_Type)

    filename = "cache/combined.pdf"
    filename = os.path.join(Directory, filename)

    doc = fitz.open(filename)
    total_pages = len(doc)
    cpu = min(cpu_count(),total_pages)
    # Close the PDF
    doc.close()
    # make vectors of arguments for the processes
    vectors = [(i, cpu, filename, C_dict) for i in range(cpu)]
    print("Starting %i processes for '%s'." % (cpu, filename))

    # Create a manager object
    manager = Manager()

    # Create a shared variable for the counter
    counter = manager.Value('i', 0)

    # Create a progress bar
    with Pool() as pool:
        results = []
        for result in pool.imap_unordered(process_file_wrapper, [(vector, counter) for vector in vectors]):
            results.append(result)
    
    
    # Convert the results into a DataFrame
    flat_results = [item for sublist in results for item in sublist]
    df2 = pd.DataFrame(flat_results)

    

    #Regulate the data in school column
    df2['Student_Name'] = df2['Student_Name'].str.strip()
    df2['School'] = df2['School'].str.strip()
    df2['Grade'] = df2['Grade'].str.strip()
    df2['LASID'] = df2['LASID'].str.strip()
    df2['School'] = df2['School'].str.strip()
    df2['School_System'] = df2['School_System'].str.strip()
    df2['DoB'] = df2['DoB'].str.strip()
    df2['Reading_Performance_Achievement_Level'] = df2['Reading_Performance_Achievement_Level'].str.replace('\n', ' ')
    df2['Literary_Text_Achievement_Level'] = df2['Literary_Text_Achievement_Level'].str.replace('«««', '').str.replace('\n', ' ')
    df2['Informational_Text_Achievement_Level'] = df2['Informational_Text_Achievement_Level'].str.replace('«««', '').str.replace('\n', ' ')
    df2['Vocabulary_Achievement_Level'] = df2['Vocabulary_Achievement_Level'].str.replace('«««', '').str.replace('\n', ' ')
    df2[['Reading_Performance_Achievement_Level_State_Percentage_Strong', 
        'Reading_Performance_Achievement_Level_State_Percentage_Moderate', 
        'Reading_Performance_Achievement_Level_State_Percentage_Weak']] = df2['Reading_Performance_Achievement_Level_State_Percentages'].str.strip().str.split('\n', expand=True)
    df2['Writing_Performance_Achievement_Level'] = df2['Writing_Performance_Achievement_Level'].str.replace('«««', '').str.replace('\n', ' ')
    df2[['Writing_Performance_Achievement_Level_State_Percentage_Strong', 
        'Writing_Performance_Achievement_Level_State_Percentage_Moderate', 
        'Writing_Performance_Achievement_Level_State_Percentage_Weak']] = df2['Writing_Performance_Achievement_Level_State_Percentages'].str.strip().str.split('\n', expand=True)
    df2['Written_Expression_Achievement_Level'] = df2['Written_Expression_Achievement_Level'].str.replace('«««', '').str.replace('\n', ' ')
    df2['Knowledge&Use_of_Language_Conventions'] = df2['Knowledge&Use_of_Language_Conventions'].str.replace('«««', '').str.replace('\n', ' ')
    report_subjects = []

    report_subjects = list(df2['Report_Subject'].unique())

#    if len(report_subjects) == 1:
#        subject = report_subjects[0]

#    if subject == 'English Language Arts':
#        subject = 'ELA'
    subject = 'ELA'

    # Split the 'Student_Name' column into two new columns
    df2[['Student_First_Name', 'Rest']] = df2['Student_Name'].str.split(' ', n=1, expand=True)

    # Check if 'Rest' contains a space
    contains_space = df2['Rest'].str.contains(' ')

    # If 'Rest' contains a space, split it into 'Middle_Initial' and 'Last_Name'
    df2.loc[contains_space, ['Student_Middle_Initial', 'Student_Last_Name']] = df2.loc[contains_space, 'Rest'].str.split(' ', n=1, expand=True)

    # If 'Rest' doesn't contain a space, it only contains the last name
    df2.loc[~contains_space, 'Student_Last_Name'] = df2.loc[~contains_space, 'Rest']
    df2.loc[~contains_space, 'Student_Middle_Initial'] = np.nan

    # Now you can drop the 'Rest' column as it's no longer needed
    df2 = df2.drop(columns='Rest')

    # Replace '--/--/----' with np.nan
    df2['DoB'] = df2['DoB'].replace('--/--/----', np.nan)

    # Convert the 'DoB' column to datetime format
    df2['DoB'] = pd.to_datetime(df2['DoB'], errors='coerce')

    # Create new columns for the day, month, and year
    df2['Summarized_DOB_Day'] = df2['DoB'].dt.day
    df2['Summarized_DOB_Month'] = df2['DoB'].dt.month
    df2['Summarized_DOB_Year'] = df2['DoB'].dt.year

    # Now you can drop the 'DoB' column as it's no longer needed
    df2 = df2.drop(columns='DoB')

    # Split the 'School' column into two new columns 'School_Code' and 'School_Name'
    df2[['School_Code', 'School_Name']] = df2['School'].str.split(' ', n=1, expand=True)
    df2 = df2.drop(columns='School')


    df2[['School_System_Code', 'School_System_Name']] = df2['School_System'].str.split(' ', n=1, expand=True)
    df2 = df2.drop(columns=['School_System', 'Reading_Performance_Achievement_Level_State_Percentages', 'Writing_Performance_Achievement_Level_State_Percentages'])

    df2 = df2.rename(columns={'Grade': 'Summarized_Grade'})
    df2 = df2.rename(columns={'Student_Performance_Score': f'Scale_Score_-_{subject}'})

    df2.to_parquet('E:/testing/Output/Report_Readin_2023_ELA.parquet')

    df2.to_csv('E:/testing/Output/Report_Readin_2023_ELA.csv')

    def delete_file(filepath):
        # Check if the file exists
        if os.path.exists(filepath):
            # Delete the file
            os.remove(filepath)
            print(f"File {filepath} has been deleted.")
        else:
            print(f"File {filepath} does not exist.")



    # specify the file to be deleted
    filepath = os.path.join(Directory, 'cache', 'combined.pdf')

    delete_file(filepath)

    end_time = time.time()
    # Print the running time
    print(f"Total running time: {end_time - start_time} seconds")
    

