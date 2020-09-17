import os
import sys
import json
from functools import partial

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide2.QtCore import QFile

"""
XX
"""


class run():

    def __init__(self):

        # vers
        self.config_path = None
        self.config_data = None
        self.sg_url = None
        self.sg_login = None
        self.sg_password = None
        
        self.entity_all = []
        self.fields_all = []

        # ui
        self.ui()
        self.authLinkCommands()
        self.mainLinkCommands()
        self.filterLinkCommands()

        # config
        if not self.setupConfig():
            return

        # auth ui or main ui
        if None in [self.sg_url, self.sg_login, self.sg_password]:
            print("SHOTGUN authentication not found")
            self.auth_ui.show()
            #while self.auth == False:
            #    if self.auth == True:
            #        break

        else:
            print("SHOTGUN authentication found")
            print("URL: {}".format(self.sg_url))
            print("LOGIN: {}".format(self.sg_login))
            print("PASSWORD: {}".format(self.sg_password))
            self.startup()

        print("\n\n#############\n# GUNPOWDER #\n#############\n")

        sys.exit(self.app.exec_())


    def setupConfig(self):
        path_dir = os.path.dirname(__file__)
        self.config_path = os.path.abspath(os.path.join(path_dir, r"data/config.json"))

        try:
            with open(self.config_path) as c:
                self.config_data = json.load(c)
        except Exception as err:
            print("Failed to load config: {}".format(self.config_path))
            print(err)
            return
        
        if not self.config_data:
            print("Config data is empty: {}".format(self.config_path))
            return

        self.sg_url = self.config_data.get("sg_url", None)
        self.sg_login = self.config_data.get("sg_login", None)
        self.sg_password = self.config_data.get("sg_password", None)
        self.entity_all = self.config_data.get("entity", None)

        return True


    def ui(self):
        self.app = QApplication(sys.argv)
        auth_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'interface/auth.ui')).replace('\\', '/')
        main_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'interface/main.ui')).replace('\\', '/')
        flt_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'interface/filter.ui')).replace('\\', '/')
        fld_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'interface/field.ui')).replace('\\', '/')

        loader = QUiLoader()

        auth_ui = QFile(auth_ui_path)
        auth_ui.open(QFile.ReadOnly)

        main_ui = QFile(main_ui_path)
        main_ui.open(QFile.ReadOnly)

        flt_ui = QFile(flt_ui_path)
        flt_ui.open(QFile.ReadOnly)

        fld_ui = QFile(fld_ui_path)
        fld_ui.open(QFile.ReadOnly)

        self.auth_ui = loader.load(auth_ui)
        self.main_ui = loader.load(main_ui)
        self.flt_ui = loader.load(flt_ui)
        self.fld_ui = loader.load(fld_ui)


    def authLinkCommands(self):
        self.auth_ui.auth_bt.clicked.connect(self.authCmd)
        self.auth_ui.cancel_bt.clicked.connect(self.cancelAuthCmd)


    def mainLinkCommands(self):
        self.main_ui.fltAdd_bt.clicked.connect(partial(self.addFilterCmd, False))
        self.main_ui.fltRemove_bt.clicked.connect(partial(self.removeItemCmd, "flt"))
        self.main_ui.fldAdd_bt.clicked.connect(partial(self.addFieldCmd, False))
        self.main_ui.fldRemove_bt.clicked.connect(partial(self.removeItemCmd, "fld"))
        self.main_ui.find_bt.clicked.connect(self.dummy)

        self.main_ui.flt_lw.itemDoubleClicked.connect(partial(self.addFilterCmd, True))
        self.main_ui.fld_lw.itemDoubleClicked.connect(partial(self.addFieldCmd, True))


    def filterLinkCommands(self):
        self.flt_ui.add_bt.clicked.connect(self.dummy)


    def fieldLinkCommands(self):
        self.fld_ui.add_bt.clicked.connect(self.dummy)


    def startup(self):
        
        if self.entity_all in [None, []]:
            print("no entity on config")
            return
        
        self.main_ui.show()
        self.main_ui.ent_cbx.clear()
        self.main_ui.ent_cbx.addItems(self.entity_all)

        self.field_all = ["id", "code", "sg_status_list", "sg_frame_start", "sg_frame_end"]# GET VALID FIELDS FROM SHOTGUN HERE


    #################
    # AUTH COMMANDS #
    #################


    def authCmd(self):

        print("ahoy!")
        print("ahoy!")
        print("ahoy!")
        print("ahoy!")
        self.auth_ui.close()
        self.startup()


    def cancelAuthCmd(self):

        self.auth_ui.close()
        print("Canceled")


    ####################
    # MAIN UI COMMANDS #
    ####################


    def dummy(self):
        
        print("ahoy")


    def addFilterCmd(self, edit=False, *args):
        
        if edit:
            flt_val = self.main_ui.flt_lw.currentItem().text()
            fld = flt_val.split(";")[0]
            cnd = flt_val.split(";")[1]
            val = flt_val.split(";")[2]
            
            print(fld)
            print(cnd)
            print(val)

            self.flt_ui.show()

            self.flt_ui.fld_cbx.clear()
            self.flt_ui.fld_cbx.addItems(self.field_all)

            flt_idx = self.flt_ui.fld_cbx.findText(fld)
            self.flt_ui.fld_cbx.setCurrentIndex(flt_idx)

            cnd_idx = self.flt_ui.cnd_cbx.findText(cnd)
            self.flt_ui.cnd_cbx.setCurrentIndex(cnd_idx)
            
            self.flt_ui.val_le.setText(val)

        else:
            self.flt_ui.show()

        self.flt_ui.fld_cbx.setCurrentIndex(0)


    def addFieldCmd(self, edit=False, *args):


        self.fld_ui.show()

        self.fld_ui.fld_cbx.clear()
        
        item_all =  [str(self.main_ui.fld_lw.item(i).text()) for i in range(self.main_ui.fld_lw.count())]

        item_tgt = []
        for fld in self.field_all:
            if not fld in item_all:
                item_tgt.append(fld)

        self.fld_ui.fld_cbx.addItems(item_tgt)

        if edit:
            fld_val = self.main_ui.fld_lw.currentItem().text()
            fld_idx = self.fld_ui.fld_cbx.findText(fld_val)
            self.fld_ui.fld_cbx.setCurrentIndex(fld_idx)

        self.fld_ui.fld_cbx.setCurrentIndex(0)


    def removeItemCmd(self, mode, *args):

        if mode == "flt":
            ui = self.main_ui.flt_lw
        else:
            ui = self.main_ui.fld_lw

        item = ui.currentItem()
        idx = ui.row(item)
        ui.takeItem(idx)








if __name__ == "__main__":
    run()





