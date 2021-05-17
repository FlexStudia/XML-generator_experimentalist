# coding: utf-8

# IMPORTS
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QLabel, QPushButton, QAction
from PyQt5.QtCore import Qt, QDate
from lxml import etree
import sys
# external templates
from source.wt import Ui_MainWindow as Ui_experimentalist_window
from source.clt import Ui_CurrentLab as Ui_CurrentLab
from source.plt import Ui_PreviousLab as Ui_PreviousLab

# GLOBALS
__version__ = 1.2
__copyright__ = "<a href='https://creativecommons.org/licenses/by/4.0/deed.fr'>CC-BY 4.0</a> (Authors attribution alone required)"
__GitHub_repos__ = "https://github.com/FlexStudia/XML-generator_experimentalist"
__author_mail__ = "flex.studia.dev@gmail.com"
__bug_support_mail__ = "XML.generator.experimentalist@gmail.com"

# XML
xml_template = "<?xml version='1.0' encoding='UTF-8'?><!--  Data type : Experimentalist Specific notes : 	- General notes :  	- Most of the tags are optional, you can remove the really unnecessary ones. 	- Tags marked as 'multiple' can be copied (with its block of sub-tag, up to the ending tag) if needed. 	- all blocs marked 'OPTION' can be fully removed if not needed (now or in the future) 	- **ABS MANDATORY / ABS COMPULSORY**: a value need to be absolutely provided, no way to escape! (SSHADE will not function properly if absent). 	- **MANDATORY / COMPULSORY**: very important values for the search of the data. If the value (txt or numeric) of one tag is not known (or irrelevant in your case), then put 'NULL' and write a comment to keep track of the missing value. Remove comment when value is added. 	- **MANDATORY / COMPULSORY only for ...**: when a value is optionally MANDATORY the condition is written.  	- 'LINK to existing UID' (unique identifier): references to another table in SSHADE. You have to reconstruct (easy for some: rule is in comment) or found this existing UID in the database beforehand (use 'Provider/Full Search' menu in SSHADE). 	- 'UID to CREATE': you need to create this UID using their specific rules of creation that are explained in their attached comment. Use only alphanumeric characters and '_'. 	- For UID you can use only alpha-numeric characters and the following: '_', '-' 	- Enumeration type ('Enum' or 'OpenEnum') must contain one single item from the list given in brackets {}. 	- use a CDATA tag when a value contains at least one special character (ie: &, >, <,...). Example: <![CDATA[AT&T]]> for AT&T 	- The data format is noted beetween [] and is 'ascii' when not specified. Ex: [Float], [Integer]. For [float] 2 formats are possible: decimal (123.456) or scientific (1.234e-56)   	- when no numerical format or Enum is specified, it is free text but limited to 256 characters. Only those noted [blob] have no size limitation. 	- to import data for the first time you have to set <import_mode>='first import'. To correct data you have to change it to 'correction'. 	- when a <filename> is given, then the file should be ziped with this xml file for import.  --><import type='experimentalist' ssdm_version='0.9.0' xmlns='http://sshade.eu/schema/import' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='http://sshade.eu/schema/import http://sshade.eu/schema/import-0.9.xsd'><experimentalist><!-- multiple --><import_mode>first import</import_mode> <!-- **ABS MANDATORY** Mode of import of the experimentalist data. Enum: {first import, ignore, draft, no change, correction} --><uid>EXPER_</uid> <!-- **ABS MANDATORY to CREATE** Unique identifier code given to the experimentalist. Should be of the style ‘EXPER_Firstname_Lastname(_n)’ --><manager_databases> <!-- **ABS MANDATORY at least one** --><database_uid>DB_</database_uid> <!-- **ABS MANDATORY** LINK to the existing UID of the database which manages the experimentalist information [‘DB_DatabaseAcronym’] -->	</manager_databases><!-- EXPERIMENTALIST NAME --><first_name></first_name> <!-- **ABS MANDATORY, requested for DOI** First name (given name) --><family_name></family_name> <!-- **ABS MANDATORY, requested for DOI** Family name (last name) --><acronym></acronym> <!-- **MANDATORY** Initials of first and last name. Ex: BS, FROD --><orcid_identifier></orcid_identifier> <!-- **MANDATORY** ORCID identifier code that uniquely identify the experimentalist --><alternate_identifiers> <!-- **OPTION** --><alternate_identifier><!-- multiple --><scheme></scheme> <!-- **ABS MANDATORY in OPTION** Alternate scheme that provideds the unique identifiers of the experimentalist. Enum: {ISNI, ResearcherID, ScopusAuthorID} --><code></code> <!-- **ABS MANDATORY in OPTION** Alternate code that uniquely identify the experimentalist in this scheme --></alternate_identifier></alternate_identifiers><state>active</state> <!-- XXX-BS 090a NEW **ABS MANDATORY** State of activity of the experimentalist. Enum: {active, inactive, retired, deceased}. default = ‘active’ --><!-- EXPERIMENTALIST LABORATORIES --><laboratories> <!-- **ABS MANDATORY at least one** Put in chronological order --><laboratory state='current'><!-- multiple --> <!-- **ABS MANDATORY, at least one 'current' for 'active', all 'previous' for others** Enum of 'state': {previous, current} --><uid></uid> <!-- **ABS MANDATORY** LINK to the existing UID of the current laboratory where the experimentalist works [‘LAB_LabAcronym’] --><status></status> <!-- **MANDATORY for current laboratory** Status of the experimentalist in this laboratory. Enum: {researcher, engineer, post-doc, PhD student, master student, undergraduate student} --><date_begin></date_begin> <!-- **ABS MANDATORY for current lab** Beginning date of the experimentalist in this laboratory. [Format: ‘YYYY-MM-DD’] Ex: '1999-10-05' --><date_end></date_end> <!-- **ABS MANDATORY for previous lab** Ending date of the experimentalist in this laboratory. [Format: ‘YYYY-MM-DD’] Ex: '1999-10-05', '' --><comments><![CDATA[]]></comments> <!-- Additional information ... [blob] --></laboratory></laboratories><!-- EXPERIMENTALIST CONTACTS --><email></email> <!-- **MANDATORY** Current e-mail of the experimentalist. Will be used as login --><phone></phone> <!-- Current phone number of the experimentalist. ex: +33(0)7 06 05 04 01 --><links> <!-- **OPTION** Link(s) to current web page(s) of the experimentalist --><link><!-- multiple --> <name><![CDATA[]]></name> <!-- Name of the web page(s) --><url><![CDATA[]]></url> <!-- **MANDATORY in OPTION** URL address (avoid non-perennial commercial URL) --></link></links><comments><![CDATA[]]></comments> <!-- Additional information on the experimentalist [blob] --></experimentalist></import>"

# global arrays
labs_current_data_array = [[], [], [], []]
labs_previous_data_array = [[], [], [], [], [], []]


