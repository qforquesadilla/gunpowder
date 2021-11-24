import json
import shotgun_api3

'''
SgUtil
'''


class SgUtil(object):

    def __init__(self, demoPath=''):
        '''
        Run as demo mode if demoPath is given.
        '''

        self.__sg = None
        self.__demoPath = demoPath

        if self.__demoPath == '':
            self.__demo = False
            self.__demoData = None
        else:
            self.__demo = True
            if not self.setupDemo():
                return


    def setupDemo(self):
        '''
        '''

        try:
            with open(self.__demoPath) as d:
                self.__demoData = json.load(d)
        except Exception as err:
            print('Failed to load demo: {}'.format(self.__demoPath))
            print(str(err))
            return False


    ##################
    # AUTHENTICATION #
    ##################

    def authenticate(self, url, login, password):
        '''
        '''

        if self.__demo:
            print('demodemo')
            self.__sg = 'demo'
        else:
            print('modemode')
            self.__sg = shotgun_api3.Shotgun(url, login, password)
            # add human auth too


    #################
    # BASE COMMANDS #
    #################

    def __find(self, entity, filters, fields):
        '''
        Return a list containing dictionaries from Shotgun.
        e.g. 
        '''

        return self.__sg.find(entity, filters, fields)


    def __getEntity(self):
        '''
        Return a dictionary of active entities from Shotgun.
        e.g. 
        '''

        if self.__demo:
            return self.__demoData.keys()
        else:
            return self.__sg.schema_entity_read()


    def __getField(self, entity):
        '''
        Return a dictionary of active fields from Shotgun.
        e.g. 
        '''

        if self.__demo:
            return self.__demoData[entity]
        else:
            return self.__sg.schema_field_read(entity)


    ###################
    # CUSTOM COMMANDS #
    ###################

    def getEntityField(self):
        '''
        Get all active entities and their fields and return its list.
        e.g. 
        '''

        out = {}
        entityAll = self.__getEntity()

        for entity in entityAll:
            fieldAll = self.__getField(entity)
            fieldList = []

            for field in fieldAll:
                fieldList.append(field)

            out[entity] = fieldList

        return out
