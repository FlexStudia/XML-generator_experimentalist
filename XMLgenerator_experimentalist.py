# coding: utf-8

# IMPORTS
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QDate
from lxml import etree
import sys

# GLOBALS
__version__ = 0.95
__copyright__ = "CC-BY 4.0 (Authors attribution alone required)"
__author_mail__ = "flex.studia.dev@gmail.com"
__bug_support_mail__ = "XML.generator.experimentalist@gmail.com"

# style
font_size = 10

# XML
xml_template = "<?xml version='1.0' encoding='UTF-8'?><!--  Data type : Experimentalist Specific notes : 	- General notes :  	- Most of the tags are optional, you can remove the really unnecessary ones. 	- Tags marked as 'multiple' can be copied (with its block of sub-tag, up to the ending tag) if needed. 	- all blocs marked 'OPTION' can be fully removed if not needed (now or in the future) 	- **ABS MANDATORY / ABS COMPULSORY**: a value need to be absolutely provided, no way to escape! (SSHADE will not function properly if absent). 	- **MANDATORY / COMPULSORY**: very important values for the search of the data. If the value (txt or numeric) of one tag is not known (or irrelevant in your case), then put 'NULL' and write a comment to keep track of the missing value. Remove comment when value is added. 	- **MANDATORY / COMPULSORY only for ...**: when a value is optionally MANDATORY the condition is written.  	- 'LINK to existing UID' (unique identifier): references to another table in SSHADE. You have to reconstruct (easy for some: rule is in comment) or found this existing UID in the database beforehand (use 'Provider/Full Search' menu in SSHADE). 	- 'UID to CREATE': you need to create this UID using their specific rules of creation that are explained in their attached comment. Use only alphanumeric characters and '_'. 	- For UID you can use only alpha-numeric characters and the following: '_', '-' 	- Enumeration type ('Enum' or 'OpenEnum') must contain one single item from the list given in brackets {}. 	- use a CDATA tag when a value contains at least one special character (ie: &, >, <,...). Example: <![CDATA[AT&T]]> for AT&T 	- The data format is noted beetween [] and is 'ascii' when not specified. Ex: [Float], [Integer]. For [float] 2 formats are possible: decimal (123.456) or scientific (1.234e-56)   	- when no numerical format or Enum is specified, it is free text but limited to 256 characters. Only those noted [blob] have no size limitation. 	- to import data for the first time you have to set <import_mode>='first import'. To correct data you have to change it to 'correction'. 	- when a <filename> is given, then the file should be ziped with this xml file for import.  --><import type='experimentalist' ssdm_version='0.9.0' xmlns='http://sshade.eu/schema/import' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='http://sshade.eu/schema/import http://sshade.eu/schema/import-0.9.xsd'><experimentalist><!-- multiple --><import_mode>first import</import_mode> <!-- **ABS MANDATORY** Mode of import of the experimentalist data. Enum: {first import, ignore, draft, no change, correction} --><uid>EXPER_</uid> <!-- **ABS MANDATORY to CREATE** Unique identifier code given to the experimentalist. Should be of the style ‘EXPER_Firstname_Lastname(_n)’ --><manager_databases> <!-- **ABS MANDATORY at least one** --><database_uid>DB_</database_uid> <!-- **ABS MANDATORY** LINK to the existing UID of the database which manages the experimentalist information [‘DB_DatabaseAcronym’] -->	</manager_databases><!-- EXPERIMENTALIST NAME --><first_name></first_name> <!-- **ABS MANDATORY, requested for DOI** First name (given name) --><family_name></family_name> <!-- **ABS MANDATORY, requested for DOI** Family name (last name) --><acronym></acronym> <!-- **MANDATORY** Initials of first and last name. Ex: BS, FROD --><orcid_identifier></orcid_identifier> <!-- **MANDATORY** ORCID identifier code that uniquely identify the experimentalist --><alternate_identifiers> <!-- **OPTION** --><alternate_identifier><!-- multiple --><scheme></scheme> <!-- **ABS MANDATORY in OPTION** Alternate scheme that provideds the unique identifiers of the experimentalist. Enum: {ISNI, ResearcherID, ScopusAuthorID} --><code></code> <!-- **ABS MANDATORY in OPTION** Alternate code that uniquely identify the experimentalist in this scheme --></alternate_identifier></alternate_identifiers><state>active</state> <!-- XXX-BS 090a NEW **ABS MANDATORY** State of activity of the experimentalist. Enum: {active, inactive, retired, deceased}. default = ‘active’ --><!-- EXPERIMENTALIST LABORATORIES --><laboratories> <!-- **ABS MANDATORY at least one** Put in chronological order --><laboratory state='current'><!-- multiple --> <!-- **ABS MANDATORY, at least one 'current' for 'active', all 'previous' for others** Enum of 'state': {previous, current} --><uid></uid> <!-- **ABS MANDATORY** LINK to the existing UID of the current laboratory where the experimentalist works [‘LAB_LabAcronym’] --><status></status> <!-- **MANDATORY for current laboratory** Status of the experimentalist in this laboratory. Enum: {researcher, engineer, post-doc, PhD student, master student, undergraduate student} --><date_begin></date_begin> <!-- **ABS MANDATORY for current lab** Beginning date of the experimentalist in this laboratory. [Format: ‘YYYY-MM-DD’] Ex: '1999-10-05' --><date_end></date_end> <!-- **ABS MANDATORY for previous lab** Ending date of the experimentalist in this laboratory. [Format: ‘YYYY-MM-DD’] Ex: '1999-10-05', '' --><comments><![CDATA[]]></comments> <!-- Additional information ... [blob] --></laboratory></laboratories><!-- EXPERIMENTALIST CONTACTS --><email></email> <!-- **MANDATORY** Current e-mail of the experimentalist. Will be used as login --><phone></phone> <!-- Current phone number of the experimentalist. ex: +33(0)7 06 05 04 01 --><links> <!-- **OPTION** Link(s) to current web page(s) of the experimentalist --><link><!-- multiple --> <name><![CDATA[]]></name> <!-- Name of the web page(s) --><url><![CDATA[]]></url> <!-- **MANDATORY in OPTION** URL address (avoid non-perennial commercial URL) --></link></links><comments><![CDATA[]]></comments> <!-- Additional information on the experimentalist [blob] --></experimentalist></import>"

