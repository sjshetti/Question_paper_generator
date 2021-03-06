'''
GUI for generating question paper and solutions
Assumption- Column Names: qno, question_text, answers, paramaters, marks
The initial window allows the user to choose the database.
In the main window, the user can edit the content of the table.
The main window also has a menu at the top.
File > Open allows the user to open another database
File > New allows the user to open a new database
File > Save allows the user to save their progress in the current database
File > Save As allows the user to copy the current content into another new database
File > Exit allows the user to exit the application
Help > Instructions outlines the instructions for the user
The user can Add or Delete Rows
To generate a question paper, the user has to click on 'Generate' and select the questions
The user has the option to preview the question paper and solutions
The final documents can be output in Markdown, HTML, TeX and/or PDF format(s)
'''


#Importing all the necessary libraries
import PySimpleGUIQt as sg
import sqlite3
import json
import sys
from datetime import date
import random
from jinja2 import Template
import pypandoc
import os
from os.path import basename
from zipfile import ZipFile
import time
import QTApp



def readTableData():
    inputData = []   #Holds the data from the user interface
    duplicateQNo = False   #Tells if the qno field has duplicate values
    for i in range(MAX_ROWS):
        row = []
        for j in range(MAX_COL):  #Reads each row
            InputText=""
            for ch in values[(i,j)]:
                InputText+=str(ch)
                if InputText == 'None' or InputText == 0.0:
                    InputText = None
            if j==0:
                InputText=int(InputText)
            row.append(InputText)
        inputData.append(row)
    test_list = [ inputData[i][0] for i in range(MAX_ROWS)]
    flag = len(set(test_list)) == len(test_list)   #Checks for duplicate entries in qno field
    if not flag:
        sg.popup_ok('Please enter unique values for qno!')
        duplicateQNo = True
    json_list = [inputData[i][3] for i in range(MAX_ROWS)]
    json_string = "["
    for i in range(len(json_list)):
        json_string+=json_list[i]
        if json_list[i][-1]==']' and i != len(json_list)-1:
            json_string+=","
    json_string+="]"
    json_list = eval(json_string)   #Holds the parameters in a JSON array
    return inputData, json_list, duplicateQNo


sg.theme('Reddit')       #Theme for the GUI

#Initial layout for choosing database
layout1 = [[sg.Text('Source for database ', size=(15, 1)), sg.InputText(), sg.FileBrowse()],
      [sg.Submit(), sg.Cancel()],
      [sg.Button('New')]]

window1 = sg.Window('Choose the database', layout1)

event, values = window1.read()
window1.close()



if event == 'Submit':
    file_path = values[0]       # get the file path from the values dictionary
    conn = sqlite3.connect(file_path)   #Opens connection to the database
    cursor = conn.cursor()                   #To read data from the table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")     #Get the list of tables in the database
    tableName = cursor.fetchall()[0][0]     #The first table will be the one with questions
    window1.close()
    data = cursor.execute("SELECT * FROM %s" %tableName).fetchall()   #Data from the first table
    data=[list(i) for i in data]
    numColumns = 5                    #number of columns
    numRows = len(data)               #number of rows
    saveStatus = True                 #Status of the data of the table (Saved or Unsaved)
elif event == 'New':
    saveStatus = False
    data =[[1,'Enter Question', None, '[]', 0.0]]         #Default data
    numRows = 1
    numColumns = 5
    tableName = None     #None denotes that the table hasn't been actually saved yet
    conn = None
    cursor =None
    file_path = None
elif event == 'Cancel':
    sys.exit()

paramChosen = []  #Empty list to later hold the value of randomly chosen parameter
paramIndex = 0  #A global index to make sure that Solutions and Question Paper have the same parameter values

sg.set_options(element_padding=(0, 0))

menu_def = [['File', ['New','Open','Save', 'Save As','Exit']],
            #['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
            ['Help', 'Instructions'], ]

MAX_ROWS = numRows
MAX_COL = numColumns

