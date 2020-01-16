from flask import Flask
import psycopg2
from flask import render_template
import pandas
from flask import request
global password_global
password_global = ''

connection = psycopg2.connect(""" 
    host=
    port=
    dbname=hospital
    user=
    password=
    target_session_attrs= 
    """)


cursor = connection.cursor()
cursor.execute('SELECT  user_pass FROM password where dr_or_not = True;')
doctor_password = cursor.fetchall()
cursor.execute('SELECT user_pass FROM password where dr_or_not = False;')
patient_password = cursor.fetchall()

print(doctor_password)
print(patient_password)
# df = pandas.DataFrame(task1)
# table = pandas.DataFrame.to_html(df)
app = Flask(__name__)

def name_columns(data, keys):
    data.extend(keys)
    data.reverse()
    return data

@app.route('/doctor', methods=['POST', 'GET'])
def doctor():
   return render_template('index_doc.html', my_text='Введите пароль, доктор')


@app.route('/patient', methods=['POST', 'GET'])
def patient():
   return render_template('index_pat.html', my_text='Введите пароль, пациент')


@app.route('/doctor/search', methods=['POST', 'GET'])
def search():
    if bool(dict(request.form)):
        fio = request.form['fio']
        if fio == "":
            return render_template('doctor_search.html', text='введите фио')
        else:
            cursor.execute("""select distinct patients.name, patients.number, patients.adress from doctors, password, patients
               where patients.name = '""" + str(fio) + """' and patients.id_dr = (select password.id_user where password.user_pass = '""" + str(
                password_global) + """');""")
            task1 = cursor.fetchall()
            name_columns(task1, [('ФИО', 'Телефон', 'Адрес')])
            df = pandas.DataFrame(task1)
            table = pandas.DataFrame.to_html(df)
            cursor.execute(
                """select distinct observs.* from observs, password, patients where observs.id_dr = password.id_user and password.user_pass = '""" + str(
                password_global) + """' and patients.name = '""" + str(fio) + """' ;""")
            task2 = cursor.fetchall()
            name_columns(task1, [('ID', 'ID доктора', 'Жалобы', 'Анамнез')])
            df2 = pandas.DataFrame(task2)
            table1 = pandas.DataFrame.to_html(df2)
            return render_template('doc_page.html', user_name="", table=table, table1 = table1)
    else:
        return render_template('doctor_search.html')


@app.route('/doctor/password', methods=['POST', 'GET'])
def doctor_pass():
    password1 = request.form['password']
    x = (password1,)
    global password_global
    password_global = password1
    if x in doctor_password:
        cursor.execute("""select doctors.name from doctors, password where
                 doctors.id = 
                (select password.id_user where password.user_pass = '""" + str(password1) + """');""")
        user_name = str(cursor.fetchall()[0]).split()
        user_name.pop(0)
        user_name.pop(-1)
        cursor.execute("""select doctors.number from doctors, password where doctors.id = 
                        (select password.id_user where password.user_pass = '""" + str(password1) + """');""")
        number = str(cursor.fetchall()[0]).split()
        return render_template('doc_page.html', my_text='Вы авторизировались как врач. Ваши данные:', user_name = str(user_name), number = number )
    else:
        return  render_template('index.html', my_text='неверный пароль')


@app.route('/patient/password', methods=['POST', 'GET'])
def patient_pass():
    password1 = request.form['password']
    x = (password1,)
    global password_global
    password_global = password1
    if x in patient_password:
        cursor.execute("""select patients.name, patients.number, patients.adress from patients, password where
             patients.id = 
            (select password.id_user where password.user_pass = '""" + str(password1) + """');""")
        dannie = str(cursor.fetchall()[0]).split()
        return render_template('pat_page.html', my_text='Вы авторизировались как пациент. Вот ваши данные:', user_name = str(dannie))
    else:
        return render_template('index.html', my_text='неверный пароль')

@app.route('/doctor/info', methods=['POST', 'GET'])
def doc_info():
    cursor.execute("""select distinct patients.name, patients.number, patients.adress from doctors, password, patients
    where patients.id_dr = (select password.id_user where password.user_pass = '""" + str(password_global) + """');""")
    task1 = cursor.fetchall()
    name_columns(task1, [('ФИО', 'Телефон', 'Адрес')])
    df = pandas.DataFrame(task1)
    table = pandas.DataFrame.to_html(df)
    return render_template('doc_page.html', my_text='Вы авторизировались как врач', user_name = "", table = table)