# MAIN WINDOW class
class XMLTemplateExperimentalist(QtWidgets.QMainWindow):
    def __init__(self):
        super(XMLTemplateExperimentalist, self).__init__()
        self.ui = Ui_experimentalist_window()
        self.ui.setupUi(self)
        # GUI beauties
        self.setWindowTitle(f'SSHADE Experimentalist XML template v{__version__}')
        # first name
        self.ui.first_name.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(251,157,111); '
            'background-color: rgb(255,250,245); padding: 5px}')
        # family name
        self.ui.family_name.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(251,157,111); '
            'background-color: rgb(255,250,245); padding: 5px}')
        # state
        self.ui.state.setStyleSheet(
            'QComboBox{border-width: 2px; border-style: solid; border-color: rgb(251,157,111); '
            'background-color: rgb(255,250,245); padding: 5px}')
        self.ui.state.insertItem(0, 'active')
        self.ui.state.insertItem(1, 'inactive')
        self.ui.state.insertItem(2, 'retired')
        self.ui.state.insertItem(3, 'deceased')
        self.ui.state.setCurrentIndex(0)
        # email
        self.ui.email.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(240,200,41); '
            'background-color: rgb(253,253,241); padding: 5px}')
        # phone
        self.ui.phone.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        # comments (general)
        self.ui.comments_contact.setStyleSheet(
            'QTextEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        # ORCID
        self.ui.ORCID.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(240,200,41); '
            'background-color: rgb(253,253,241); padding: 5px}')
        # ISNI
        self.ui.ISNI.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        # Researcher ID
        self.ui.ResearcherID.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        # Scopus Author ID
        self.ui.ScopusAuthorID.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        # web links
        self.ui.link_url_1.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        self.ui.link_name_1.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        self.ui.link_url_2.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        self.ui.link_name_2.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        self.ui.link_url_3.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        self.ui.link_name_3.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        self.ui.link_url_4.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        self.ui.link_name_4.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(86,231,200); '
            'background-color: rgb(249,255,254); padding: 5px}')
        # current labs
        self.ui.c_lab_btn_1.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.c_lab_btn_2.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.c_lab_btn_3.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.c_lab_btn_4.setStyleSheet('QPushButton{padding: 5px}')
        # previous labs
        self.ui.p_lab_btn_1.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.p_lab_btn_2.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.p_lab_btn_3.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.p_lab_btn_4.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.p_lab_btn_5.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.p_lab_btn_6.setStyleSheet('QPushButton{padding: 5px}')
        # generate button
        self.ui.buttonBox.setStyleSheet('QPushButton{padding: 5px}')
        # Menu
        extractAction = QAction("&About", self)
        extractAction.setStatusTip('About The App')
        extractAction.triggered.connect(self.show_about)
        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Help')
        fileMenu.addAction(extractAction)
        # SIGNALS & SLOTS
        # current labs
        self.ui.c_lab_btn_1.clicked.connect(self.add_current_lab_1)
        self.ui.c_lab_btn_2.clicked.connect(self.add_current_lab_2)
        self.ui.c_lab_btn_3.clicked.connect(self.add_current_lab_3)
        self.ui.c_lab_btn_4.clicked.connect(self.add_current_lab_4)
        # previous labs
        self.ui.p_lab_btn_1.clicked.connect(self.add_previous_lab_1)
        self.ui.p_lab_btn_2.clicked.connect(self.add_previous_lab_2)
        self.ui.p_lab_btn_3.clicked.connect(self.add_previous_lab_3)
        self.ui.p_lab_btn_4.clicked.connect(self.add_previous_lab_4)
        self.ui.p_lab_btn_5.clicked.connect(self.add_previous_lab_5)
        self.ui.p_lab_btn_6.clicked.connect(self.add_previous_lab_6)
        # main fill button
        self.ui.buttonBox.clicked.connect(self.fill_XML)


    def show_about(self):
        self.dialog_ok(f"<b>XML generator: experimentalist</b> v{__version__}"
                       f"<p>Copyright: {__copyright__}</p>"
                       f"<p><a href='{__GitHub_repos__}'>GitHub repository</a> (program code and more information)</p>"
                       f"<p>Created by Gorbacheva Maria ({__author_mail__})</p>"
                       "<p>Scientific base by Bernard Schmitt, IPAG (bernard.schmitt@univ-grenoble-alpes.fr)</p>"
                       f"<p>For any questions and bug reports, please, mail at {__bug_support_mail__}</p>"
                       "<p>In case of a bug, please report it and specify your operating system, "
                       "provide a detailed description of the problem with screenshots "
                       "and the files used and produced, if possible. Your contribution matters to make it better!</p>")

    def dialog_ok(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('Ok!')
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Information)
        dlg.show()

    # SIGNALS functions
    # current labs
    def add_current_lab_1(self):
        XMLTemplateCurrentLab(1)

    def add_current_lab_2(self):
        XMLTemplateCurrentLab(2)

    def add_current_lab_3(self):
        XMLTemplateCurrentLab(3)

    def add_current_lab_4(self):
        XMLTemplateCurrentLab(4)

    # previous labs
    def add_previous_lab_1(self):
        XMLTemplatePreviousLab(1)

    def add_previous_lab_2(self):
        XMLTemplatePreviousLab(2)

    def add_previous_lab_3(self):
        XMLTemplatePreviousLab(3)

    def add_previous_lab_4(self):
        XMLTemplatePreviousLab(4)

    def add_previous_lab_5(self):
        XMLTemplatePreviousLab(5)

    def add_previous_lab_6(self):
        XMLTemplatePreviousLab(6)

    # dialog windows
    def dialog_ok(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('Info')
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Information)
        dlg.show()

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('Error!')
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    # main fill button
    def fill_XML(self):
        # FUNCTION replacing special character
        def special_characters_replace(string_var):
            # A
            string_var = string_var.replace("À", "A")
            string_var = string_var.replace("Á", "A")
            string_var = string_var.replace("Â", "A")
            string_var = string_var.replace("Ã", "A")
            string_var = string_var.replace("Ä", "A")
            string_var = string_var.replace("Å", "A")
            string_var = string_var.replace("Æ", "Ae")
            # C
            string_var = string_var.replace("Ç", "C")
            # D
            string_var = string_var.replace("Ð", "D")
            # E
            string_var = string_var.replace("È", "E")
            string_var = string_var.replace("É", "E")
            string_var = string_var.replace("Ê", "E")
            string_var = string_var.replace("Ë", "E")
            # I
            string_var = string_var.replace("Ì", "I")
            string_var = string_var.replace("Í", "I")
            string_var = string_var.replace("Î", "I")
            string_var = string_var.replace("Ï", "I")
            # N
            string_var = string_var.replace("Ñ", "N")
            # O
            string_var = string_var.replace("Ò", "O")
            string_var = string_var.replace("Ó", "O")
            string_var = string_var.replace("Ô", "O")
            string_var = string_var.replace("Õ", "O")
            string_var = string_var.replace("Ö", "O")
            string_var = string_var.replace("Ø", "O")
            # T
            string_var = string_var.replace("Þ", "th")
            # U
            string_var = string_var.replace("Ù", "U")
            string_var = string_var.replace("Ú", "U")
            string_var = string_var.replace("Û", "U")
            string_var = string_var.replace("Ü", "U")
            # Y
            string_var = string_var.replace("Ý", "Y")
            # a
            string_var = string_var.replace("à", "a")
            string_var = string_var.replace("á", "a")
            string_var = string_var.replace("â", "a")
            string_var = string_var.replace("ã", "a")
            string_var = string_var.replace("ä", "a")
            string_var = string_var.replace("å", "a")
            string_var = string_var.replace("æ", "ae")
            # c
            string_var = string_var.replace("ç", "c")
            # d
            string_var = string_var.replace("ð", "d")
            # e
            string_var = string_var.replace("è", "e")
            string_var = string_var.replace("é", "e")
            string_var = string_var.replace("ê", "e")
            string_var = string_var.replace("ë", "e")
            # i
            string_var = string_var.replace("ì", "i")
            string_var = string_var.replace("í", "i")
            string_var = string_var.replace("î", "i")
            string_var = string_var.replace("ï", "i")
            # n
            string_var = string_var.replace("ñ", "n")
            # o
            string_var = string_var.replace("ò", "o")
            string_var = string_var.replace("ó", "o")
            string_var = string_var.replace("ô", "o")
            string_var = string_var.replace("õ", "o")
            string_var = string_var.replace("ö", "o")
            string_var = string_var.replace("ø", "o")
            # t
            string_var = string_var.replace("þ", "th")
            # s
            string_var = string_var.replace("ß", "ss")
            # u
            string_var = string_var.replace("ù", "u")
            string_var = string_var.replace("ú", "u")
            string_var = string_var.replace("û", "u")
            string_var = string_var.replace("û", "u")
            string_var = string_var.replace("ü", "u")
            # y
            string_var = string_var.replace("ý", "y")
            string_var = string_var.replace("ÿ", "y")
            return string_var

        # VERIFICATION of data & FILLING the XML template
        verification_Ok = 1
        # abs_mandatory
        if self.ui.first_name.text().strip() == '':
            verification_Ok = 0
            self.dialog_critical('First name is mandatory!')
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.first_name.setFocus()
        elif self.ui.family_name.text().strip() == '':
            verification_Ok = 0
            self.dialog_critical('Family name is mandatory!')
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.family_name.setFocus()
        elif labs_current_data_array[0] == [] and labs_current_data_array[1] == [] and labs_current_data_array[2] == [] \
                and labs_current_data_array[3] == []:
            verification_Ok = 0
            self.dialog_critical('At least on current lab is mandatory!')
            self.ui.tabWidget.setCurrentIndex(3)
            self.ui.c_lab_btn_1.setFocus()
        # mandatory
        if verification_Ok and self.ui.email.text() == '':
            reply = QMessageBox.question(self, 'Message',
                                         "Are you sure to leave no email?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                verification_Ok = 0
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.email.setFocus()
        if verification_Ok and self.ui.ORCID.text() == '':
            reply = QMessageBox.question(self, 'Message',
                                         "Are you sure to leave no ORCID?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                verification_Ok = 0
                self.ui.tabWidget.setCurrentIndex(1)
                self.ui.ORCID.setFocus()
        # filling
        if verification_Ok:
            # SORTING labs arrays
            # previous
            index_array_previous = []
            for d in range(len(labs_previous_data_array)):
                if labs_previous_data_array[d]:
                    index_array_previous.append([d, int(labs_previous_data_array[d][3][0:4]) * 365
                                                 + int(labs_previous_data_array[d][3][5:7]) * 30
                                                 + int(labs_previous_data_array[d][3][8:])])

            def take_second(elem):
                return elem[1]

            index_array_previous.sort(key=take_second)
            # current
            index_array_current = []
            for d in range(len(labs_current_data_array)):
                if labs_current_data_array[d]:
                    index_array_current.append([d, int(labs_current_data_array[d][3][0:4]) * 365 + int(
                        labs_current_data_array[d][3][5:7]) * 30 + int(labs_current_data_array[d][3][8:])])
            index_array_current.sort(key=take_second)
            # FILLING the XML
            parser = etree.XMLParser(remove_blank_text=True)
            xml_root = etree.fromstring(xml_template.encode("utf8"), parser)
            for child in xml_root.find("{http://sshade.eu/schema/import}experimentalist").getchildren():
                if child.tag == "{http://sshade.eu/schema/import}uid":
                    child.clear()
                    uid = "EXPER_" + special_characters_replace(self.ui.first_name.text().strip()).capitalize(). \
                        replace(" ", "-") + "_" + special_characters_replace(self.ui.family_name.text().strip()). \
                              capitalize().replace(" ", "-")
                    child.text = uid
                    comment_verify = etree.Comment(" %%% TO VERIFY ")
                    child.insert(0, comment_verify)
                if child.tag == "{http://sshade.eu/schema/import}first_name":
                    child.clear()
                    if self.ui.first_name.text().strip() == special_characters_replace(
                            self.ui.first_name.text().strip()):
                        child.text = self.ui.first_name.text().strip()
                    else:
                        child.text = etree.CDATA(self.ui.first_name.text().strip())
                if child.tag == "{http://sshade.eu/schema/import}family_name":
                    child.clear()
                    if self.ui.family_name.text().strip() == special_characters_replace(
                            self.ui.family_name.text().strip()):
                        child.text = self.ui.family_name.text().strip()
                    else:
                        child.text = etree.CDATA(self.ui.family_name.text().strip())
                if child.tag == "{http://sshade.eu/schema/import}acronym":
                    child.clear()
                    acronym = self.ui.first_name.text().strip()[0].upper()
                    for n in range(len(self.ui.first_name.text().strip())):
                        if n < len(self.ui.first_name.text().strip()) - 1 and (
                                self.ui.first_name.text().strip()[n] == " " or self.ui.first_name.text().strip()[
                            n] == "-"):
                            acronym = acronym + self.ui.first_name.text().strip()[n + 1].upper()
                    acronym = acronym + self.ui.family_name.text().strip()[0].upper()
                    for n in range(len(self.ui.family_name.text().strip())):
                        if n < len(self.ui.family_name.text().strip()) - 1 and (
                                self.ui.family_name.text().strip()[n] == " " or self.ui.family_name.text().strip()[
                            n] == "-"):
                            acronym = acronym + self.ui.family_name.text().strip()[n + 1].upper()
                    child.text = special_characters_replace(acronym)
                    comment_verify = etree.Comment(" %%% TO VERIFY ")
                    child.insert(0, comment_verify)
                if child.tag == "{http://sshade.eu/schema/import}email":
                    child.clear()
                    if self.ui.email.text().strip() != "":
                        child.text = self.ui.email.text().strip()
                    else:
                        child.text = "NULL"
                if child.tag == "{http://sshade.eu/schema/import}phone":
                    child.clear()
                    child.text = self.ui.phone.text().strip()
                if child.tag == "{http://sshade.eu/schema/import}comments":
                    child.clear()
                    if self.ui.comments_contact.toPlainText() == special_characters_replace(
                            self.ui.comments_contact.toPlainText()):
                        child.text = self.ui.comments_contact.toPlainText()
                    else:
                        child.text = etree.CDATA(self.ui.comments_contact.toPlainText())
                if child.tag == "{http://sshade.eu/schema/import}orcid_identifier":
                    child.clear()
                    if self.ui.ORCID.text().strip() != '':
                        child.text = self.ui.ORCID.text().strip()
                    else:
                        child.text = 'NULL'
                if child.tag == "{http://sshade.eu/schema/import}alternate_identifiers":
                    at_least_one_is_added = 0
                    if self.ui.ISNI.text().strip() != "":
                        for item in child.iter():
                            if item.tag == "{http://sshade.eu/schema/import}alternate_identifier":
                                for inner_item in item.iter():
                                    if inner_item.tag == "{http://sshade.eu/schema/import}scheme":
                                        inner_item.clear()
                                        inner_item.text = 'ISNI'
                                        at_least_one_is_added = 1
                                    if inner_item.tag == "{http://sshade.eu/schema/import}code":
                                        inner_item.clear()
                                        inner_item.text = self.ui.ISNI.text().strip()
                    if self.ui.ResearcherID.text().strip() != "":
                        if at_least_one_is_added:
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'alternate_identifier')
                            child1_element = etree.SubElement(big_child_element, 'scheme')
                            child1_element.text = 'ResearcherID'
                            child2_element = etree.SubElement(big_child_element, 'code')
                            child2_element.text = self.ui.ResearcherID.text().strip()
                        else:
                            for item in child.iter():
                                if item.tag == "{http://sshade.eu/schema/import}alternate_identifier":
                                    for inner_item in item.iter():
                                        if inner_item.tag == "{http://sshade.eu/schema/import}scheme":
                                            inner_item.clear()
                                            inner_item.text = 'ResearcherID'
                                            at_least_one_is_added = 1
                                        if inner_item.tag == "{http://sshade.eu/schema/import}code":
                                            inner_item.clear()
                                            inner_item.text = self.ui.ResearcherID.text().strip()
                    if self.ui.ScopusAuthorID.text().strip() != "":
                        if at_least_one_is_added:
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'alternate_identifier')
                            child1_element = etree.SubElement(big_child_element, 'scheme')
                            child1_element.text = 'ScopusAuthorID'
                            child2_element = etree.SubElement(big_child_element, 'code')
                            child2_element.text = self.ui.ScopusAuthorID.text().strip()
                        else:
                            for item in child.iter():
                                if item.tag == "{http://sshade.eu/schema/import}alternate_identifier":
                                    for inner_item in item.iter():
                                        if inner_item.tag == "{http://sshade.eu/schema/import}scheme":
                                            inner_item.clear()
                                            inner_item.text = 'ScopusAuthorID'
                                            at_least_one_is_added = 1
                                        if inner_item.tag == "{http://sshade.eu/schema/import}code":
                                            inner_item.clear()
                                            inner_item.text = self.ui.ScopusAuthorID.text().strip()
                    if at_least_one_is_added == 0:
                        for item in child.iter():
                            if item.tag == "{http://sshade.eu/schema/import}alternate_identifier":
                                for inner_item in item.iter():
                                    if inner_item.tag == "{http://sshade.eu/schema/import}scheme":
                                        inner_item.clear()
                                        inner_item.text = ''
                                    if inner_item.tag == "{http://sshade.eu/schema/import}code":
                                        inner_item.clear()
                                        inner_item.text = ''
                if child.tag == "{http://sshade.eu/schema/import}state":
                    child.clear()
                    child.text = self.ui.state.currentText()
                if child.tag == "{http://sshade.eu/schema/import}links":
                    at_least_one_is_added = 0
                    if self.ui.link_name_1.text().strip() != "" and self.ui.link_url_1.text().strip() != "":
                        for item in child.iter():
                            if item.tag == "{http://sshade.eu/schema/import}link":
                                for inner_item in item.iter():
                                    if inner_item.tag == "{http://sshade.eu/schema/import}name":
                                        inner_item.clear()
                                        if self.ui.link_name_1.text() != special_characters_replace(
                                                self.ui.link_name_1.text()):
                                            inner_item.text = etree.CDATA(self.ui.link_name_1.text())
                                        else:
                                            inner_item.text = self.ui.link_name_1.text()
                                        at_least_one_is_added = 1
                                    if inner_item.tag == "{http://sshade.eu/schema/import}url":
                                        inner_item.clear()
                                        inner_item.text = etree.CDATA(self.ui.link_url_1.text())
                    if self.ui.link_name_2.text().strip() != "" and self.ui.link_url_2.text().strip() != "":
                        if at_least_one_is_added:
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'link')
                            child1_element = etree.SubElement(big_child_element, 'name')
                            if self.ui.link_name_2.text() != special_characters_replace(self.ui.link_name_2.text()):
                                child1_element.text = etree.CDATA(self.ui.link_name_2.text())
                            else:
                                child1_element.text = self.ui.link_name_2.text()
                            child2_element = etree.SubElement(big_child_element, 'url')
                            child2_element.text = etree.CDATA(self.ui.link_url_2.text())
                        else:
                            for item in child.iter():
                                if item.tag == "{http://sshade.eu/schema/import}link":
                                    for inner_item in item.iter():
                                        if inner_item.tag == "{http://sshade.eu/schema/import}name":
                                            inner_item.clear()
                                            if self.ui.link_name_2.text() != special_characters_replace(
                                                    self.ui.link_name_2.text()):
                                                inner_item.text = etree.CDATA(self.ui.link_name_2.text())
                                            else:
                                                inner_item.text = self.ui.link_name_2.text()
                                            at_least_one_is_added = 1
                                        if inner_item.tag == "{http://sshade.eu/schema/import}url":
                                            inner_item.clear()
                                            inner_item.text = etree.CDATA(self.ui.link_url_2.text())
                    if self.ui.link_name_3.text().strip() != "" and self.ui.link_url_3.text().strip() != "":
                        if at_least_one_is_added:
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'link')
                            child1_element = etree.SubElement(big_child_element, 'name')
                            if self.ui.link_name_3.text() != special_characters_replace(self.ui.link_name_3.text()):
                                child1_element.text = etree.CDATA(self.ui.link_name_3.text())
                            else:
                                child1_element.text = self.ui.link_name_3.text()
                            child2_element = etree.SubElement(big_child_element, 'url')
                            child2_element.text = etree.CDATA(self.ui.link_url_3.text())
                        else:
                            for item in child.iter():
                                if item.tag == "{http://sshade.eu/schema/import}link":
                                    for inner_item in item.iter():
                                        if inner_item.tag == "{http://sshade.eu/schema/import}name":
                                            inner_item.clear()
                                            if self.ui.link_name_3.text() != special_characters_replace(
                                                    self.ui.link_name_3.text()):
                                                inner_item.text = etree.CDATA(self.ui.link_name_3.text())
                                            else:
                                                inner_item.text = self.ui.link_name_3.text()
                                            at_least_one_is_added = 1
                                        if inner_item.tag == "{http://sshade.eu/schema/import}url":
                                            inner_item.clear()
                                            inner_item.text = etree.CDATA(self.ui.link_url_3.text())
                    if self.ui.link_name_4.text().strip() != "" and self.ui.link_url_4.text().strip() != "":
                        if at_least_one_is_added:
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'link')
                            child1_element = etree.SubElement(big_child_element, 'name')
                            if self.ui.link_name_4.text() != special_characters_replace(self.ui.link_name_4.text()):
                                child1_element.text = etree.CDATA(self.ui.link_name_4.text())
                            else:
                                child1_element.text = self.ui.link_name_4.text()
                            child2_element = etree.SubElement(big_child_element, 'url')
                            child2_element.text = etree.CDATA(self.ui.link_url_4.text())
                        else:
                            for item in child.iter():
                                if item.tag == "{http://sshade.eu/schema/import}link":
                                    for inner_item in item.iter():
                                        if inner_item.tag == "{http://sshade.eu/schema/import}name":
                                            inner_item.clear()
                                            if self.ui.link_name_4.text() != special_characters_replace(
                                                    self.ui.link_name_4.text()):
                                                inner_item.text = etree.CDATA(self.ui.link_name_4.text())
                                            else:
                                                inner_item.text = self.ui.link_name_4.text()
                                            at_least_one_is_added = 1
                                        if inner_item.tag == "{http://sshade.eu/schema/import}url":
                                            inner_item.clear()
                                            inner_item.text = etree.CDATA(self.ui.link_url_4.text())
                    if at_least_one_is_added == 0:
                        for item in child.iter():
                            if item.tag == "{http://sshade.eu/schema/import}link":
                                for inner_item in item.iter():
                                    if inner_item.tag == "{http://sshade.eu/schema/import}name":
                                        inner_item.clear()
                                        inner_item.text = ''
                                    if inner_item.tag == "{http://sshade.eu/schema/import}url":
                                        inner_item.clear()
                                        inner_item.text = ''
                if child.tag == "{http://sshade.eu/schema/import}laboratories":
                    if len(index_array_previous) == 0:
                        for item in child.iter():
                            if item.tag == "{http://sshade.eu/schema/import}laboratory":
                                item.set('state', 'current')
                                for inner_item in item.iter():
                                    if inner_item.tag == "{http://sshade.eu/schema/import}uid":
                                        inner_item.clear()
                                        inner_item.text = "LAB_" + special_characters_replace(
                                            labs_current_data_array[index_array_current[0][0]][0])
                                        comment_verify = etree.Comment(" %%% TO VERIFY ")
                                        inner_item.insert(0, comment_verify)
                                    if inner_item.tag == "{http://sshade.eu/schema/import}status":
                                        inner_item.clear()
                                        if labs_current_data_array[index_array_current[0][0]][2] == 'no status':
                                            inner_item.text = 'NULL'
                                        else:
                                            inner_item.text = labs_current_data_array[index_array_current[0][0]][2]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}date_begin":
                                        inner_item.clear()
                                        inner_item.text = labs_current_data_array[index_array_current[0][0]][3]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}date_end":
                                        inner_item.clear()
                                        inner_item.text = ''
                                    if inner_item.tag == "{http://sshade.eu/schema/import}comments":
                                        inner_item.clear()
                                        if labs_current_data_array[index_array_current[0][0]][4] != \
                                                special_characters_replace(
                                                    labs_current_data_array[index_array_current[0][0]][4]):
                                            inner_item.text = etree.CDATA(
                                                labs_current_data_array[index_array_current[0][0]][4])
                                        else:
                                            inner_item.text = labs_current_data_array[index_array_current[0][0]][4]
                        if len(index_array_current) > 1:
                            for d in range(1, len(index_array_current)):
                                parent_element = child
                                big_child_element = etree.SubElement(parent_element, 'laboratory')
                                big_child_element.set('state', 'current')
                                child_element = etree.SubElement(big_child_element, 'uid')
                                child_element.text = "LAB_" + special_characters_replace(
                                    labs_current_data_array[index_array_current[d][0]][0])
                                comment_verify = etree.Comment(" %%% TO VERIFY ")
                                child_element.insert(0, comment_verify)
                                child_element = etree.SubElement(big_child_element, 'status')
                                if labs_current_data_array[index_array_current[d][0]][2] == 'no status':
                                    child_element.text = 'NULL'
                                else:
                                    child_element.text = labs_current_data_array[index_array_current[d][0]][2]
                                child_element = etree.SubElement(big_child_element, 'date_begin')
                                child_element.text = labs_current_data_array[index_array_current[d][0]][3]
                                child_element = etree.SubElement(big_child_element, 'date_end')
                                child_element.text = ''
                                child_element = etree.SubElement(big_child_element, 'comments')
                                if labs_current_data_array[index_array_current[d][0]][4] != \
                                        special_characters_replace(
                                            labs_current_data_array[index_array_current[d][0]][4]):
                                    child_element.text = etree.CDATA(
                                        labs_current_data_array[index_array_current[d][0]][4])
                                else:
                                    child_element.text = labs_current_data_array[index_array_current[d][0]][4]
                    elif len(index_array_previous) == 1:
                        for item in child.iter():
                            if item.tag == "{http://sshade.eu/schema/import}laboratory":
                                item.set('state', 'previous')
                                for inner_item in item.iter():
                                    if inner_item.tag == "{http://sshade.eu/schema/import}uid":
                                        inner_item.clear()
                                        inner_item.text = "LAB_" + special_characters_replace(
                                            labs_previous_data_array[index_array_previous[0][0]][0])
                                        comment_verify = etree.Comment(" %%% TO VERIFY ")
                                        inner_item.insert(0, comment_verify)
                                    if inner_item.tag == "{http://sshade.eu/schema/import}status":
                                        inner_item.clear()
                                        if labs_previous_data_array[index_array_previous[0][0]][2] == 'no status':
                                            inner_item.text = 'NULL'
                                        else:
                                            inner_item.text = labs_previous_data_array[index_array_previous[0][0]][2]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}date_begin":
                                        inner_item.clear()
                                        inner_item.text = labs_previous_data_array[index_array_previous[0][0]][3]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}date_end":
                                        inner_item.clear()
                                        inner_item.text = labs_previous_data_array[index_array_previous[0][0]][4]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}comments":
                                        inner_item.clear()
                                        if labs_previous_data_array[index_array_previous[0][0]][5] != \
                                                special_characters_replace(
                                                    labs_previous_data_array[index_array_previous[0][0]][5]):
                                            inner_item.text = etree.CDATA(
                                                labs_previous_data_array[index_array_previous[0][0]][5])
                                        else:
                                            inner_item.text = labs_previous_data_array[index_array_previous[0][0]][5]
                        for d in range(len(index_array_current)):
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'laboratory')
                            big_child_element.set('state', 'current')
                            child_element = etree.SubElement(big_child_element, 'uid')
                            child_element.text = "LAB_" + special_characters_replace(
                                labs_current_data_array[index_array_current[d][0]][0])
                            comment_verify = etree.Comment(" %%% TO VERIFY ")
                            child_element.insert(0, comment_verify)
                            child_element = etree.SubElement(big_child_element, 'status')
                            if labs_current_data_array[index_array_current[d][0]][2] == 'no status':
                                child_element.text = 'NULL'
                            else:
                                child_element.text = labs_current_data_array[index_array_current[d][0]][2]
                            child_element = etree.SubElement(big_child_element, 'date_begin')
                            child_element.text = labs_current_data_array[index_array_current[d][0]][3]
                            child_element = etree.SubElement(big_child_element, 'date_end')
                            child_element.text = ''
                            child_element = etree.SubElement(big_child_element, 'comments')
                            if labs_current_data_array[index_array_current[d][0]][4] != \
                                    special_characters_replace(
                                        labs_current_data_array[index_array_current[d][0]][4]):
                                child_element.text = etree.CDATA(
                                    labs_current_data_array[index_array_current[d][0]][4])
                            else:
                                child_element.text = labs_current_data_array[index_array_current[d][0]][4]
                    else:
                        for item in child.iter():
                            if item.tag == "{http://sshade.eu/schema/import}laboratory":
                                item.set('state', 'previous')
                                for inner_item in item.iter():
                                    if inner_item.tag == "{http://sshade.eu/schema/import}uid":
                                        inner_item.clear()
                                        inner_item.text = "LAB_" + special_characters_replace(
                                            labs_previous_data_array[index_array_previous[0][0]][0])
                                        comment_verify = etree.Comment(" %%% TO VERIFY ")
                                        inner_item.insert(0, comment_verify)
                                    if inner_item.tag == "{http://sshade.eu/schema/import}status":
                                        inner_item.clear()
                                        if labs_previous_data_array[index_array_previous[0][0]][2] == 'no status':
                                            inner_item.text = 'NULL'
                                        else:
                                            inner_item.text = labs_previous_data_array[index_array_previous[0][0]][2]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}date_begin":
                                        inner_item.clear()
                                        inner_item.text = labs_previous_data_array[index_array_previous[0][0]][3]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}date_end":
                                        inner_item.clear()
                                        inner_item.text = labs_previous_data_array[index_array_previous[0][0]][4]
                                    if inner_item.tag == "{http://sshade.eu/schema/import}comments":
                                        inner_item.clear()
                                        if labs_previous_data_array[index_array_previous[0][0]][5] != \
                                                special_characters_replace(
                                                    labs_previous_data_array[index_array_previous[0][0]][5]):
                                            inner_item.text = etree.CDATA(
                                                labs_previous_data_array[index_array_previous[0][0]][5])
                                        else:
                                            inner_item.text = labs_previous_data_array[index_array_previous[0][0]][5]
                        for d in range(1, len(index_array_previous)):
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'laboratory')
                            big_child_element.set('state', 'previous')
                            child_element = etree.SubElement(big_child_element, 'uid')
                            child_element.text = "LAB_" + special_characters_replace(
                                labs_previous_data_array[index_array_previous[d][0]][0])
                            comment_verify = etree.Comment(" %%% TO VERIFY ")
                            child_element.insert(0, comment_verify)
                            child_element = etree.SubElement(big_child_element, 'status')
                            if labs_previous_data_array[index_array_previous[d][0]][2] == 'no status':
                                child_element.text = 'NULL'
                            else:
                                child_element.text = labs_previous_data_array[index_array_previous[d][0]][2]
                            child_element = etree.SubElement(big_child_element, 'date_begin')
                            child_element.text = labs_previous_data_array[index_array_previous[d][0]][3]
                            child_element = etree.SubElement(big_child_element, 'date_end')
                            child_element.text = labs_previous_data_array[index_array_previous[d][0]][4]
                            child_element = etree.SubElement(big_child_element, 'comments')
                            if labs_previous_data_array[index_array_previous[d][0]][5] != \
                                    special_characters_replace(
                                        labs_previous_data_array[index_array_previous[d][0]][5]):
                                child_element.text = etree.CDATA(
                                    labs_previous_data_array[index_array_previous[d][0]][5])
                            else:
                                child_element.text = labs_previous_data_array[index_array_previous[d][0]][5]
                        for d in range(len(index_array_current)):
                            parent_element = child
                            big_child_element = etree.SubElement(parent_element, 'laboratory')
                            big_child_element.set('state', 'current')
                            child_element = etree.SubElement(big_child_element, 'uid')
                            child_element.text = "LAB_" + special_characters_replace(
                                labs_current_data_array[index_array_current[d][0]][0])
                            comment_verify = etree.Comment(" %%% TO VERIFY ")
                            child_element.insert(0, comment_verify)
                            child_element = etree.SubElement(big_child_element, 'status')
                            if labs_current_data_array[index_array_current[d][0]][2] == 'no status':
                                child_element.text = 'NULL'
                            else:
                                child_element.text = labs_current_data_array[index_array_current[d][0]][2]
                            child_element = etree.SubElement(big_child_element, 'date_begin')
                            child_element.text = labs_current_data_array[index_array_current[d][0]][3]
                            child_element = etree.SubElement(big_child_element, 'date_end')
                            child_element.text = ''
                            child_element = etree.SubElement(big_child_element, 'comments')
                            if labs_current_data_array[index_array_current[d][0]][4] != \
                                    special_characters_replace(
                                        labs_current_data_array[index_array_current[d][0]][4]):
                                child_element.text = etree.CDATA(
                                    labs_current_data_array[index_array_current[d][0]][4])
                            else:
                                child_element.text = labs_current_data_array[index_array_current[d][0]][4]

            # SAVING the XML file
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", f"{uid}.xml",
                                                       "Text Files (*.xml)", options=options)
            if file_name:
                str_to_upload = etree.tostring(xml_root, pretty_print=True, encoding="utf-8",
                                               xml_declaration=True, method="xml")
                with open(file_name, 'wb') as file_output:
                    file_output.write(str_to_upload)
                self.dialog_ok('The XML was saved!')


