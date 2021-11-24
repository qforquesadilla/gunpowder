import os
import sys
import json
from functools import partial

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide2.QtCore import QFile

from sgUtil import SgUtil

'''
Gunpowder
'''


class Gunpowder(object):

    def __init__(self):
        '''
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

        # cache
        #

        # ui & commands
        self.__buildUi()
        self.__linkCommands()

        # startup
        self.__startup()

        print('\n\n########\n# GUNPOWDER #\n########\n')
        sys.exit(self.__app.exec_())


    def __setupConfig(self):
        '''
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


    def __buildUi(self):
        '''
        '''

        # define ui file paths
        self.__app = QApplication(sys.argv)
        authUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/auth.ui')).replace('\\', '/')
        mainUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/main.ui')).replace('\\', '/')
        filterUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/filter.ui')).replace('\\', '/')
        fieldUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/field.ui')).replace('\\', '/')

        # open ui files
        loader = QUiLoader()
        authUiFile = QFile(authUiPath)
        authUiFile.open(QFile.ReadOnly)
        mainUiFile = QFile(mainUiPath)
        mainUiFile.open(QFile.ReadOnly)
        filterUiFile = QFile(filterUiPath)
        filterUiFile.open(QFile.ReadOnly)
        fieldUiFile = QFile(fieldUiPath)
        fieldUiFile.open(QFile.ReadOnly)

        # create ui objects
        self.__authUi = loader.load(authUiFile)
        self.__mainUi = loader.load(mainUiFile)
        self.__filterUi = loader.load(filterUiFile)
        self.__fieldUi = loader.load(fieldUiFile)


    def __linkCommands(self):
        '''
        '''

        # auth ui
        self.__authUi.auth_bt.clicked.connect(partial(self.__authDemoCmd, False, True))
        self.__authUi.demo_bt.clicked.connect(partial(self.__authDemoCmd, True, True))

        # main ui
        
        self.__mainUi.authPB.clicked.connect(partial(self.__authDemoCmd, False, False))
        self.__mainUi.demoPB.clicked.connect(partial(self.__authDemoCmd, True, False))
        
        return
        self.__mainUi.fltAdd_bt.clicked.connect(self.dummy)
        self.__mainUi.fltRemove_bt.clicked.connect(self.dummy)
        self.__mainUi.fldAdd_bt.clicked.connect(self.dummy)
        self.__mainUi.fldRemove_bt.clicked.connect(self.dummy)
        self.__mainUi.find_bt.clicked.connect(self.dummy)

        # filter ui
        self.__filterUi.add_bt.clicked.connect(self.dummy)

        # field ui
        self.__fieldUi.add_bt.clicked.connect(self.dummy)


    def __startup(self):
        '''
        Check Shotgun credentials and authenticate.
        Show auth interface if credentials do not exist. 
        '''
        
        if None in self.__sgCredentials.values():
            self.__authUi.show()
        else:
            self.__initializeApi()
            self.__loadCache()
            self.__mainUi.show()


    def dummy(self):
        print('ahoy')


    ###########
    # AUTH UI #
    ###########

    def __authDemoCmd(self, demo, startup):
        '''
        '''

        if demo:
            self.__demo = True
        else:
            self.__demo = False

        self.__setCredentials(startup)
        self.__initializeApi()
        self.__loadCache()

        if startup:
            self.__authUi.close()
            self.__mainUi.show()


    #############
    # FILTER UI #
    #############


    ############
    # FIELD UI #
    ############


    ########
    # MISC #
    ########

    def __setCredentials(self, startup):
        '''
        TBA.
        '''
        if self.__demo:
            url = 'demo'
            login = 'demo'
            password = 'demo'
        else:
            if startup:
                url = self.__getLineEdit(self.__authUi.url_le)
                login = self.__getLineEdit(self.__authUi.login_le)
                password = self.__getLineEdit(self.__authUi.password_le)
            else:
                url = self.__getLineEdit(self.__mainUi.urlLE)
                login = self.__getLineEdit(self.__mainUi.loginLE)
                password = self.__getLineEdit(self.__mainUi.passwordLE)

        self.__sgCredentials = {'url': url, 'login': login, 'password': password}
        self.__updateJson(self.__configPath, self.__sgCredentials)
        self.__setLineEdit(self.__mainUi.urlLE, url)
        self.__setLineEdit(self.__mainUi.loginLE, login)
        self.__setLineEdit(self.__mainUi.passwordLE, '*'*len(password))

        # ui, color. greyout...


    def __initializeApi(self):
        '''
        Instantiate SgUtil class and authenticate Shotgun.
        If self.__demo is True, it gives self.__demoPath to run demo mode.
        '''

        if self.__demo:
            self.sgutil = SgUtil(self.__demoPath)
            print('demo')
        else:
            self.sgutil = SgUtil()
            print('standard')

        url = self.__sgCredentials['url']
        login = self.__sgCredentials['login']
        password = self.__sgCredentials['password']
        self.sgutil.authenticate(url, login, password)


    def __loadCache(self, force=False):
        '''
        Load dictionary of Shotgun entity & field from cache.json.
        If cache.json is empty, it creates cache with SgUtil.
        If force is True, it overwrite existing cache with the latest data.
        '''

        entityFieldDict = self.__readJson(self.__cachePath)
 
        if not entityFieldDict or force:
            entityFieldDict = self.sgutil.getEntityField()
            self.__writeJson(self.__cachePath, entityFieldDict)



    def __readJson(self, jsonPath):
        with open(jsonPath) as d:
            data = json.load(d)
        return data

    def __writeJson(self, jsonPath, keyValue):
        with open(jsonPath, 'w') as d:
            dump = json.dumps(keyValue, indent=4, sort_keys=True, ensure_ascii=False)
            d.write(dump)

    def __updateJson(self, jsonPath, keyValue):
        data = self.__readJson(jsonPath)
        for key in keyValue:
            value = keyValue[key]
            data[key] = value
        self.__writeJson(jsonPath, data)

    def __getLineEdit(self, qLineEdit):
        return qLineEdit.text()

    def __setLineEdit(self, qLineEdit, value):
        return qLineEdit.setText(value)




if __name__ == "__main__":
    Gunpowder()