@app.route('/doctor/add', methods=['POST', 'GET'])
def doc_add():
    cursor.execute("""select * from patients""")
    idi = len(cursor.fetchall())
    cursor.execute("""select doctors.id from doctors where doctors.id =(select password.id_user from password where password.user_pass ='""" +  str(password_global) +"""');""")
    doc_id = cursor.fetchall()[0][0]
    cursor.execute('select id_diag from patients where id_dr='+str(doc_id)+';')
    id_diag =cursor.fetchall()[0][0]
    if bool(dict(request.form)):
        if str(dict(request.form)['name1'][0]) != "":
            data = str(dict(request.form)['name1'][0]).split(',')
            name = data[0]
            number = data[1]
            adress = data[2::]
            adress = str(adress[0])+str(adress[1])+str(adress[2])
            cursor.execute("""insert into patients (id, id_dr, name, number, adress, id_diag) values ( '""" + str(int(idi)+1) + """', '""" +str(doc_id) + """', '""" + str(name) + """', '""" + str(number) + """', '""" + adress + """','""" +str(id_diag)+ """');""")
            cursor.execute('select id, name, number, adress from patients where id_dr = '+str(doc_id)+';')
            task1 = cursor.fetchall()
            name_columns(task1, [('ID','ФИО','Телефон', 'Адрес')])
            df = pandas.DataFrame(task1)
            table = pandas.DataFrame.to_html(df)
            user_pass = str('pass'+str(int(idi)+1))
            cursor.execute("""insert into password (id_user, dr_or_not, user_pass) values ('"""+ str(int(idi)+1) +"""',false,'"""+ user_pass +"""');""")
            connection.commit()
            return render_template('doc_add_pat.html',table = table)
        else:
            return render_template('doc_add_pat.html',title = 'введите данные')

    else:
        return render_template('doc_add_pat.html')


@app.route('/doctor/collegs', methods=['POST', 'GET'])
def get_collegs():
    cursor.execute(
        """select distinct doctors.name, doctors.number, diagnosis.name from doctors, diagnosis where
doctors.id_diag = diagnosis.id and doctors.id != (select password.id_user from password where password.user_pass ='""" + str(
            password_global) + """');""")
    task1 = cursor.fetchall()
    name_columns(task1, [('ФИО', 'Телефон', 'Специализация')])
    df = pandas.DataFrame(task1)
    table = pandas.DataFrame.to_html(df)
    return render_template('doctor_collegs.html', my_text='Информация о ваших коллегах', table = table)


@app.route('/patient/diag', methods=['POST', 'GET'])
def get_diagnosis():
    cursor.execute("""select diagnosis.* from diagnosis where diagnosis.id = (select patients.id_diag from patients where patients.id =( select password.id_user from password where password.user_pass = '""" + str(
            password_global) + """'));
""")
    task1 = cursor.fetchall()
    name_columns(task1, [('ID','Диагноз', 'Показания', 'Противопоказания')])
    df = pandas.DataFrame(task1)
    table = pandas.DataFrame.to_html(df)
    return render_template('pat_diag.html', table = table)


@app.route('/patient/info', methods=['POST', 'GET'])
def get_doctor():
    cursor.execute("""select doctors.name, doctors.number from doctors where doctors.id = (select patients.id_dr from patients, password where patients.id = password.id_user and password.user_pass = '""" + str(
            password_global) + """');""")
    task1 = cursor.fetchall()
    name_columns(task1, [('ФИО', 'Телефон')])
    df = pandas.DataFrame(task1)
    table = pandas.DataFrame.to_html(df)
    return render_template('pat_info.html', text='Информация о вашем лечащем враче', table= table)

@app.route('/patient/change', methods=['POST', 'GET'])
def change_info():
    if bool(dict(request.form)):
        if dict(request.form)['number']:
            num = str(dict(request.form)['number'][0])
        else:
            num = ""
        if dict(request.form)['adress']:
             adress = str(dict(request.form)['adress'][0])
        else:
             adress = ""
        if num == "" and adress != "":
            cursor.execute("""UPDATE patients SET adress = '""" + str(adress) + """' WHERE id = ( SELECT password.id_user FROM password WHERE password.user_pass = '""" + str(password_global) + """');""")
            cursor.execute("""select patients.name, patients.number, patients.adress from patients, password where patients.id = (select password.id_user where password.user_pass = '""" + str(password_global) + """');""")
            return render_template('pat_page.html', my_text='Ваши обновленные данные:', user_name = num+adress)
        if num != "" and adress == "":
            cursor.execute("""UPDATE patients SET number = '""" + str(num) + """' WHERE id = ( SELECT password.id_user FROM password WHERE password.user_pass = '""" + str(password_global) + """');""")
            cursor.execute("""select patients.name, patients.number, patients.adress from patients, password where patients.id = (select password.id_user where password.user_pass = '""" + str(password_global) + """');""")
            return render_template('pat_page.html', my_text='Ваши обновленные данные:', user_name = num+adress)
        if num != "" and adress != "":
            cursor.execute("""UPDATE patients SET number = '""" + str(num) + """' WHERE id = ( SELECT password.id_user FROM password WHERE password.user_pass = '""" + str(password_global) + """');""")
            cursor.execute("""UPDATE patients SET adress = '""" + str(
                adress) + """' WHERE id = ( SELECT password.id_user FROM password WHERE password.user_pass = '""" + str(
                password_global) + """');""")
            cursor.execute("""select patients.name, patients.number, patients.adress from patients, password where patients.id = (select password.id_user where password.user_pass = '""" + str(password_global) + """');""")
            return render_template('pat_page.html', my_text='Ваши обновленные данные:', user_name = num+adress)
        if num == "" and adress == "":
            return render_template('changig_info.html', my_text='Введите информацию для обновления')
    else:
         return render_template('changig_info.html', my_text='Введите информацию для обновления')