# CURRENT labs CLASS
class XMLTemplateCurrentLab(QtWidgets.QDialog):
    def __init__(self, current_lab_edit):
        super(XMLTemplateCurrentLab, self).__init__()
        self.ui = Ui_CurrentLab()
        self.ui.setupUi(self)
        self.current_lab_edit = current_lab_edit
        # GUI beauties
        self.setWindowTitle(f'Add/Edit current lab {current_lab_edit}')
        # acronym
        self.ui.c_lab_acronym.setStyleSheet(
            'QLineEdit{border-width: 2px; border-style: solid; border-color: rgb(251,157,111); '
            'background-color: rgb(255,250,245); padding: 5px}')
        if labs_current_data_array[current_lab_edit - 1]:
            self.ui.c_lab_acronym.setText(labs_current_data_array[current_lab_edit - 1][0])
        # status
        self.ui.c_status.setStyleSheet(
            'QComboBox{border-width: 2px; border-style: solid; border-color: rgb(240,200,41); '
            'background-color: rgb(253,253,241); padding: 5px}')
        self.ui.c_status.insertItem(0, 'no status')
        self.ui.c_status.insertItem(1, 'researcher')
        self.ui.c_status.insertItem(2, 'engineer')
        self.ui.c_status.insertItem(3, 'post-doc')
        self.ui.c_status.insertItem(4, 'PhD student')
        self.ui.c_status.insertItem(5, 'master student')
        self.ui.c_status.insertItem(6, 'undergraduate student')
        if labs_current_data_array[current_lab_edit - 1]:
            self.ui.c_status.setCurrentIndex(labs_current_data_array[current_lab_edit - 1][1])
        # begin date
        self.ui.c_begin_date.setStyleSheet('QDateEdit{border-width: 2px; border-style: solid; border-color: '
                                           'rgb(251,157,111); background-color: rgb(255,250,245); padding: 5px}')
        self.ui.c_begin_date.setDisplayFormat('yyyy-MM-dd')
        if labs_current_data_array[current_lab_edit - 1]:
            self.ui.c_begin_date.setDate(
                QDate.fromString(labs_current_data_array[current_lab_edit - 1][3], 'yyyy-MM-dd'))
        else:
            self.ui.c_begin_date.setDate(QDate.fromString('1900-01-01', 'yyyy-MM-dd'))
        # additional information
        self.ui.c_lab_comment.setStyleSheet('QTextEdit{border-width: 2px; border-style: solid; border-color: '
                                            'rgb(86,231,200); background-color: rgb(249,255,254); padding: 5px}')
        if labs_current_data_array[current_lab_edit - 1]:
            self.ui.c_lab_comment.setPlainText(labs_current_data_array[current_lab_edit - 1][4])
        # button
        self.ui.buttonBox.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.clear_btn.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.cancel_btn.setStyleSheet('QPushButton{padding: 5px}')
        # SLOTS & SIGNALS
        self.ui.buttonBox.clicked.connect(self.add_current_lab_action)
        self.ui.cancel_btn.clicked.connect(self.close_add_lab)
        self.ui.clear_btn.clicked.connect(self.clear_add_lab)
        # WINDOW show
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        self.exec_()

    # SIGNALS functions
    def close_add_lab(self):
        self.close()

    def clear_add_lab(self):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to clear the form?\nAll its data will be lost", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ui.c_lab_acronym.setText('')
            self.ui.c_status.setCurrentIndex(0)
            self.ui.c_begin_date.setDate(QDate.fromString('1900-01-01', 'yyyy-MM-dd'))
            self.ui.c_lab_comment.setPlainText('')
            labs_current_data_array[self.current_lab_edit - 1].clear()

    def add_current_lab_action(self):
        verification_Ok = 1
        # abd_mandatory
        if self.ui.c_lab_acronym.text().strip() == '':
            verification_Ok = 0
            self.dialog_critical('Lab Acronym is mandatory!')
            self.ui.c_lab_acronym.setFocus()
        elif self.ui.c_begin_date.date().toString("yyyy-MM-dd") == '1900-01-01':
            verification_Ok = 0
            self.dialog_critical('Beginning date is mandatory!\nWe need this for DOI')
            self.ui.c_begin_date.setFocus()
        # mandatory
        if verification_Ok and self.ui.c_status.currentIndex() == 0:
            reply = QMessageBox.question(self, 'Message',
                                         "Are you sure to leave the status empty?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                verification_Ok = 0
                self.ui.c_status.setFocus()
        # creation or re-filling
        if verification_Ok:
            if not labs_current_data_array[self.current_lab_edit - 1]:
                labs_current_data_array[self.current_lab_edit - 1].append(self.ui.c_lab_acronym.text())
                labs_current_data_array[self.current_lab_edit - 1].append(self.ui.c_status.currentIndex())
                labs_current_data_array[self.current_lab_edit - 1].append(self.ui.c_status.currentText())
                labs_current_data_array[self.current_lab_edit - 1].append(
                    self.ui.c_begin_date.date().toString("yyyy-MM-dd"))
                labs_current_data_array[self.current_lab_edit - 1].append(self.ui.c_lab_comment.toPlainText())
            else:
                labs_current_data_array[self.current_lab_edit - 1][0] = self.ui.c_lab_acronym.text()
                labs_current_data_array[self.current_lab_edit - 1][1] = self.ui.c_status.currentIndex()
                labs_current_data_array[self.current_lab_edit - 1][2] = self.ui.c_status.currentText()
                labs_current_data_array[self.current_lab_edit - 1][3] = self.ui.c_begin_date.date().toString(
                    "yyyy-MM-dd")
                labs_current_data_array[self.current_lab_edit - 1][4] = self.ui.c_lab_comment.toPlainText()
            self.close()

    # dialog windows
    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('Error!')
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()


# PREVIOUS labs CLASS
class XMLTemplatePreviousLab(QtWidgets.QDialog):
    def __init__(self, previous_lab_edit):
        super(XMLTemplatePreviousLab, self).__init__()
        self.ui = Ui_PreviousLab()
        self.ui.setupUi(self)
        self.previous_lab_edit = previous_lab_edit
        # GUI beauties
        # window
        self.setWindowTitle(f'Add/Edit previous lab {previous_lab_edit}')
        # acronym
        self.ui.p_lab_acronym.setStyleSheet('QLineEdit{border-width: 2px; border-style: solid; border-color: '
                                            'rgb(251,157,111); background-color: rgb(255,250,245); '
                                            'padding: 5px}')
        if labs_previous_data_array[previous_lab_edit - 1]:
            self.ui.p_lab_acronym.setText(labs_previous_data_array[previous_lab_edit - 1][0])
        # status
        self.ui.p_status.setStyleSheet('QComboBox{border-width: 2px; border-style: solid; '
                                       'border-color: rgb(240,200,41); background-color: rgb(253,253,241); '
                                       'padding: 5px}')
        self.ui.p_status.insertItem(0, 'no status')
        self.ui.p_status.insertItem(1, 'researcher')
        self.ui.p_status.insertItem(2, 'engineer')
        self.ui.p_status.insertItem(3, 'post-doc')
        self.ui.p_status.insertItem(4, 'PhD student')
        self.ui.p_status.insertItem(5, 'master student')
        self.ui.p_status.insertItem(6, 'undergraduate student')
        if labs_previous_data_array[previous_lab_edit - 1]:
            self.ui.p_status.setCurrentIndex(labs_previous_data_array[previous_lab_edit - 1][1])
        # begin date
        self.ui.p_begin_date.setStyleSheet('QDateEdit{border-width: 2px; border-style: solid; '
                                           'border-color: rgb(251,157,111); background-color: rgb(255,250,245); '
                                           'padding: 5px}')
        self.ui.p_begin_date.setDisplayFormat('yyyy-MM-dd')
        if labs_previous_data_array[previous_lab_edit - 1]:
            self.ui.p_begin_date.setDate(
                QDate.fromString(labs_previous_data_array[previous_lab_edit - 1][3], 'yyyy-MM-dd'))
        else:
            self.ui.p_begin_date.setDate(QDate.fromString('1900-01-01', 'yyyy-MM-dd'))
        # end date
        self.ui.p_end_date.setStyleSheet('QDateEdit{border-width: 2px; border-style: solid; '
                                         'border-color: rgb(251,157,111); background-color: rgb(255,250,245); '
                                         'padding: 5px}')
        self.ui.p_end_date.setDisplayFormat('yyyy-MM-dd')
        if labs_previous_data_array[previous_lab_edit - 1]:
            self.ui.p_end_date.setDate(
                QDate.fromString(labs_previous_data_array[previous_lab_edit - 1][4], 'yyyy-MM-dd'))
        else:
            self.ui.p_end_date.setDate(QDate.fromString('1900-01-01', 'yyyy-MM-dd'))
        # additional information
        self.ui.p_lab_comment.setStyleSheet('QTextEdit{border-width: 2px; border-style: solid; '
                                            'border-color: rgb(86,231,200); background-color: rgb(249,255,254); '
                                            'padding: 5px}')
        if labs_previous_data_array[previous_lab_edit - 1]:
            self.ui.p_lab_comment.setPlainText(labs_previous_data_array[previous_lab_edit - 1][5])
        # button
        self.ui.buttonBox.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.clear_btn.setStyleSheet('QPushButton{padding: 5px}')
        self.ui.cancel_btn.setStyleSheet('QPushButton{padding: 5px}')
        # SLOTS & SIGNALS
        self.ui.buttonBox.clicked.connect(self.add_previous_lab_action)
        self.ui.cancel_btn.clicked.connect(self.close_add_lab)
        self.ui.clear_btn.clicked.connect(self.clear_add_lab)
        # WINDOW show
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        self.exec_()

    # SIGNALS functions
    def close_add_lab(self):
        self.close()

    def clear_add_lab(self):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to clear the form?\nAll its data will be lost", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ui.p_lab_acronym.setText('')
            self.ui.p_status.setCurrentIndex(0)
            self.ui.p_begin_date.setDate(QDate.fromString('1900-01-01', 'yyyy-MM-dd'))
            self.ui.p_end_date.setDate(QDate.fromString('1900-01-01', 'yyyy-MM-dd'))
            self.ui.p_lab_comment.setPlainText('')
            labs_previous_data_array[self.previous_lab_edit - 1].clear()

    def add_previous_lab_action(self):
        verification_Ok = 1
        if self.ui.p_lab_acronym.text().strip() == '':
            verification_Ok = 0
            self.dialog_critical('Lab Acronym is mandatory!')
            self.ui.p_lab_acronym.setFocus()
        elif self.ui.p_begin_date.date().toString("yyyy-MM-dd") == '1900-01-01':
            verification_Ok = 0
            self.dialog_critical('Beginning date is mandatory!\nWe need this for DOI')
            self.ui.p_begin_date.setFocus()
        elif self.ui.p_end_date.date().toString("yyyy-MM-dd") == '1900-01-01':
            verification_Ok = 0
            self.dialog_critical('Ending date is mandatory!\nWe need this for DOI')
            self.ui.p_end_date.setFocus()
        if verification_Ok and self.ui.p_status.currentIndex() == 0:
            reply = QMessageBox.question(self, 'Message',
                                         "Are you sure to leave the status empty?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                verification_Ok = 0
                self.ui.p_status.setFocus()
        if verification_Ok:
            if not labs_previous_data_array[self.previous_lab_edit - 1]:
                labs_previous_data_array[self.previous_lab_edit - 1].append(self.ui.p_lab_acronym.text())
                labs_previous_data_array[self.previous_lab_edit - 1].append(self.ui.p_status.currentIndex())
                labs_previous_data_array[self.previous_lab_edit - 1].append(self.ui.p_status.currentText())
                labs_previous_data_array[self.previous_lab_edit - 1].append(
                    self.ui.p_begin_date.date().toString("yyyy-MM-dd"))
                labs_previous_data_array[self.previous_lab_edit - 1].append(
                    self.ui.p_end_date.date().toString("yyyy-MM-dd"))
                labs_previous_data_array[self.previous_lab_edit - 1].append(self.ui.p_lab_comment.toPlainText())
            else:
                labs_previous_data_array[self.previous_lab_edit - 1][0] = self.ui.p_lab_acronym.text()
                labs_previous_data_array[self.previous_lab_edit - 1][1] = self.ui.p_status.currentIndex()
                labs_previous_data_array[self.previous_lab_edit - 1][2] = self.ui.p_status.currentText()
                labs_previous_data_array[self.previous_lab_edit - 1][3] = self.ui.p_begin_date.date().toString(
                    "yyyy-MM-dd")
                labs_previous_data_array[self.previous_lab_edit - 1][4] = self.ui.p_end_date.date().toString(
                    "yyyy-MM-dd")
                labs_previous_data_array[self.previous_lab_edit - 1][5] = self.ui.p_lab_comment.toPlainText()
            self.close()

    # dialog windows
    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('Error!')
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()


app = QtWidgets.QApplication([])
win = XMLTemplateExperimentalist()
win.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
win.show()
sys.exit(app.exec())
