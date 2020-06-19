import sys
import os
from PyQt5 import QtWidgets
import app_interface
import patent_processor as pp
import pymysql
import feature_extractor
import ontology
from datetime import datetime
import time
#from lxml import etree
connection = pymysql.connect(host='localhost',
                             user='user',
                             password='123456',
                             db='ontology_builder',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

class App(QtWidgets.QMainWindow, app_interface.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.saoTable.resizeColumnsToContents()
        self.loadPatentsBtn.clicked.connect(self.load_patents)
        self.loadPatentBtn.clicked.connect(self.load_patent)
        self.extractSaoBtn.clicked.connect(self.extract_sao)
        self.buildOntologyBtn.clicked.connect(self.build_ontology)
        self.buildPatentsOntologyBtn.clicked.connect(self.build_patents_ontology)
        self.init_patent_list()
        self.patentsList.itemClicked.connect(self.show_patent)

    def init_patent_list(self):
        self.patentsList.clear()
        cursor = connection.cursor()
        cursor.execute("select patent_name from patents")
        patents = cursor.fetchall()
        if patents:
            for patent in patents:
                self.patentsList.addItem(patent['patent_name'])
        

    def show_patent(self):
        self.patentClaimsText.clear()
        self.saoTable.clear()
        self.saoTable.setRowCount(0)
        patent_name = self.patentsList.currentItem().text()
        cursor = connection.cursor()
        cursor.execute("SELECT `patent_content` FROM `patents` WHERE `patent_name`=%s", (patent_name))
        patent = cursor.fetchone()

        if patent:
            self.patentClaimsText.setText(pp.get_claims(patent['patent_content'])[0])

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM `extracted_sao` WHERE `patent_name`=%s", (patent_name))
            saos = cursor.fetchall()

            if saos:
                self.saoTable.clear()
                self.saoTable.setRowCount(0)
                for sao in saos:
                    rowPosition = self.saoTable.rowCount()
                    self.saoTable.insertRow(rowPosition)
                    self.saoTable.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(sao['subj']))
                    self.saoTable.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(sao['act']))
                    self.saoTable.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(sao['obj']))
                self.saoTable.resizeColumnsToContents()

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM `technical_problems` WHERE `patent_name`=%s", (patent_name))
            t_problem = cursor.fetchall()

            if t_problem:
                self.problemText.clear()
                problem = t_problem[0]
                self.problemText.setText(problem['problem'])

    def load_patent(self):
        xml_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите XML-файл с патентом', '/home', 'XML files (*.xml)')[0]
        if xml_file:

            with open(xml_file, 'r') as input_xml:
                content = input_xml.read()

            patent_name = pp.get_patent_name(content)
            cursor = connection.cursor()
            sql = "INSERT INTO `patents` (`patent_name`, `patent_content`) VALUES (%s, %s)"
            cursor.execute(sql, (patent_name, content))

            connection.commit()
            self.init_patent_list()
        else:
            QtWidgets.QMessageBox.about(self.centralwidget, 'Ошибка', 'Путь к каталогу с патентами не указан.')

    def load_patents(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите каталог с патентами', '/home')
        if directory:
            xml_files = [f"{directory}/{file_path}" for file_path in os.listdir(directory)]
            cursor = connection.cursor()
            for xml_file in xml_files:
                with open(xml_file, 'r') as input_xml:
                    content = input_xml.read()
                
                patent_name = pp.get_patent_name(content)
                    # Create a new record
                sql = "INSERT INTO `patents` (`patent_name`, `patent_content`) VALUES (%s, %s)"
                cursor.execute(sql, (patent_name, content))
                connection.commit()
            self.init_patent_list()

        else:
            QtWidgets.QMessageBox.about(self.centralwidget, 'Ошибка', 'Путь к каталогу с патентами не указан.')

    def extract_sao(self):
        if self.patentsList.currentItem():
            patent_name = self.patentsList.currentItem().text()
            cursor = connection.cursor()
            cursor.execute("SELECT `patent_content` FROM `patents` WHERE `patent_name`=%s", (patent_name))
            patent = cursor.fetchone()

            if patent:
                patent_claim = pp.get_claims(patent['patent_content'])[0]
                SAOs, SAOs_with_lemma = feature_extractor.extract_sao(patent_claim)
                solution_sao = feature_extractor.get_problem_sao(patent['patent_content'])

                cursor = connection.cursor()
                for sao in SAOs:
                    sql = "INSERT INTO `extracted_sao` (`patent_name`, `subj`, `act`, `obj`) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (patent_name, sao[0], sao[1], sao[2]))
                    connection.commit()

                for sao_with_lemma in SAOs_with_lemma:
                    sql = "INSERT INTO `extracted_sao_with_lemma` (`patent_name`, `subj`, `act`, `obj`) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (patent_name, sao_with_lemma[0], sao_with_lemma[1], sao_with_lemma[2]))
                    connection.commit()
                
                if solution_sao:
                    problem_string = ''
                    for solution in solution_sao:
                            
                        problem_string = problem_string + ' '.join(solution) + '. '
                        sql = "INSERT INTO `sao_problems` (`patent_name`, `subj`, `act`, `obj`) VALUES (%s, %s, %s, %s)"
                        if len(solution) == 2:
                            cursor.execute(sql, (patent_name, '', solution[0], solution[1]))
                        else:
                            cursor.execute(sql, (patent_name, solution[0], solution[1], solution[2]))
                        connection.commit()
                    
                    sql = "INSERT INTO `technical_problems` (`patent_name`, `problem`) VALUES (%s, %s)"
                    cursor.execute(sql, (patent_name, problem_string))
                    connection.commit()

                self.show_patent()
        else:
            QtWidgets.QMessageBox.about(self.centralwidget, 'Ошибка!', 'Патент не выбран.')


    def build_ontology(self):
        patent_name = self.patentsList.currentItem().text()
        cursor = connection.cursor()
        cursor.execute("SELECT `patent_content` FROM `patents` WHERE `patent_name`=%s", (patent_name))
        patent = cursor.fetchone()

        if patent:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM `extracted_sao_with_lemma` WHERE `patent_name`=%s", (patent_name))
            saos = cursor.fetchall()
            if saos:
                saos = [[sao['subj'], sao['act'], sao['obj']] for sao in saos]

                cursor = connection.cursor()
                cursor.execute("SELECT * FROM `technical_problems` WHERE `patent_name`=%s", (patent_name))
                t_problem = cursor.fetchall()

                if t_problem:
                    problem = t_problem[0]['problem']
                else:
                    problem = ''

                patent_info = {
                    'patentName': pp.get_patent_name(patent['patent_content']),
                    'patentNumber': pp.get_patent_number(patent['patent_content']),
                    'problemName': problem,
                    'problemSolutions': None,
                    'saos': saos,
                    'mainComponent': saos[0][0]
                }
                ontology.save_patent_to_ontology(patent_info)
                QtWidgets.QMessageBox.about(self.centralwidget, 'Успех!', 'Онтология для патента построена.')
            else:
                QtWidgets.QMessageBox.about(self.centralwidget, 'Ошибка!', 'Нет извлеченных SAO.')
        else:
            QtWidgets.QMessageBox.about(self.centralwidget, 'Ошибка!', 'Нет загруженных патентов.')

    def build_patents_ontology(self):
        cursor = connection.cursor()
        cursor.execute("SELECT `patent_content` FROM `patents`")
        patents = cursor.fetchall()
        
        if patents:
            patents_info = []
            for patent in patents:
                patent_name = pp.get_patent_name(patent['patent_content'])
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM `extracted_sao_with_lemma` WHERE `patent_name`=%s", (patent_name))
                saos = cursor.fetchall()
                saos = [[sao['subj'], sao['act'], sao['obj']] for sao in saos]

                cursor = connection.cursor()
                cursor.execute("SELECT * FROM `technical_problems` WHERE `patent_name`=%s", (patent_name))
                t_problem = cursor.fetchall()

                if t_problem:
                    problem = t_problem[0]['problem']
                else:
                    problem = ''

                patent_info = {
                    'patentName': pp.get_patent_name(patent['patent_content']),
                    'patentNumber': pp.get_patent_number(patent['patent_content']),
                    'problemName': problem,
                    'problemSolutions': None,
                    'saos': saos,
                    'mainComponent': saos[0][0]
                }
                patents_info.append(patent_info)
            ontology.save_patents_to_ontology(patents_info)
            QtWidgets.QMessageBox.about(self.centralwidget, 'Успех!', 'Онтология для патентов построена.')
        else:
            QtWidgets.QMessageBox.about(self.centralwidget, 'Ошибка!', 'Нет загруженных патентов.')



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
    connection.close()