# global arrays
labs_current_data_array = [[], [], [], []]
labs_previous_data_array = [[], [], [], [], [], []]


# MAIN WINDOW interface
class Ui_experimentalist_window(object):
    def setupUi(self, experimentalist_window):
        experimentalist_window.setObjectName("experimentalist_window")
        experimentalist_window.resize(477, 679)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(experimentalist_window.sizePolicy().hasHeightForWidth())
        experimentalist_window.setSizePolicy(sizePolicy)
        experimentalist_window.setMinimumSize(QtCore.QSize(475, 0))
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        experimentalist_window.setFont(font)
        experimentalist_window.setSizeGripEnabled(False)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(experimentalist_window)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.about_btn = QtWidgets.QPushButton(experimentalist_window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.about_btn.sizePolicy().hasHeightForWidth())
        self.about_btn.setSizePolicy(sizePolicy)
        self.about_btn.setMaximumSize(QtCore.QSize(25, 16777215))
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.about_btn.setFont(font)
        self.about_btn.setObjectName("about_btn")
        self.gridLayout_8.addWidget(self.about_btn, 0, 1, 1, 1)
        self.header = QtWidgets.QLabel(experimentalist_window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') + 8)
        self.header.setFont(font)
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.header.setObjectName("header")
        self.gridLayout_8.addWidget(self.header, 0, 0, 1, 1)
        self.XML_type_label = QtWidgets.QLabel(experimentalist_window)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.XML_type_label.setFont(font)
        self.XML_type_label.setTextFormat(QtCore.Qt.AutoText)
        self.XML_type_label.setScaledContents(False)
        self.XML_type_label.setAlignment(QtCore.Qt.AlignCenter)
        self.XML_type_label.setObjectName("XML_type_label")
        self.gridLayout_8.addWidget(self.XML_type_label, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_8)
        self.tabWidget = QtWidgets.QTabWidget(experimentalist_window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.label_7 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        self.first_name = QtWidgets.QLineEdit(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.first_name.setFont(font)
        self.first_name.setStyleSheet("border-color: rgb(255, 85, 0);")
        self.first_name.setObjectName("first_name")
        self.gridLayout.addWidget(self.first_name, 2, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 7, 0, 1, 1)
        self.email = QtWidgets.QLineEdit(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.email.setFont(font)
        self.email.setObjectName("email")
        self.gridLayout.addWidget(self.email, 6, 0, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') + 1)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.gridLayout.addWidget(self.label_21, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_5.setFont(font)
        self.label_5.setToolTip("")
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.family_name = QtWidgets.QLineEdit(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.family_name.setFont(font)
        self.family_name.setObjectName("family_name")
        self.gridLayout.addWidget(self.family_name, 4, 0, 1, 1)
        self.phone = QtWidgets.QLineEdit(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.phone.setFont(font)
        self.phone.setObjectName("phone")
        self.gridLayout.addWidget(self.phone, 8, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 9, 0, 1, 1)
        self.comments_contact = QtWidgets.QTextEdit(self.tab)
        self.comments_contact.setMaximumSize(QtCore.QSize(16777215, 150))
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.comments_contact.setFont(font)
        self.comments_contact.setOverwriteMode(True)
        self.comments_contact.setTabStopWidth(80)
        self.comments_contact.setObjectName("comments_contact")
        self.gridLayout.addWidget(self.comments_contact, 10, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_ISNI = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_ISNI.setFont(font)
        self.label_ISNI.setObjectName("label_ISNI")
        self.gridLayout_2.addWidget(self.label_ISNI, 3, 0, 1, 1, QtCore.Qt.AlignBottom)
        self.label_ResearcherID = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_ResearcherID.setFont(font)
        self.label_ResearcherID.setObjectName("label_ResearcherID")
        self.gridLayout_2.addWidget(self.label_ResearcherID, 5, 0, 1, 1, QtCore.Qt.AlignBottom)
        self.ORCID = QtWidgets.QLineEdit(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.ORCID.setFont(font)
        self.ORCID.setObjectName("ORCID")
        self.gridLayout_2.addWidget(self.ORCID, 2, 0, 1, 1, QtCore.Qt.AlignTop)
        self.label_ORCIDE = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_ORCIDE.setFont(font)
        self.label_ORCIDE.setObjectName("label_ORCIDE")
        self.gridLayout_2.addWidget(self.label_ORCIDE, 1, 0, 1, 1, QtCore.Qt.AlignBottom)
        self.ISNI = QtWidgets.QLineEdit(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.ISNI.setFont(font)
        self.ISNI.setObjectName("ISNI")
        self.gridLayout_2.addWidget(self.ISNI, 4, 0, 1, 1, QtCore.Qt.AlignTop)
        self.label_22 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') + 1)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.gridLayout_2.addWidget(self.label_22, 0, 0, 1, 1, QtCore.Qt.AlignTop)
        self.ResearcherID = QtWidgets.QLineEdit(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.ResearcherID.setFont(font)
        self.ResearcherID.setObjectName("ResearcherID")
        self.gridLayout_2.addWidget(self.ResearcherID, 6, 0, 1, 1, QtCore.Qt.AlignTop)
        self.ScopusAuthorID = QtWidgets.QLineEdit(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.ScopusAuthorID.setFont(font)
        self.ScopusAuthorID.setObjectName("ScopusAuthorID")
        self.gridLayout_2.addWidget(self.ScopusAuthorID, 8, 0, 1, 1, QtCore.Qt.AlignTop)
        self.label_ScopusAuthorID = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_ScopusAuthorID.setFont(font)
        self.label_ScopusAuthorID.setObjectName("label_ScopusAuthorID")
        self.gridLayout_2.addWidget(self.label_ScopusAuthorID, 7, 0, 1, 1, QtCore.Qt.AlignBottom)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 9, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') + 1)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_23 = QtWidgets.QLabel(self.tab_3)
        self.label_23.setObjectName("label_23")
        self.verticalLayout.addWidget(self.label_23)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.link_name_1 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_name_1.setFont(font)
        self.link_name_1.setObjectName("link_name_1")
        self.gridLayout_5.addWidget(self.link_name_1, 0, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 0, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.tab_3)
        self.label_11.setMinimumSize(QtCore.QSize(0, 0))
        self.label_11.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout_5.addWidget(self.label_11, 1, 0, 1, 1)
        self.link_url_1 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_url_1.setFont(font)
        self.link_url_1.setObjectName("link_url_1")
        self.gridLayout_5.addWidget(self.link_url_1, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_5)
        self.label_2 = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_12 = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 1)
        self.link_name_2 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_name_2.setFont(font)
        self.link_name_2.setObjectName("link_name_2")
        self.gridLayout_3.addWidget(self.link_name_2, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.tab_3)
        self.label_13.setMinimumSize(QtCore.QSize(0, 0))
        self.label_13.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 1, 0, 1, 1)
        self.link_url_2 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_url_2.setFont(font)
        self.link_url_2.setObjectName("link_url_2")
        self.gridLayout_3.addWidget(self.link_url_2, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.label_3 = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_14 = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.gridLayout_6.addWidget(self.label_14, 0, 0, 1, 1)
        self.link_name_3 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_name_3.setFont(font)
        self.link_name_3.setObjectName("link_name_3")
        self.gridLayout_6.addWidget(self.link_name_3, 0, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.tab_3)
        self.label_15.setMinimumSize(QtCore.QSize(0, 0))
        self.label_15.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.gridLayout_6.addWidget(self.label_15, 1, 0, 1, 1)
        self.link_url_3 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_url_3.setFont(font)
        self.link_url_3.setObjectName("link_url_3")
        self.gridLayout_6.addWidget(self.link_url_3, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_6)
        self.label_4 = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_16 = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.gridLayout_7.addWidget(self.label_16, 0, 0, 1, 1)
        self.link_name_4 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_name_4.setFont(font)
        self.link_name_4.setObjectName("link_name_4")
        self.gridLayout_7.addWidget(self.link_name_4, 0, 1, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.tab_3)
        self.label_17.setMinimumSize(QtCore.QSize(0, 0))
        self.label_17.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.gridLayout_7.addWidget(self.label_17, 1, 0, 1, 1)
        self.link_url_4 = QtWidgets.QLineEdit(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.link_url_4.setFont(font)
        self.link_url_4.setObjectName("link_url_4")
        self.gridLayout_7.addWidget(self.link_url_4, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_7)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_4)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_18 = QtWidgets.QLabel(self.tab_4)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_4.addWidget(self.label_18, 1, 0, 1, 1)
        self.c_lab_btn_1 = QtWidgets.QPushButton(self.tab_4)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_lab_btn_1.setFont(font)
        self.c_lab_btn_1.setObjectName("c_lab_btn_1")
        self.gridLayout_4.addWidget(self.c_lab_btn_1, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem1, 6, 0, 1, 1)
        self.c_lab_btn_3 = QtWidgets.QPushButton(self.tab_4)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_lab_btn_3.setFont(font)
        self.c_lab_btn_3.setObjectName("c_lab_btn_3")
        self.gridLayout_4.addWidget(self.c_lab_btn_3, 4, 0, 1, 1)
        self.c_lab_btn_2 = QtWidgets.QPushButton(self.tab_4)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_lab_btn_2.setFont(font)
        self.c_lab_btn_2.setObjectName("c_lab_btn_2")
        self.gridLayout_4.addWidget(self.c_lab_btn_2, 3, 0, 1, 1)
        self.c_lab_btn_4 = QtWidgets.QPushButton(self.tab_4)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_lab_btn_4.setFont(font)
        self.c_lab_btn_4.setObjectName("c_lab_btn_4")
        self.gridLayout_4.addWidget(self.c_lab_btn_4, 5, 0, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.tab_4)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') + 1)
        self.label_24.setFont(font)
        self.label_24.setObjectName("label_24")
        self.gridLayout_4.addWidget(self.label_24, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_25 = QtWidgets.QLabel(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') + 1)
        self.label_25.setFont(font)
        self.label_25.setObjectName("label_25")
        self.verticalLayout_7.addWidget(self.label_25)
        self.label_19 = QtWidgets.QLabel(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.verticalLayout_7.addWidget(self.label_19)
        self.p_lab_btn_1 = QtWidgets.QPushButton(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_btn_1.setFont(font)
        self.p_lab_btn_1.setObjectName("p_lab_btn_1")
        self.verticalLayout_7.addWidget(self.p_lab_btn_1)
        self.p_lab_btn_2 = QtWidgets.QPushButton(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_btn_2.setFont(font)
        self.p_lab_btn_2.setObjectName("p_lab_btn_2")
        self.verticalLayout_7.addWidget(self.p_lab_btn_2)
        self.p_lab_btn_3 = QtWidgets.QPushButton(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_btn_3.setFont(font)
        self.p_lab_btn_3.setObjectName("p_lab_btn_3")
        self.verticalLayout_7.addWidget(self.p_lab_btn_3)
        self.p_lab_btn_4 = QtWidgets.QPushButton(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_btn_4.setFont(font)
        self.p_lab_btn_4.setObjectName("p_lab_btn_4")
        self.verticalLayout_7.addWidget(self.p_lab_btn_4)
        self.p_lab_btn_5 = QtWidgets.QPushButton(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_btn_5.setFont(font)
        self.p_lab_btn_5.setObjectName("p_lab_btn_5")
        self.verticalLayout_7.addWidget(self.p_lab_btn_5)
        self.p_lab_btn_6 = QtWidgets.QPushButton(self.tab_5)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_btn_6.setFont(font)
        self.p_lab_btn_6.setObjectName("p_lab_btn_6")
        self.verticalLayout_7.addWidget(self.p_lab_btn_6)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem2)
        self.tabWidget.addTab(self.tab_5, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.label_20 = QtWidgets.QLabel(experimentalist_window)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}') - 2)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.verticalLayout_2.addWidget(self.label_20)
        self.buttonBox = QtWidgets.QPushButton(experimentalist_window)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(experimentalist_window)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(experimentalist_window)
        experimentalist_window.setTabOrder(self.first_name, self.family_name)
        experimentalist_window.setTabOrder(self.family_name, self.email)
        experimentalist_window.setTabOrder(self.email, self.phone)
        experimentalist_window.setTabOrder(self.phone, self.comments_contact)
        experimentalist_window.setTabOrder(self.comments_contact, self.ORCID)
        experimentalist_window.setTabOrder(self.ORCID, self.ISNI)
        experimentalist_window.setTabOrder(self.ISNI, self.ResearcherID)
        experimentalist_window.setTabOrder(self.ResearcherID, self.ScopusAuthorID)
        experimentalist_window.setTabOrder(self.ScopusAuthorID, self.link_name_1)
        experimentalist_window.setTabOrder(self.link_name_1, self.link_url_1)
        experimentalist_window.setTabOrder(self.link_url_1, self.link_name_2)
        experimentalist_window.setTabOrder(self.link_name_2, self.link_url_2)
        experimentalist_window.setTabOrder(self.link_url_2, self.link_name_3)
        experimentalist_window.setTabOrder(self.link_name_3, self.link_url_3)
        experimentalist_window.setTabOrder(self.link_url_3, self.link_name_4)
        experimentalist_window.setTabOrder(self.link_name_4, self.link_url_4)
        experimentalist_window.setTabOrder(self.link_url_4, self.c_lab_btn_1)
        experimentalist_window.setTabOrder(self.c_lab_btn_1, self.c_lab_btn_2)
        experimentalist_window.setTabOrder(self.c_lab_btn_2, self.c_lab_btn_3)
        experimentalist_window.setTabOrder(self.c_lab_btn_3, self.c_lab_btn_4)
        experimentalist_window.setTabOrder(self.c_lab_btn_4, self.p_lab_btn_1)
        experimentalist_window.setTabOrder(self.p_lab_btn_1, self.p_lab_btn_2)
        experimentalist_window.setTabOrder(self.p_lab_btn_2, self.p_lab_btn_3)
        experimentalist_window.setTabOrder(self.p_lab_btn_3, self.p_lab_btn_4)
        experimentalist_window.setTabOrder(self.p_lab_btn_4, self.p_lab_btn_5)
        experimentalist_window.setTabOrder(self.p_lab_btn_5, self.p_lab_btn_6)
        experimentalist_window.setTabOrder(self.p_lab_btn_6, self.buttonBox)

    def retranslateUi(self, experimentalist_window):
        _translate = QtCore.QCoreApplication.translate
        experimentalist_window.setWindowTitle(_translate("experimentalist_window",
                                                         "SSHADE Experimentalist XML template"))
        self.about_btn.setText(_translate("experimentalist_window", "?"))
        self.header.setText(_translate("experimentalist_window", "SSHADE XML generator"))
        self.XML_type_label.setText(_translate("experimentalist_window",
                                               "<html><head/><body><p>Experimentalist template</p></body></html>"))
        self.label_7.setText(_translate("experimentalist_window", "Email *"))
        self.label_6.setText(_translate("experimentalist_window", "Family name **"))
        self.first_name.setToolTip(_translate("experimentalist_window",
                                              "<html><head/><body><p>Experimentalist First (Given) name</p>"
                                              "</body></html>"))
        self.first_name.setWhatsThis(_translate("experimentalist_window",
                                                "<html><head/><body><p><br/></p></body></html>"))
        self.label_8.setText(_translate("experimentalist_window", "Phone"))
        self.email.setToolTip(_translate("experimentalist_window",
                                         "<html><head/><body>Experimentalist Email</body></html>"))
        self.label_21.setText(_translate("experimentalist_window", "Experimentalist\'s information"))
        self.label_5.setText(_translate("experimentalist_window", "First name **"))
        self.family_name.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>Experimentalist Family (Last) name</body></html>"))
        self.phone.setToolTip(_translate("experimentalist_window",
                                         "<html><head/><body>Experimental phone in international format</body></html>"))
        self.label_9.setText(_translate("experimentalist_window", "Any additional information"))
        self.comments_contact.setToolTip(_translate("experimentalist_window",
                                                    "<html><head/><body>"
                                                    "<p>Any additional information about the experimentalist</p>"
                                                    "</body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("experimentalist_window", "1 Info"))
        self.label_ISNI.setText(_translate("experimentalist_window", "ISNI"))
        self.label_ResearcherID.setText(_translate("experimentalist_window", "Researcher ID"))
        self.ORCID.setToolTip(_translate("experimentalist_window",
                                         "<html><head/><body>"
                                         "<p>Experimentalist ORCID, Open Researcher and Contributor ID, if available</p>"
                                         "</body></html>"))
        self.label_ORCIDE.setText(_translate("experimentalist_window", "ORCID identifier *"))
        self.ISNI.setToolTip(_translate("experimentalist_window",
                                        "<html><head/><body>"
                                        "<p>Experimentalist ISNI (International Standard Name Identifier) if available</p>"
                                        "</body></html>"))
        self.label_22.setText(_translate("experimentalist_window", "Experimentalist\'s identifiers"))
        self.ResearcherID.setToolTip(_translate("experimentalist_window",
                                                "<html><head/><body><p>Experimentalist Researcher ID if available</p>"
                                                "</body></html>"))
        self.ScopusAuthorID.setToolTip(_translate("experimentalist_window",
                                                  "<html><head/><body>"
                                                  "<p>Experimentalist Scopus Author ID if available</p></body></html>"))
        self.label_ScopusAuthorID.setText(_translate("experimentalist_window", "Scopus Author ID"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("experimentalist_window", "2 Idents"))
        self.label.setText(_translate("experimentalist_window", "Experimentalist professional web page"))
        self.label_23.setText(_translate("experimentalist_window", "Experimentalist\'s web page(s)"))
        self.link_name_1.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Web page title, i.e. John Doe\'s professional web page</p>"
                                               "</body></html>"))
        self.label_10.setText(_translate("experimentalist_window", "name"))
        self.label_11.setText(_translate("experimentalist_window", "URL "))
        self.link_url_1.setToolTip(_translate("experimentalist_window",
                                              "<html><head/><body><p>web address of the page</p></body></html>"))
        self.label_2.setText(_translate("experimentalist_window", "Experimentalist personal web page"))
        self.label_12.setText(_translate("experimentalist_window", "name"))
        self.link_name_2.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Web page title, i.e. John Doe\'s strange science</p></body></html>"))
        self.label_13.setText(_translate("experimentalist_window", "URL "))
        self.link_url_2.setToolTip(_translate("experimentalist_window",
                                              "<html><head/><body><p>web address of the page</p></body></html>"))
        self.label_3.setText(_translate("experimentalist_window", "Other web page (project, ...)"))
        self.label_14.setText(_translate("experimentalist_window", "name"))
        self.link_name_3.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Web page title, i.e. John Doe\'s Gray Matter project</p>"
                                               "</body></html>"))
        self.label_15.setText(_translate("experimentalist_window", "URL "))
        self.link_url_3.setToolTip(_translate("experimentalist_window",
                                              "<html><head/><body><p>web address of the page</p></body></html>"))
        self.label_4.setText(_translate("experimentalist_window", "Other web page (ResearchGate, LinkedIn, ...)"))
        self.label_16.setText(_translate("experimentalist_window", "name"))
        self.link_name_4.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Web page title, i.e. John Doe\'s LinkedIn page</p></body></html>"))
        self.label_17.setText(_translate("experimentalist_window", "URL "))
        self.link_url_4.setToolTip(_translate("experimentalist_window",
                                              "<html><head/><body><p>web address of the page</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("experimentalist_window", "3 Links"))
        self.label_18.setText(_translate("experimentalist_window",
                                         "Please, provide all laboratories in which you are currently affiliated. \n"
                                         "At least one laboratory must be given"))
        self.c_lab_btn_1.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body><p>Add a current laboratory</p></body></html>"))
        self.c_lab_btn_1.setText(_translate("experimentalist_window", "Your main current laboratory"))
        self.c_lab_btn_3.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add one more current laboratory</p></body></html>"))
        self.c_lab_btn_3.setText(_translate("experimentalist_window", "Current Lab 3"))
        self.c_lab_btn_2.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add another current laboratory</p></body></html>"))
        self.c_lab_btn_2.setText(_translate("experimentalist_window", "Current Lab 2"))
        self.c_lab_btn_4.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add one more current laboratory</p></body></html>"))
        self.c_lab_btn_4.setText(_translate("experimentalist_window", "Current Lab 4"))
        self.label_24.setText(_translate("experimentalist_window", "Experimentalist\'s current laboratories"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("experimentalist_window", "4 Current"))
        self.label_25.setText(_translate("experimentalist_window", "Experimentalist\'s previous laboratories"))
        self.label_19.setText(_translate("experimentalist_window",
                                         "Please, provide all your previously affiliated laboratories\n"
                                         "in which you were producing lab data"))
        self.p_lab_btn_1.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body><p>Add a previous laboratory</p></body></html>"))
        self.p_lab_btn_1.setText(_translate("experimentalist_window", "Previous Lab 1"))
        self.p_lab_btn_2.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add another previous laboratory</p></body></html>"))
        self.p_lab_btn_2.setText(_translate("experimentalist_window", "Previous Lab 2"))
        self.p_lab_btn_3.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add one more previous laboratory</p></body></html>"))
        self.p_lab_btn_3.setText(_translate("experimentalist_window", "Previous Lab 3"))
        self.p_lab_btn_4.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add one more previous laboratory</p></body></html>"))
        self.p_lab_btn_4.setText(_translate("experimentalist_window", "Previous Lab 4"))
        self.p_lab_btn_5.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add one more previous laboratory</p></body></html>"))
        self.p_lab_btn_5.setText(_translate("experimentalist_window", "Previous Lab 5"))
        self.p_lab_btn_6.setToolTip(_translate("experimentalist_window",
                                               "<html><head/><body>"
                                               "<p>Add one more previous laboratory</p></body></html>"))
        self.p_lab_btn_6.setText(_translate("experimentalist_window", "Previous Lab 6"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5),
                                  _translate("experimentalist_window", "5 Previous"))
        self.label_20.setText(_translate("experimentalist_window", "**: This information is mandatory\n"
                                                                   "*: This information is recommended"))
        self.buttonBox.setText(_translate("experimentalist_window", "Fill the XML template with this information"))


# MAIN WINDOW class
class XMLTemplateExperimentalist(QtWidgets.QDialog):
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
        # about button
        self.ui.about_btn.clicked.connect(self.about_info)

    def about_info(self):
        self.dialog_ok(f"<b>XML generator: experimentalist</b> v{__version__}"
                       f"<p>Copyright: {__copyright__}</p>"
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
        if self.ui.first_name.text().strip() == '':
            AbsMandatoryWarning('First name', '')
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.first_name.setFocus()
        elif self.ui.family_name.text().strip() == '':
            AbsMandatoryWarning('Family name', '')
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.family_name.setFocus()
        elif labs_current_data_array[0] == [] and labs_current_data_array[1] == [] and labs_current_data_array[2] == [] \
                and labs_current_data_array[3] == []:
            AbsMandatoryWarning('At least on current lab', '')
            self.ui.tabWidget.setCurrentIndex(3)
            self.ui.c_lab_btn_1.setFocus()
        else:
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
                SavingOK()


# CURRENT labs window
class Ui_CurrentLab(object):
    def setupUi(self, CurrentLab):
        CurrentLab.setObjectName("CurrentLab")
        CurrentLab.resize(445, 359)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        CurrentLab.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(CurrentLab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_10 = QtWidgets.QLabel(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.verticalLayout.addWidget(self.label_10)
        self.c_lab_acronym = QtWidgets.QLineEdit(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_lab_acronym.setFont(font)
        self.c_lab_acronym.setObjectName("c_lab_acronym")
        self.verticalLayout.addWidget(self.c_lab_acronym)
        self.label = QtWidgets.QLabel(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.c_status = QtWidgets.QComboBox(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_status.setFont(font)
        self.c_status.setObjectName("c_status")
        self.verticalLayout.addWidget(self.c_status)
        self.label_12 = QtWidgets.QLabel(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.verticalLayout.addWidget(self.label_12)
        self.c_begin_date = QtWidgets.QDateEdit(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_begin_date.setFont(font)
        self.c_begin_date.setObjectName("c_begin_date")
        self.verticalLayout.addWidget(self.c_begin_date)
        self.label_13 = QtWidgets.QLabel(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.verticalLayout.addWidget(self.label_13)
        self.c_lab_comment = QtWidgets.QTextEdit(CurrentLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.c_lab_comment.setFont(font)
        self.c_lab_comment.setObjectName("c_lab_comment")
        self.verticalLayout.addWidget(self.c_lab_comment)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.buttonBox = QtWidgets.QPushButton(CurrentLab)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.clear_btn = QtWidgets.QPushButton(CurrentLab)
        self.clear_btn.setObjectName("clear_btn")
        self.horizontalLayout_2.addWidget(self.clear_btn)
        self.cancel_btn = QtWidgets.QPushButton(CurrentLab)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout_2.addWidget(self.cancel_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(CurrentLab)
        QtCore.QMetaObject.connectSlotsByName(CurrentLab)

    def retranslateUi(self, CurrentLab):
        _translate = QtCore.QCoreApplication.translate
        CurrentLab.setWindowTitle(_translate("CurrentLab", "Current Lab 1"))
        self.label_10.setText(_translate("CurrentLab", "Lab Acronym **"))
        self.c_lab_acronym.setToolTip(_translate("CurrentLab",
                                                 "<html><head/><body>"
                                                 "<p>Experimentalist laboratory acronym</p></body></html>"))
        self.label.setText(_translate("CurrentLab", "Status *"))
        self.c_status.setToolTip(_translate("CurrentLab",
                                            "<html><head/><body>"
                                            "<p>Experimentalist\'s status in this laboratory</p></body></html>"))
        self.label_12.setText(_translate("CurrentLab", "Beginning date **"))
        self.c_begin_date.setToolTip(_translate("CurrentLab",
                                                "<html><head/><body>"
                                                "<p>Format: YYYY-MM-DD, beginning date of the experimentalist in this laboratory (<span style=\" font-weight:600;\">needed for DOI</span>)</p></body></html>"))
        self.label_13.setText(_translate("CurrentLab", "Additional information"))
        self.c_lab_comment.setToolTip(_translate("CurrentLab",
                                                 "<html><head/><body>"
                                                 "<p>Any additional information on this laboratory</p></body></html>"))
        self.buttonBox.setText(_translate("CurrentLab", "Save and Close"))
        self.clear_btn.setText(_translate("CurrentLab", "Clear this form"))
        self.cancel_btn.setText(_translate("CurrentLab", "Close without change"))


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
        if self.ui.c_lab_acronym.text().strip() == '':
            AbsMandatoryWarning('Lab Acronym', '')
            self.ui.c_lab_acronym.setFocus()
        elif self.ui.c_begin_date.date().toString("yyyy-MM-dd") == '1900-01-01':
            AbsMandatoryWarning('Beginning date', 'We need this for DOI')
            self.ui.c_begin_date.setFocus()
        else:
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


# PREVIOUS labs template
class Ui_PreviousLab(object):
    def setupUi(self, PreviousLab):
        PreviousLab.setObjectName("PreviousLab")
        PreviousLab.resize(445, 420)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        PreviousLab.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(PreviousLab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_10 = QtWidgets.QLabel(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.verticalLayout.addWidget(self.label_10)
        self.p_lab_acronym = QtWidgets.QLineEdit(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_acronym.setFont(font)
        self.p_lab_acronym.setObjectName("p_lab_acronym")
        self.verticalLayout.addWidget(self.p_lab_acronym)
        self.label_2 = QtWidgets.QLabel(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.p_status = QtWidgets.QComboBox(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_status.setFont(font)
        self.p_status.setObjectName("p_status")
        self.verticalLayout.addWidget(self.p_status)
        self.label_12 = QtWidgets.QLabel(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.verticalLayout.addWidget(self.label_12)
        self.p_begin_date = QtWidgets.QDateEdit(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_begin_date.setFont(font)
        self.p_begin_date.setObjectName("p_begin_date")
        self.verticalLayout.addWidget(self.p_begin_date)
        self.label = QtWidgets.QLabel(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.p_end_date = QtWidgets.QDateEdit(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_end_date.setFont(font)
        self.p_end_date.setObjectName("p_end_date")
        self.verticalLayout.addWidget(self.p_end_date)
        self.label_13 = QtWidgets.QLabel(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.verticalLayout.addWidget(self.label_13)
        self.p_lab_comment = QtWidgets.QTextEdit(PreviousLab)
        font = QtGui.QFont()
        font.setPointSize(int(f'{font_size}'))
        self.p_lab_comment.setFont(font)
        self.p_lab_comment.setObjectName("p_lab_comment")
        self.verticalLayout.addWidget(self.p_lab_comment)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.buttonBox = QtWidgets.QPushButton(PreviousLab)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.clear_btn = QtWidgets.QPushButton(PreviousLab)
        self.clear_btn.setObjectName("clear_btn")
        self.horizontalLayout_2.addWidget(self.clear_btn)
        self.cancel_btn = QtWidgets.QPushButton(PreviousLab)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout_2.addWidget(self.cancel_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(PreviousLab)
        QtCore.QMetaObject.connectSlotsByName(PreviousLab)

    def retranslateUi(self, PreviousLab):
        _translate = QtCore.QCoreApplication.translate
        PreviousLab.setWindowTitle(_translate("PreviousLab", "Previous Lab 1"))
        self.label_10.setText(_translate("PreviousLab", "Lab Acronym **"))
        self.p_lab_acronym.setToolTip(_translate("PreviousLab",
                                                 "<html><head/><body>"
                                                 "<p>Experimentalist laboratory acronym</p></body></html>"))
        self.label_2.setText(_translate("PreviousLab", "Status *"))
        self.p_status.setToolTip(_translate("PreviousLab",
                                            "<html><head/><body>"
                                            "<p>Experimentalist\'s status in this laboratory</p></body></html>"))
        self.label_12.setText(_translate("PreviousLab", "Beginning date **"))
        self.p_begin_date.setToolTip(_translate("PreviousLab",
                                                "<html><head/><body>"
                                                "<p>Format: YYYY-MM-DD, beginning date of the experimentalist in this laboratory (<span style=\" font-weight:600;\">needed for DOI</span>)</p></body></html>"))
        self.label.setText(_translate("PreviousLab", "Ending date **"))
        self.p_end_date.setToolTip(_translate("PreviousLab",
                                              "<html><head/><body>"
                                              "<p>Format: YYYY-MM-DD, ending date of the experimentalist in this laboratory (<span style=\" font-weight:600;\">needed for DOI</span>)</p></body></html>"))
        self.label_13.setText(_translate("PreviousLab", "Additional information"))
        self.p_lab_comment.setToolTip(_translate("PreviousLab",
                                                 "<html><head/><body>"
                                                 "<p>Any additional information on this laboratory</p></body></html>"))
        self.buttonBox.setText(_translate("PreviousLab", "Save and Close"))
        self.clear_btn.setText(_translate("PreviousLab", "Clear this form"))
        self.cancel_btn.setText(_translate("PreviousLab", "Close without change"))


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
        if self.ui.p_lab_acronym.text().strip() == '':
            AbsMandatoryWarning('Lab Acronym', '')
            self.ui.p_lab_acronym.setFocus()
        elif self.ui.p_begin_date.date().toString("yyyy-MM-dd") == '1900-01-01':
            AbsMandatoryWarning('Beginning date', 'We need this for DOI')
            self.ui.p_begin_date.setFocus()
        elif self.ui.p_end_date.date().toString("yyyy-MM-dd") == '1900-01-01':
            AbsMandatoryWarning('Ending date', 'We need this for DOI')
            self.ui.p_end_date.setFocus()
        else:
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


# MANDATORY warning CLASS
class AbsMandatoryWarning(QtWidgets.QDialog):
    def __init__(self, warning_type, warning_masg):
        super(AbsMandatoryWarning, self).__init__()
        # GUI
        # window
        self.setMinimumSize(275, 151)
        self.setWindowTitle('Warning!')
        # label
        self.label_warning = QLabel()
        self.label_warning.setStyleSheet('QLabel{color: rgb(228,76,0)}')
        if warning_masg == "":
            self.label_warning.setText(f'{warning_type} is mandatory!')
        else:
            self.label_warning.setText(f'{warning_type} is mandatory!\n{warning_masg}')
            # button
        self.ok_btn = QPushButton('Ok')
        self.ok_btn.setStyleSheet('QPushButton{padding: 5px;}')
        # layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.label_warning)
        self.main_layout.addWidget(self.ok_btn)
        self.setLayout(self.main_layout)
        # SIGNALS & SLOTS
        self.ok_btn.clicked.connect(self.close_window)
        # WINDOW SHOW
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        self.exec_()

    # SIGNALS
    def close_window(self):
        self.close()


# OK warning CLASS
class SavingOK(QtWidgets.QDialog):
    def __init__(self):
        super(SavingOK, self).__init__()
        # GUI
        # window
        self.setMinimumSize(262, 151)
        self.setWindowTitle('Saved!')
        # label
        self.label_warning = QLabel('The XML was saved!')
        self.label_warning.setStyleSheet('QLabel{color: rgb(0,148,116)}')
        # button
        self.ok_btn = QPushButton('Ok')
        self.ok_btn.setStyleSheet('QPushButton{padding: 5px;}')
        # layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.label_warning)
        self.main_layout.addWidget(self.ok_btn)
        self.setLayout(self.main_layout)
        # SIGNALS & SLOTS
        self.ok_btn.clicked.connect(self.close_window)
        # WINDOW SHOW
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        self.exec_()

    # SIGNALS
    def close_window(self):
        self.close()


app = QtWidgets.QApplication([])
win = XMLTemplateExperimentalist()
win.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
win.show()
sys.exit(app.exec())
