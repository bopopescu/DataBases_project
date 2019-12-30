import mainn
import pandas
from flask import render_template


mainn.cursor.execute(
        """select distinct doctors.name, doctors.number, diagnosis.name from doctors, diagnosis where
doctors.id_diag = diagnosis.id and doctors.id != (select password.id_user from password where password.user_pass = 'abvg111');""")
task1 = mainn.cursor.fetchall()
df = pandas.DataFrame(task1)
table = pandas.DataFrame.to_html(df)