#Layout of the table
columm_layout =  [[sg.Multiline(str(data[i][j]),size=(30, 6), pad=(
        1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
col_layout.extend(columm_layout)

#Layout of the table (main) window
layout = [[sg.Menu(menu_def)],[sg.Stretch()],
          [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
          [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
          [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]

if tableName is None:
    windowTitle = "Untitled"
else:
    windowTitle = tableName
if not saveStatus:
    windowTitle+=" (Unsaved Changes)"

window = sg.Window(windowTitle, layout, return_keyboard_events=True)

while True:    #MAIN EVENT LOOP
    event, values = window.read()


    if event in (sg.WIN_CLOSED, 'Exit'):   #Closes the progra,
        if event =='Exit':
            layout3=[[sg.Stretch(),sg.Text("All unsaved changes will be lost. Are you sure you want to quit?"),sg.Stretch()],[sg.Stretch(),sg.Button('Yes'),sg.Stretch(),sg.Button('No'),sg.Stretch()]]
            window3 = sg.Window('Exit',layout3,return_keyboard_events=True)
            event3, value3 = window3.read()
            if event3 =="No":
                window3.close()
                continue
        break
    elif event == 'New':        #Opens a new table
        saveStatus = False
        data =[[1,'Enter Question', None, '[]', 0.0]]
        numRows = 1
        numColumns = 5
        tableName = None
        MAX_ROWS = numRows
        MAX_COL = numColumns
        conn = None
        cursor = None
        columm_layout =  [[sg.Multiline(str(data[i][j]),size=(30, 6), pad=(
                1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
        col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
        col_layout.extend(columm_layout)

        #Layout of the table window
        layout = [[sg.Menu(menu_def)],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
                  [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]
        if tableName is None:
            windowTitle = "Untitled"
        else:
            windowTitle = tableName
        if not saveStatus:
            windowTitle+=" (Unsaved Changes)"
        window.close()
        window = sg.Window(windowTitle, layout, return_keyboard_events=True)

    elif event == 'Instructions':   #Provides instructions to the user
        sg.popup('''Instructions for use:\n
        To work with tables, import a database using File>Open or select a databse in the beginning.\n
        It is assumed that the database contains only one table.\n
        Further, it is assumed that the table contains columns named 'qno', 'question_text', 'answers', 'parameters' and 'marks'.\n
        qno is of type INTEGER, is the PRIMARY KEY and cannot be NULL.\n
        question_text is of type TEXT and cannot be NULL\n
        answers is of type TEXT (can be NULL)\n
        parameters is of type JSON\n
        marks is of type FLOAT\n
        While editing, if you want answers to be NULL, just type 'None' in the box. (without the quotes)\n
        If you leave the answers field blank, it won't be NULL.\n
        Similarly, if you want parameters to contain nothing, type '[]' in the box. (without the quotes)\n
        You CANNOT leave the parameters field blank and it MUST contain valid JSON objects/arrays.\n
        Before closing the application, make sure you click on 'Save' to save your progress. The program doesn't automatically save the contents in the database.\n
        After any action (like adding a row, deleting a row,etc), the original database won't be affected until and unless 'Save' is clicked.\n
        Before opening a new database (using 'Open'), press 'Save' if you want the contents to be saved in the original database. \n
        To generate the question paper, click on 'Generate' and choose the questions you want to include.\n
        Later, choose the output format and destination folder.\n
        The papers will be generated when the app returns to the main window (Table Viewer/Editor).\n
        Do NOT press anything while the papers are being generated. Let the app return to the main window on its own.
        ''')
    elif event == 'Delete row(s)': #Deletes row(s) from the table
        inputData , json_list, duplicateQNo = readTableData()   #Gives us the data from the table in the user interface
        if duplicateQNo:
            continue
        for i in range(MAX_ROWS):
            inputData[i][3]=json_list[i]
        columm_layout1 =  [[sg.Stretch(),sg.Checkbox(str(inputData[i][0]),key=(i,12)),sg.Stretch(), sg.Text(str(inputData[i][1]),size=(30, 6), pad=(
                1, 1), key=(i, 13)), sg.Stretch(),sg.Text(str(inputData[i][2]),size=(30, 6), pad=(
                        1, 1), key=(i, 14)),sg.Stretch(), sg.Text(str(inputData[i][3]),size=(30, 6), pad=(
                                1, 1), key=(i, 15)),sg.Stretch(), sg.Text(str(inputData[i][4]),size=(30, 6), pad=(
                                        1, 1), key=(i, 16)),sg.Stretch()] for i in range(MAX_ROWS)]
        col_layout1 = [[sg.Text('Question'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
        col_layout1.extend(columm_layout1)

        #Layout of the table window
        layout1 = [[sg.Stretch(),sg.Col(col_layout1, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                  [sg.Stretch(),sg.Checkbox('Select All', key='select_all'),sg.Stretch(), sg.Button('Delete'),sg.Stretch()] ]
        window4 = sg.Window('Delete Row(s)', layout1, return_keyboard_events = True)
        while True:
            event4, value4 = window4.read()
            if event4 == sg.WIN_CLOSED:   #If the "X" button is clicked
                break
            if event4 == 'Delete':
                window4.close()
                rowsToDelete=[]  #Holds the row numbers the user wants to delete
                if value4['select_all']:  #If "Select All" is selected
                    rowsToDelete = range(1,MAX_ROWS+1)
                else:
                    for i in range(MAX_ROWS):
                        if value4[(i,12)]:
                            rowsToDelete.append(i+1)
                if not rowsToDelete:  #If the list is empty
                    break
                MAX_ROWS=0
                for ele in inputData:
                    if ele[0] not in rowsToDelete:
                        MAX_ROWS+=1
                data = [ele for ele in inputData if ele[0] not in rowsToDelete]  #Keeps only that data which is undeleted
                saveStatus = False
                #Layout of the table
                columm_layout =  [[sg.Multiline(str(data[i][j]),size=(30, 6), pad=(
                        1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
                col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
                col_layout.extend(columm_layout)

                #Layout of the table window
                layout = [[sg.Menu(menu_def)],[sg.Stretch()],
                          [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
                          [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                          [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]
                if tableName is None:
                    windowTitle = "Untitled"
                else:
                    windowTitle = tableName
                if not saveStatus:
                    windowTitle+=" (Unsaved Changes)"
                window.close()
                window = sg.Window(windowTitle, layout, return_keyboard_events=True)
                break
            elif event4 == 'Cancel':
                window4.close()
                break

    elif event == 'Open':    #Opens a new database of questions and solutions
        file_name = sg.popup_get_file(
            'Choose the database to open', no_window=True)
        if file_name is not None:
            if conn is not None:
                conn.close()
            file_path=file_name
            conn = sqlite3.connect(file_path)   #Opens connection to the database
            cursor = conn.cursor()                   #To read data from the table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            try:
                tableName = cursor.fetchall()[0][0]
            except:
                continue
            try:
                    data = cursor.execute("SELECT * FROM %s" %tableName).fetchall()
                    data=[list(i) for i in data]
                    MAX_ROWS = len(data)
            except:
                    sg.popup_error('Error reading file')
                    continue
            # clear the table window
            window.close()

            #New layout with new data
            columm_layout =  [[sg.Multiline(str(data[i][j]),size=(30, 6), pad=(
                    1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
            col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
            col_layout.extend(columm_layout)
            saveStatus = True


            layout = [[sg.Menu(menu_def)],[sg.Stretch()],
                      [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
                      [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                      [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]
            if tableName is None:
                windowTitle = "Untitled"
            else:
                windowTitle = tableName
            if not saveStatus:
                windowTitle+=" (Unsaved Changes)"
            window.close()
            window = sg.Window(windowTitle, layout, return_keyboard_events=True)
        else:
            continue
    elif event=='Add row':   #Adds a row to the table
        data , json_list, duplicateQNo = readTableData()
        if duplicateQNo:
            continue

        for i in range(MAX_ROWS):
            data[i][3]=json_list[i]
        data.append([max([ele[0] for ele in data])+1,'Enter Question', None, '[]', 0.0])   #Append a default row
        columm_layout =  [[sg.Multiline(str(data[i][j]),size=(30, 6), pad=(
                1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS+1)]
        col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
        col_layout.extend(columm_layout)
        #Layout of the table window
        layout = [[sg.Menu(menu_def)],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
                  [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]
        window.close()
        saveStatus = False
        if tableName is None:
            windowTitle = "Untitled"
        else:
            windowTitle = tableName
        if not saveStatus:
            windowTitle+=" (Unsaved Changes)"
        window = sg.Window(windowTitle, layout, return_keyboard_events=True)
        MAX_ROWS+=1
    elif event=='Generate':   #Generates the question paper and solutions
        inputData , json_list, duplicateQNo = readTableData()
        if duplicateQNo:
            continue

        for i in range(MAX_ROWS):
            inputData[i][3]=json_list[i]
        columm_layout1 =  [[sg.Stretch(),sg.Checkbox(str(inputData[i][0]),key=(i,6)),sg.Stretch(), sg.Text(str(inputData[i][1]),size=(30, 6), pad=(
                1, 1), key=(i, 5)), sg.Stretch(),sg.Text(str(inputData[i][2]),size=(30, 6), pad=(
                        1, 1), key=(i, 11)),sg.Stretch(), sg.Text(str(inputData[i][3]),size=(30, 6), pad=(
                                1, 1), key=(i, 10)),sg.Stretch(), sg.Text(str(inputData[i][4]),size=(30, 6), pad=(
                                        1, 1), key=(i, 16)),sg.Stretch()] for i in range(MAX_ROWS)]
        col_layout1 = [[sg.Text('Question'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
        col_layout1.extend(columm_layout1)

        #Layout of the table window
        layout1 = [[sg.Stretch(),sg.Col(col_layout1, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                  [sg.Stretch(),sg.Checkbox('Select All', key='select_all'),sg.Stretch(), sg.Button('Generate'),sg.Stretch(), sg.Checkbox('Randomize Order', key='randomOrder'),sg.Stretch()] ]
        window1 = sg.Window('Generate Question Paper', layout1, return_keyboard_events = True)
        while True:
            event2, values2 = window1.read()
            if values2['select_all'] == True:  #If all questions are selected
                for i in range(MAX_ROWS):
                    window1[(i,6)].update(True)
            if event2 == sg.WIN_CLOSED:
                break
            if event2 == 'Generate':
                rows1 = []
                if not values2['select_all']:  #If "Select All" is not checked
                    for i in range(MAX_ROWS):
                        if values2[(i,6)]:
                            rows1.append(inputData[i])
                    if values2['randomOrder']:   #If user wishes to randomize the order of questions
                        rows1 = random.sample(rows1, len(rows1))
                    today = date.today()
                    d1 = today.strftime("%B %d, %Y")   #Date in "Month date, year" format
                    params = [ele[3] for ele in rows1]
                    rows = [ele[1] for ele in rows1]    #Question Text data from the table
                    marks = []    #Each question's marks
                    for ele in rows1:
                        if ele[4] is None:
                            marks.append(0.0)
                        else:
                            marks.append(float(ele[4]))
                    maxMarks = sum(marks)    #Total marks (Maximum scorable marks)
                    qpText = '''--- \n title: Question Paper (Maximum Marks - %s) \n author: Roll No.- \n date: %s \n--- \n \n# Questions \n<!--- Questions begin below. Do NOT edit the content below. To change the question content, please edit the table directly. To change the position of Maximum Marks, use only this expression: 'Maximum Marks -' -->\n''' %(maxMarks,d1)    #Question Paper text for creating html and md files
                    qpTextAlt = qpText    #Question Paper text for creating TeX and PDF files
                    j=1
                    for i in range(0,len(rows)):
                        if len(params[i])>0:                #If paramaters are available
                            paramChosen.append(random.choice(params[i]))    #Appends a randomly chosen parameter to the global paramChosen list
                            temp = Template(rows[i])               #Creates a template using jinja2. rows[0][0] is assumed to have placeholders for the parameters
                            qpText+= "\n%d. %s \n" %(j,temp.render(paramChosen[-1]))    #Replaces the placeholders with paramater values and writes into file
                            qpText+='<div style="text-align: right;"> [%s] </div>\n'%(marks[i])
                            qpTextAlt+= "\n%d. (%s marks) %s \n" %(j,marks[i],temp.render(paramChosen[-1]))

                        else:          #If there are no parameters available
                            qpText+="\n%d. %s \n" %(j,rows[i])
                            qpText+='<div style="text-align: right;"> [%s] </div>\n'%(marks[i])
                            qpTextAlt+="\n%d. (%s marks) %s \n" %(j, marks[i],rows[i])
                        j+=1
                    j=1
                    SolText = '''--- \n title: Solutions \n---\n'''    #Solution Text for creating the solution files
                    rows = [ele[2] for ele in rows1]   #Solution data from the table
                    for i in range(0,len(rows)):
                        if len(params[i])>0:    #If paramaters are available

                            if rows[i] and rows[i]!='':    #If the answers field in the table is not NULL or blank
                                temp = Template(rows[i])    #Creates a template using jinja2. rows[i][0] is assumed to have placeholders for the parameters
                                SolText+="\n%d. %s \n" %(j,temp.render(paramChosen[paramIndex]))    #Replaces the placeholders with paramater values and writes into file

                            else:     #If the answers field in the table is NULL or blank
                                SolText+="\n%d. %s \n" %(j,"Solution Not Available")
                            paramIndex+=1

                        else:    #If paramaters are not available

                            if rows[i] and rows[i]!='':
                                SolText+="\n%d. %s \n" %(j,rows[i])

                            else:
                                SolText+="\n%d. %s \n" %(j,"Solution Not Available")
                        j+=1
                    layout5=[[sg.Text('Make changes into the Question Paper and Solutions if you want (Markdown)')],
                    [sg.Multiline(qpText, key='qp'), sg.Multiline(SolText, key = 'sol')],
                    [sg.Stretch(),sg.Button('Preview Question Paper'),sg.Stretch(),sg.Button('Done'), sg.Stretch(),sg.Button('Preview Solutions'), sg.Stretch()]]
                    window5=sg.Window('Edit Question Paper and Solutions',layout5)
                    while True:
                        event5, values5 = window5.read()
                        if event5 == sg.WIN_CLOSED:
                            break
                        if event5 == 'Preview Question Paper': #Displays an HTML preview of the question paper
                            qpText = ''
                            for ch in values5['qp']:
                                qpText+=str(ch)
                            html = pypandoc.convert_text(qpText, 'html', format='md', extra_args=['-s'])
                            QTApp.showQP(html)
                        if event5 == 'Preview Solutions':  #Displays an HTML preview of the solutions
                            SolText = ''
                            for ch in values5['sol']:
                                SolText+=str(ch)
                            html = pypandoc.convert_text(SolText, 'html', format='md', extra_args=['-s'])
                            #win = sg.popup("Please Wait...")
                            QTApp.showQP(html)
                            #app.exec_()
                        if event5 == 'Done':   #Renders the documents in a zip file
                            qpText = ''
                            SolText = ''
                            for ch in values5['qp']:
                                qpText+=str(ch)
                            for ch in values5['sol']:
                                SolText+=str(ch)
                            layout6 = [[sg.Text('In which format do you want the question paper to be?')],
                            [sg.Stretch(), sg.Checkbox('Markdown', key=(0,7)), sg.Stretch(), sg.Checkbox('HTML', key=(1,7)), sg.Stretch(), sg.Checkbox('TeX', key=(2,7)), sg.Stretch(),sg.Checkbox('PDF', key=(3,7)), sg.Stretch()],
                            [sg.Text('In which format do you want the solutions to be?')],
                            [sg.Stretch(), sg.Checkbox('Markdown', key=(0,8)), sg.Stretch(), sg.Checkbox('HTML', key=(1,8)), sg.Stretch(), sg.Checkbox('TeX', key=(2,8)), sg.Stretch(),sg.Checkbox('PDF', key=(3,8)), sg.Stretch()],
                            [sg.Stretch(), sg.Button('Okay'), sg.Stretch()]]
                            window6 = sg.Window('Choose output format',layout6, return_keyboard_events=True)
                            while True:
                                event6, values6 = window6.read()
                                if event6 == sg.WIN_CLOSED:
                                    break
                                if event6 == 'Okay':
                                    window6.close()
                                    if not (values6[(0,7)] or values6[(1,7)] or values6[(2,7)] or values6[(3,7)] or values6[(0,8)] or values6[(1,8)] or values6[(2,8)] or values6[(3,8)]):
                                        break
                                    layout2 = [[
                                        sg.InputText(visible=False, enable_events=True, key='file_path'),
                                        sg.FileSaveAs(
                                            key='file_save',
                                            file_types=(('Zip File', '.zip'),),
                                        )
                                    ]]
                                    window2 = sg.Window('Select Output Destination', layout2)
                                    event2, values2 = window2.read()
                                    window2.close()
                                    if not values2['file_path'].split('.')[0]:
                                        break
                                    sg.popup_ok('Your files will be ready in a zip file once the Table window (main window) appears. Please do NOT press anything else till then. Press OK to continue.')
                                    if event2== 'file_path':
                                        OPfile_path = values2['file_path'].split('.')[0]

                                        extensions = ['md', 'html', 'tex', 'pdf']

                                        #Creating a few files to apply pypandoc and convert into other formats
                                        f = open(OPfile_path+'QP.md', 'wb')
                                        f.write(qpText.encode('utf8'))
                                        f.close()

                                        qpTextAlt = qpText.split('-->\n')[0]+'-->\n'+qpTextAlt.split('-->\n')[1]
                                        f = open(OPfile_path+'QPAlt.md', 'wb')
                                        f.write(qpTextAlt.encode('utf8'))
                                        f.close()

                                        f = open(OPfile_path+'Sol.md', 'wb')
                                        f.write(SolText.encode('utf8'))
                                        f.close()

                                        file_paths=[]
                                        for i in range(3):
                                            if values6[(i+1,7)]:
                                                try:
                                                    if i == 2 or i == 1:  #For PDF or TeX
                                                        pypandoc.convert_file(OPfile_path+'QPAlt.md',extensions[i+1] ,outputfile=OPfile_path+'QP.'+extensions[i+1],  extra_args=['-s'])
                                                    else:
                                                        pypandoc.convert_file(OPfile_path+'QP.md',extensions[i+1] ,outputfile=OPfile_path+'QP.'+extensions[i+1],  extra_args=['-s'])
                                                    file_paths.append(OPfile_path+'QP.'+extensions[i+1])
                                                except:
                                                    sg.popup('Couldn\'t generate a '+extensions[i+1]+' file. Check your pandoc or TeX installation' )
                                            if values6[(i+1,8)]:
                                                try:
                                                    pypandoc.convert_file(OPfile_path+'Sol.md',extensions[i+1] ,outputfile=OPfile_path+'Sol.'+extensions[i+1],  extra_args=['-s'])
                                                    file_paths.append(OPfile_path+'Sol.'+extensions[i+1])
                                                except:
                                                    sg.popup('Couldn\'t generate a '+extensions[i+1]+' file. Check your pandoc or TeX installation' )
                                        os.remove(OPfile_path+'QPAlt.md')
                                        if not values6[(0,7)]:
                                            os.remove(OPfile_path+'QP.md')
                                        else:
                                            file_paths.append(OPfile_path+'QP.md')
                                        if not values6[(0,8)]:
                                            os.remove(OPfile_path+'Sol.md')
                                        else:
                                            file_paths.append(OPfile_path+'Sol.md')
                                        with ZipFile(OPfile_path+'.zip','w') as zip:
                                            for file in file_paths:
                                                zip.write(file, basename(file))
                                                os.remove(file)
                                    break
                                    window2.close()

                            break
                    window5.close()

                else:  #If "Select All" is checked
                #Same as the previous case
                    for i in range(MAX_ROWS):
                            rows1.append(inputData[i])
                    if values2['randomOrder']:
                        rows1 = random.sample(rows1, len(rows1))
                    today = date.today()
                    d1 = today.strftime("%B %d, %Y")   #Date in "Month date, year" format
                    params = [ele[3] for ele in rows1]
                    rows = [ele[1] for ele in rows1]
                    marks = []
                    for ele in rows1:
                        if ele[4] is None:
                            marks.append(0.0)
                        else:
                            marks.append(float(ele[4]))
                    j=1
                    maxMarks = sum(marks)
                    qpText = '''--- \n title: Question Paper (Maximum Marks - %s) \n author: Roll No.- \n date: %s \n--- \n \n# Questions \n<!--- Questions begin below. Do NOT edit the content below. To change the question content, please edit the table directly. To change the position of Maximum Marks, use only this expression: 'Maximum Marks -' -->\n''' %(maxMarks,d1)
                    qpTextAlt = qpText
                    for i in range(0,len(rows)):
                        if len(params[i])>0:                #If paramaters are available
                            paramChosen.append(random.choice(params[i]))    #Appends a randomly chosen parameter to the global paramChosen list
                            temp = Template(rows[i])               #Creates a template using jinja2. rows[0][0] is assumed to have placeholders for the parameters
                            qpText+= "\n%d. %s \n" %(j,temp.render(paramChosen[-1]))    #Replaces the placeholders with paramater values and writes into file
                            qpText+='<div style="text-align: right;"> [%s] </div>\n'%(marks[i])
                            qpTextAlt+= "\n%d. (%s marks) %s \n" %(j,marks[i],temp.render(paramChosen[-1]))

                        else:          #If there are no parameters available
                            qpText+="\n%d. %s \n" %(j,rows[i])
                            qpText+='<div style="text-align: right;"> [%s] </div>\n'%(marks[i])
                            qpTextAlt+="\n%d. (%s marks) %s \n" %(j, marks[i],rows[i])
                        j+=1
                    j=1
                    SolText = '''--- \n title: Solutions \n---\n'''
                    rows = [ele[2] for ele in rows1]
                    for i in range(0,len(rows)):
                        if len(params[i])>0:    #If paramaters are available

                            if rows[i] and rows[i]!='':    #If the answers field in the table is not NULL or blank
                                temp = Template(rows[i])    #Creates a template using jinja2. rows[i][0] is assumed to have placeholders for the parameters
                                SolText+="\n%d. %s \n" %(j,temp.render(paramChosen[paramIndex]))    #Replaces the placeholders with paramater values and writes into file

                            else:     #If the answers field in the table is NULL or blank
                                SolText+="\n%d. %s \n" %(j,"Solution Not Available")
                            paramIndex+=1

                        else:    #If paramaters are not available

                            if rows[i] and rows[i]!='':
                                SolText+="\n%d. %s \n" %(j,rows[i])

                            else:
                                SolText+="\n%d. %s \n" %(j,"Solution Not Available")
                        j+=1
                    layout5=[[sg.Text('Make changes into the Question Paper and Solutions if you want (Markdown)')],
                    [sg.Multiline(qpText, key='qp'), sg.Multiline(SolText, key = 'sol')],
                    [sg.Stretch(),sg.Button('Preview Question Paper'),sg.Stretch(),sg.Button('Done'), sg.Stretch(),sg.Button('Preview Solutions'), sg.Stretch()]]
                    window5=sg.Window('Edit Question Paper and Solutions',layout5)
                    while True:
                        event5, values5 = window5.read()
                        if event5 == sg.WIN_CLOSED:
                            break
                        if event5 == 'Preview Question Paper':
                            qpText = ''
                            for ch in values5['qp']:
                                qpText+=str(ch)
                            html = pypandoc.convert_text(qpText, 'html', format='md', extra_args=['-s'])
                            QTApp.showQP(html)
                        if event5 == 'Preview Solutions':
                            SolText = ''
                            for ch in values5['sol']:
                                SolText+=str(ch)
                            html = pypandoc.convert_text(SolText, 'html', format='md', extra_args=['-s'])
                            QTApp.showQP(html)
                        if event5 == 'Done':
                            qpText = ''
                            SolText = ''
                            for ch in values5['qp']:
                                qpText+=str(ch)
                            for ch in values5['sol']:
                                SolText+=str(ch)
                            layout6 = [[sg.Text('In which format do you want the question paper to be?')],
                            [sg.Stretch(), sg.Checkbox('Markdown', key=(0,7)), sg.Stretch(), sg.Checkbox('HTML', key=(1,7)), sg.Stretch(), sg.Checkbox('TeX', key=(2,7)), sg.Stretch(),sg.Checkbox('PDF', key=(3,7)), sg.Stretch()],
                            [sg.Text('In which format do you want the solutions to be?')],
                            [sg.Stretch(), sg.Checkbox('Markdown', key=(0,8)), sg.Stretch(), sg.Checkbox('HTML', key=(1,8)), sg.Stretch(), sg.Checkbox('TeX', key=(2,8)), sg.Stretch(),sg.Checkbox('PDF', key=(3,8)), sg.Stretch()],
                            [sg.Stretch(), sg.Button('Okay'), sg.Stretch()]]
                            window6 = sg.Window('Choose output format',layout6, return_keyboard_events=True)
                            while True:
                                event6, values6 = window6.read()
                                if event6 == sg.WIN_CLOSED:
                                    break
                                if event6 == 'Okay':
                                    window6.close()
                                    if not (values6[(0,7)] or values6[(1,7)] or values6[(2,7)] or values6[(3,7)] or values6[(0,8)] or values6[(1,8)] or values6[(2,8)] or values6[(3,8)]):
                                        break
                                    layout2 = [[
                                        sg.InputText(visible=False, enable_events=True, key='file_path'),
                                        sg.FileSaveAs(
                                            key='file_save',
                                            file_types=(('Zip File', '.zip'),),
                                        )
                                    ]]
                                    window2 = sg.Window('Select Output Destination', layout2)
                                    event2, values2 = window2.read()
                                    window2.close()
                                    if not values2['file_path'].split('.')[0]:
                                        break
                                    sg.popup_ok('Your files will be ready in a zip file once the Table window (main window) appears. Please do NOT press anything else till then. Press OK to continue.')
                                    if event2== 'file_path':
                                        OPfile_path = values2['file_path'].split('.')[0]
                                        extensions = ['md', 'html', 'tex', 'pdf']

                                        f = open(OPfile_path+'QP.md', 'wb')
                                        f.write(qpText.encode('utf8'))
                                        f.close()

                                        qpTextAlt = qpText.split('-->\n')[0]+'-->\n'+qpTextAlt.split('-->\n')[1]
                                        f = open(OPfile_path+'QPAlt.md', 'wb')
                                        f.write(qpTextAlt.encode('utf8'))
                                        f.close()

                                        f = open(OPfile_path+'Sol.md', 'wb')
                                        f.write(SolText.encode('utf8'))
                                        f.close()

                                        file_paths=[]
                                        for i in range(3):
                                            if values6[(i+1,7)]:
                                                try:
                                                    if i == 2 or i == 1:  #For PDF or TeX
                                                        pypandoc.convert_file(OPfile_path+'QPAlt.md',extensions[i+1] ,outputfile=OPfile_path+'QP.'+extensions[i+1],  extra_args=['-s'])
                                                    else:
                                                        pypandoc.convert_file(OPfile_path+'QP.md',extensions[i+1] ,outputfile=OPfile_path+'QP.'+extensions[i+1],  extra_args=['-s'])
                                                    file_paths.append(OPfile_path+'QP.'+extensions[i+1])
                                                except:
                                                    sg.popup('Couldn\'t generate a '+extensions[i+1]+' file. Check your pandoc or TeX installation' )
                                            if values6[(i+1,8)]:
                                                try:
                                                    pypandoc.convert_file(OPfile_path+'Sol.md',extensions[i+1] ,outputfile=OPfile_path+'Sol.'+extensions[i+1],  extra_args=['-s'])
                                                    file_paths.append(OPfile_path+'Sol.'+extensions[i+1])
                                                except:
                                                    sg.popup('Couldn\'t generate a '+extensions[i+1]+' file. Check your pandoc or TeX installation' )
                                        os.remove(OPfile_path+'QPAlt.md')
                                        if not values6[(0,7)]:
                                            os.remove(OPfile_path+'QP.md')
                                        else:
                                            file_paths.append(OPfile_path+'QP.md')
                                        if not values6[(0,8)]:
                                            os.remove(OPfile_path+'Sol.md')
                                        else:
                                            file_paths.append(OPfile_path+'Sol.md')
                                        with ZipFile(OPfile_path+'.zip','w') as zip:
                                            for file in file_paths:
                                                zip.write(file, basename(file))
                                                os.remove(file)
                                    break
                                    window2.close()

                            break
                    window5.close()
                break
            if event2==sg.WIN_CLOSED:
                break
        window1.close()
        columm_layout =  [[sg.Multiline(str(inputData[i][j]),size=(30, 6), pad=(
                1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
        col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
        col_layout.extend(columm_layout)
        #Layout of the table window
        layout = [[sg.Menu(menu_def)],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
                  [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]
        window.close()
        saveStatus = False
        if tableName is None:
            windowTitle = "Untitled"
        else:
            windowTitle = tableName
        if not saveStatus:
            windowTitle+=" (Unsaved Changes)"
        window = sg.Window(windowTitle, layout, return_keyboard_events=True)

    elif event == 'Save':  #Saves the current contents of the table into the database
        inputData , json_list, duplicateQNo = readTableData()
        if duplicateQNo:
            continue

        for i in range(MAX_ROWS):
            inputData[i][3]=json_list[i]
        data = inputData
        try:
            if tableName is not None:
                cursor.execute("DELETE FROM "+ tableName)  #Clears the table in the database
                for i in range(MAX_ROWS):
                    sqlCommand = "INSERT INTO "+ tableName +" (qno, question_text, answers, parameters, marks) VALUES(?, ?, ?, ?, ?)"
                    params = (inputData[i][0], inputData[i][1], inputData[i][2], json.dumps(inputData[i][3]), inputData[i][4])
                    cursor.execute(sqlCommand,(inputData[i][0], inputData[i][1], inputData[i][2], json.dumps(inputData[i][3]), inputData[i][4]))#.format(tableName,inputData[i][0],inputData[i][1],inputData[i][2]))#,inputData[i][3]))
                    conn.commit()
            else:  #If the database doesn't exist i.e., this table is newly created
                layout2 = [[
                    sg.InputText(visible=False, enable_events=True, key='file_path'),
                    sg.FileSaveAs(
                        key='file_save',
                        file_types=(('Database (.db)', '.db'),),
                    )
                ]]
                window2 = sg.Window('', layout2)
                event2, values2 = window2.read()
                window2.close()
                if event2 == sg.WIN_CLOSED:
                    continue
                if event2 == 'file_path':
                    file_path = values2['file_path']
                    tableName = file_path.split('/')[-1]
                    if file_path[-3:] != ".db":
                        file_path = file_path+".db"
                    else:
                        tableName=tableName[:-3]
                    conn = sqlite3.connect(file_path)   #Opens connection to the database
                    cursor = conn.cursor()                   #To read data from the table

                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    try:
                        if tableName == cursor.fetchall()[0][0]:
                            cursor.execute("DELETE FROM "+ tableName)
                    except:
                        pass
                    cursor.execute("CREATE TABLE IF NOT EXISTS "+tableName+" ( qno INTEGER PRIMARY KEY, question_text TEXT NOT NULL, answers TEXT, parameters JSON, marks REAL);")
                    numColumns = 5
                    numRows = len(data)
                    MAX_ROWS = numRows
                    for i in range(MAX_ROWS):
                        sqlCommand = "INSERT INTO "+ tableName +" (qno, question_text, answers, parameters, marks) VALUES(?, ?, ?, ?, ?)"
                        params = (inputData[i][0], inputData[i][1], inputData[i][2], json.dumps(inputData[i][3]), inputData[i][4])
                        cursor.execute(sqlCommand,(inputData[i][0], inputData[i][1], inputData[i][2], json.dumps(inputData[i][3]), inputData[i][4]))#.format(tableName,inputData[i][0],inputData[i][1],inputData[i][2]))#,inputData[i][3]))
                        conn.commit()
            saveStatus = True
        except sqlite3.Error as e:
            sg.popup_ok('Couldn\'t Save. Please try again.')
            saveStatus = False
        columm_layout =  [[sg.Multiline(str(data[i][j]),size=(30, 6), pad=(
                1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
        col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
        col_layout.extend(columm_layout)

        #Layout of the table window
        layout = [[sg.Menu(menu_def)],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
                  [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]
        if tableName is None:
            windowTitle = "Untitled"
        else:
            windowTitle = tableName
        if not saveStatus:
            windowTitle+=" (Unsaved Changes)"
        window.close()
        window = sg.Window(windowTitle, layout, return_keyboard_events=True)

    elif event =='Save As':   #Saves the current contents of the table into a different database than the one opened currently
        #Same as the previous case
        inputData , json_list, duplicateQNo = readTableData()
        if duplicateQNo:
            continue

        for i in range(MAX_ROWS):
            inputData[i][3]=json_list[i]
        data = inputData
        try:
            layout2 = [[
                sg.InputText(visible=False, enable_events=True, key='file_path'),
                sg.FileSaveAs(
                    key='file_save',
                    file_types=(('Database (.db)', '.db'),),
                )
            ]]
            window2 = sg.Window('', layout2)
            event2, values2 = window2.read()
            window2.close()
            if event2 == sg.WIN_CLOSED:
                continue
            if event2 == 'file_path':
                file_path = values2['file_path']
                tableName = file_path.split('/')[-1]
                if file_path[-3:] != ".db":
                    file_path = file_path+".db"
                else:
                    tableName=tableName[:-3]
                conn = sqlite3.connect(file_path)   #Opens connection to the database
                cursor = conn.cursor()                   #To read data from the table

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                try:
                    if tableName == cursor.fetchall()[0][0]:
                        cursor.execute("DROP TABLE "+ tableName)
                except:
                    pass
                cursor.execute("CREATE TABLE IF NOT EXISTS "+tableName+" ( qno INTEGER PRIMARY KEY, question_text TEXT NOT NULL, answers TEXT, parameters JSON, marks REAL);")
                numColumns = 5
                numRows = len(data)
                MAX_ROWS = numRows
                for i in range(MAX_ROWS):
                    sqlCommand = "INSERT INTO "+ tableName +" (qno, question_text, answers, parameters, marks) VALUES(?, ?, ?, ?, ?)"
                    params = (inputData[i][0], inputData[i][1], inputData[i][2], json.dumps(inputData[i][3]), inputData[i][4])
                    cursor.execute(sqlCommand,(inputData[i][0], inputData[i][1], inputData[i][2], json.dumps(inputData[i][3]), inputData[i][4]))#.format(tableName,inputData[i][0],inputData[i][1],inputData[i][2]))#,inputData[i][3]))
                    conn.commit()
            saveStatus =True
        except sqlite3.Error as e:
            sg.popup_ok('Couldn\'t Save. Please check the entries!')
            saveStatus = False
        window.close()

        columm_layout =  [[sg.Multiline(str(data[i][j]),size=(30, 6), pad=(
                1, 1), key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
        col_layout = [[sg.Text('qno'),sg.Text('question_text'),sg.Text('answers'),sg.Text('parameters'), sg.Text('marks')]]
        col_layout.extend(columm_layout)


        layout = [[sg.Menu(menu_def)],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Save'),sg.Stretch(),sg.Text('Table of Questions and Solutions', font='Any 18'),sg.Stretch(),sg.Button('Exit'),sg.Stretch()],
                  [sg.Stretch(),sg.Col(col_layout, size=(1000,750),scrollable=True),sg.Stretch()],[sg.Stretch()],
                  [sg.Stretch(),sg.Button('Add row'),sg.Stretch(),sg.Button('Generate'),sg.Stretch(),sg.Button('Delete row(s)'),sg.Stretch()] ]
        windowTitle = tableName
        if tableName is None:
            windowTitle = "Untitled"
        else:
            windowTitle = tableName
        if not saveStatus:
            windowTitle+=" (Unsaved Changes)"

        window = sg.Window(windowTitle, layout, return_keyboard_events=True)
window.close()
