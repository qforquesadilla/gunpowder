import os
import sys
import json
from functools import partial

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QComboBox, QTableWidgetItem
from PySide2.QtCore import QFile

from gunpowderApi import GunpowderApi


'''
Gunpowder
'''


class Gunpowder(object):

    def __init__(self):
        '''
        TBA
        '''

        # variables
        self.__sgCredentials = {'url': None, 'login': None, 'password': None}
        self.__conditions = {}
        self.__demo = True

        # config
        self.__toolRootDir = os.path.normpath((os.path.dirname(__file__)))
        self.__configPath = os.path.normpath(os.path.join(self.__toolRootDir, 'data/config.json'))
        self.__cachePath = os.path.normpath(os.path.join(self.__toolRootDir, 'data/cache.json'))
        self.__demoPath = os.path.normpath(os.path.join(self.__toolRootDir, 'data/demo.json'))
        self.__setupConfig()

        # ui & commands
        self.__buildUi()
        self.__linkCommands()

        # startup
        self.__startup()

        print('\n\n#############\n# GUNPOWDER #\n#############\n')
        sys.exit(self.__app.exec_())


    def __setupConfig(self):
        '''
        TBA
        '''

        # load json
        configData = self.__readJson(self.__configPath)

        # restore values
        url = configData.get('url', None)
        login = configData.get('login', None)
        password = configData.get('password', None)
        self.__sgCredentials = {'url': url, 'login': login, 'password': password}
        self.__conditions = configData.get('conditions', None)
        self.__demo = configData.get('demo', None)
        self.__entityFieldData = {}


    def __buildUi(self):
        '''
        TBA
        '''

        # define ui file paths
        self.__app = QApplication(sys.argv)
        authenticationUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/authentication.ui')).replace('\\', '/')
        mainUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/main.ui')).replace('\\', '/')
        preferenceUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/preference.ui')).replace('\\', '/')

        # open ui files
        loader = QUiLoader()
        authenticationUiFile = QFile(authenticationUiPath)
        authenticationUiFile.open(QFile.ReadOnly)
        mainUiFile = QFile(mainUiPath)
        mainUiFile.open(QFile.ReadOnly)
        preferenceUiFile = QFile(preferenceUiPath)
        preferenceUiFile.open(QFile.ReadOnly)

        # create ui objects
        self.__authenticationUi = loader.load(authenticationUiFile)
        self.__mainUi = loader.load(mainUiFile)
        self.__preferenceUi = loader.load(preferenceUiFile)


    def __linkCommands(self):
        '''
        TBA
        '''

        # authentication ui
        self.__authenticationUi.authenticatePB.clicked.connect(partial(self.__onAuthenticatePressed, False, True))
        self.__authenticationUi.demoPB.clicked.connect(partial(self.__onAuthenticatePressed, True, True))

        # main ui
        self.__mainUi.entityCB.currentTextChanged.connect(self.__onEntityChanged)
        self.__mainUi.filtersAddPB.clicked.connect(partial(self.__onAddPressed, self.__mainUi.filtersTW))
        self.__mainUi.filtersRemovePB.clicked.connect(partial(self.__onRemovePressed, self.__mainUi.filtersTW))
        self.__mainUi.fieldsAddPB.clicked.connect(partial(self.__onAddPressed, self.__mainUi.fieldsTW))
        self.__mainUi.fieldsRemovePB.clicked.connect(partial(self.__onRemovePressed, self.__mainUi.fieldsTW))
        self.__mainUi.preferencePB.clicked.connect(self.__onPreferencePressed)
        self.__mainUi.runPB.clicked.connect(self.__onRunPressed)

        # preference ui
        self.__preferenceUi.authenticatePB.clicked.connect(partial(self.__onAuthenticatePressed, False, False))
        self.__preferenceUi.demoPB.clicked.connect(partial(self.__onAuthenticatePressed, True, False))
        self.__preferenceUi.reloadPB.clicked.connect(self.__onReloadPressed)
        self.__preferenceUi.savePB.clicked.connect(self.__onSavePressed)
        self.__preferenceUi.cancelPB.clicked.connect(self.__onCancelPressed)


    def __startup(self):
        '''
        Check Shotgun credentials and authenticate.
        Show auth interface if credentials do not exist. 
        '''
        
        if None in self.__sgCredentials.values():
            self.__authenticationUi.show()
            return

        self.__initializeApi()
        self.__loadCache()

        entities = self.__entityFieldData.keys()
        self.__clearComboBox(self.__mainUi.entityCB)
        self.__setComboBox(self.__mainUi.entityCB, entities)

        self.__mainUi.show()

    
    def __onEntityChanged(self):
        '''
        TBA
        '''

        entity = self.__getComboBox(self.__mainUi.entityCB)
        if not entity:
            return

        self.__clearTableWidget(self.__mainUi.filtersTW)
        self.__clearTableWidget(self.__mainUi.fieldsTW)

        self.__insertTableWidgetRow(self.__mainUi.filtersTW)
        self.__insertTableWidgetRow(self.__mainUi.fieldsTW)


    def __onAddPressed(self, qTableWidget):
        '''
        TBA
        '''

        self.__insertTableWidgetRow(qTableWidget)


    def __onRemovePressed(self, qTableWidget):
        '''
        TBA
        '''

        row = qTableWidget.currentRow()
        if row != -1:
            qTableWidget.removeRow(row)


    def __onPreferencePressed(self):
        '''
        TBA
        '''

        self.__setLineEdit(self.__preferenceUi.urlLE, self.__sgCredentials['url'])
        self.__setLineEdit(self.__preferenceUi.loginLE, self.__sgCredentials['login'])
        self.__setLineEdit(self.__preferenceUi.passwordLE, '*'*len(self.__sgCredentials['password']))
        self.__preferenceUi.show()


    def __onRunPressed(self):
        '''
        TBA
        '''

        print('ahoy')




    ###################
    # COMMON COMMANDS #
    ###################


    def __onAuthenticatePressed(self, demo, startup):
        '''
        TBA
        '''

        if demo:
            self.__demo = True
        else:
            self.__demo = False

        self.__setCredentials(startup)
        self.__initializeApi()
        self.__loadCache()

        if startup:
            self.__authenticationUi.close()
            self.__mainUi.show()


    #######################
    # PREFERENCE COMMANDS #
    #######################


    def __onReloadPressed(self):
        '''
        TBA
        '''

        self.__loadCache(True)

        entities = self.__entityFieldData.keys()
        self.__clearComboBox(self.__mainUi.entityCB)
        self.__setComboBox(self.__mainUi.entityCB, entities)


    def __onSavePressed(self):
        '''
        TBA
        '''

        self.__preferenceUi.close()


    def __onCancelPressed(self):
        '''
        TBA
        '''

        self.__preferenceUi.close()


    ########
    # MISC #
    ########


    def __setCredentials(self, startup):
        '''
        TBA
        '''

        if self.__demo:
            url = 'demo'
            login = 'demo'
            password = 'demo'
        else:
            if startup:
                url = self.__getLineEdit(self.__authenticationUi.urlLE)
                login = self.__getLineEdit(self.__authenticationUi.loginLE)
                password = self.__getLineEdit(self.__authenticationUi.passwordLE)
            else:
                url = self.__getLineEdit(self.__preferenceUi.urlLE)
                login = self.__getLineEdit(self.__preferenceUi.loginLE)
                password = self.__getLineEdit(self.__preferenceUi.passwordLE)

        self.__updateJson(self.__configPath, self.__sgCredentials)

        # TODO: ui, color. greyout...


    def __initializeApi(self):
        '''
        Instantiate GunpowderApi class and authenticate Shotgun.
        If self.__demo is True, it gives self.__demoPath to run demo mode.
        '''

        if self.__demo:
            self.gunpowderApi = GunpowderApi(self.__demoPath)
            print('demo')
        else:
            self.gunpowderApi = GunpowderApi()
            print('standard')

        url = self.__sgCredentials['url']
        login = self.__sgCredentials['login']
        password = self.__sgCredentials['password']
        self.gunpowderApi.authenticate(url, login, password)


    def __loadCache(self, force=False):
        '''
        Load dictionary of Shotgun entity & field from cache.json and fill UI.
        If cache.json is empty, it creates cache with GunpowderApi.
        If force is True, it overwrite existing cache with the latest data.
        '''

        self.__entityFieldData = self.__readJson(self.__cachePath)
 
        if not self.__entityFieldData or force:
            self.__entityFieldData = self.gunpowderApi.getEntityField()
            self.__writeJson(self.__cachePath, self.__entityFieldData)


    def __insertTableWidgetRow(self, qTableWidget):
        '''
        TBA
        '''

        objectName = qTableWidget.objectName()
        entity = self.__getComboBox(self.__mainUi.entityCB)
        fields = self.__entityFieldData[entity]
        row = qTableWidget.rowCount()

        qTableWidget.insertRow(row)

        if objectName == 'filtersTW':
            fieldsCB = QComboBox()
            fieldsCB.addItems(fields)

            conditionsCB = QComboBox()
            conditionsCB.addItems(self.__conditions)

            valueItem = QTableWidgetItem()

            qTableWidget.setCellWidget(row, 0, fieldsCB)
            qTableWidget.setCellWidget(row, 1, conditionsCB)
            qTableWidget.setItem(row, 2, valueItem)

        else:
            fieldsCB = QComboBox()
            fieldsCB.addItems(fields)
            qTableWidget.setCellWidget(row, 0, fieldsCB)


    def __readJson(self, jsonPath):
        '''
        TBA
        '''

        with open(jsonPath) as d:
            data = json.load(d)
        return data


    def __writeJson(self, jsonPath, keyValue):
        '''
        TBA
        '''

        with open(jsonPath, 'w') as d:
            dump = json.dumps(keyValue, indent=4, sort_keys=True, ensure_ascii=False)
            d.write(dump)


    def __updateJson(self, jsonPath, keyValue):
        '''
        TBA
        '''

        data = self.__readJson(jsonPath)
        for key in keyValue:
            value = keyValue[key]
            data[key] = value
        self.__writeJson(jsonPath, data)


    def __getLineEdit(self, qLineEdit):
        '''
        TBA
        '''

        return qLineEdit.text()


    def __setLineEdit(self, qLineEdit, value):
        '''
        TBA
        '''

        return qLineEdit.setText(value)


    def __getComboBox(self, qComboBox):
        '''
        TBA
        '''

        return qComboBox.currentText()


    def __setComboBox(self, qComboBox, values):
        '''
        TBA
        '''

        qComboBox.addItems(values)


    def __clearComboBox(self, qComboBox):
        '''
        TBA
        '''

        qComboBox.clear()


    def __clearTableWidget(self, qTableWidget):
        '''
        TBA
        '''

        rowCount = qTableWidget.rowCount()
        for row in range(rowCount):
            qTableWidget.removeRow(row)


if __name__ == '__main__':
    Gunpowder()