@app.route('/patient/observs', methods=['POST', 'GET'])
def obsrvs():
    cursor.execute("""select observs.* from observs, password where observs.id_pat = password.id_user and password.user_pass = '""" + str(password_global) + """';""")
    task1 = cursor.fetchall()
    name_columns(task1, [('ID', 'ID доктора', 'Жалобы', 'Анамнез')])
    df = pandas.DataFrame(task1)
    table = pandas.DataFrame.to_html(df)
    return render_template('pat_info.html', table = table)


@app.route('/doctor/observs', methods=['POST', 'GET'])
def set_obs():
    cursor.execute("""select * from patients""")
    idi = len(cursor.fetchall())
    cursor.execute("""select doctors.id from doctors where doctors.id =(select password.id_user from password where password.user_pass ='""" +  str(password_global) +"""');""")
    doc_id = cursor.fetchall()[0][0]
    cursor.execute('select id_diag from patients where id_dr='+str(doc_id)+';')
    if bool(dict(request.form)):
        info = request.form['info']
        if info == "":
            return render_template('doctor_set_obs.html', my_text='введите информацию')
        else:
            data = str(dict(request.form)['info'][0]).split(';')
            pat_id = data[0]
            compls = data[1]
            anamnez = data[2]
            cursor.execute("""insert into observs (id_pat, id_dr, complains, anamnez) values ( '""" + str((pat_id)) + """', '""" + str(doc_id) + """', '""" + str(compls) + """', '""" + str(
                anamnez) + """');""")
            cursor.execute("""select observs.* from observs, password where password.user_pass = '""" +  str(password_global) +"""' and password.id_user = observs.id_dr;""")
            task1 = cursor.fetchall()
            name_columns(task1, [('ID', 'ID доктора', 'Жалобы', 'Анамнез')])
            df = pandas.DataFrame(task1)
            table = pandas.DataFrame.to_html(df)
            connection.commit()
            return render_template('pat_info.html',text = str(data), table = table)
    else:
        return render_template('doctor_set_obs.html')

@app.route('/doctor/delete', methods=['POST', 'GET'])
def delete():
    if bool(dict(request.form)):
        cursor.execute(
    """select doctors.id from doctors where doctors.id =(select password.id_user from password where password.user_pass ='""" + str(
        password_global) + """');""")
        doc_id = cursor.fetchall()[0][0]
        fio = request.form['fio']
        if fio == "":
            return render_template('doc_del.html', text='введите фио')
        else:
            cursor.execute("""select id from patients where name='""" + str(fio) + """';""")
            id_pat = cursor.fetchall()[0][0]
            cursor.execute("""delete from  patients where patients.name = '""" + str(
                fio) + """' and patients.id_dr = (select password.id_user from password where password.user_pass = '""" + str(
                password_global) + """');""")
            cursor.execute("""delete from  password where password.id_user = '""" + str(id_pat) + """' ;""")
            cursor.execute("""delete from  observs where password.id_user = '""" + str(id_pat) + """' ;""")
            cursor.execute("""select distinct patients.name, patients.number, patients.adress from doctors, password, patients
                    where patients.id_dr = '""" + str(doc_id) + """' ;""")
            task1 = cursor.fetchall()
            name_columns(task1, [('ФИО', 'Телефон', 'Адрес')])
            df = pandas.DataFrame(task1)
            table = pandas.DataFrame.to_html(df)
            connection.commit()
            return render_template('doc_page.html', my_text='Ваши пациенты', user_name="", table=table)
    else:
        return render_template('doc_del.html')



@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html', my_text='Добро пожаловать в нашу больницу')

if __name__ == "__main__":
    app.run()

