'''
PathData = {
'emmcPath' : '',
'outDirPath' : "",
'targetPath' :""
}
'''


class pathData(object):
    def __init__(self, emmcPath, outDirPath, targetPath):
        self._emmcPath = emmcPath
        self._outDirPath = outDirPath
        self._targetPath = targetPath

    @property
    def emmcPath(self):
        return self._emmcPath

    @emmcPath.setter
    def emmcPath(self, emmcPath):
        self._emmcPath = emmcPath

    @property
    def outDirPath(self):
        return self._outDirPath

    @outDirPath.setter
    def outDirPath(self, outDirPath):
        self._outDirPath = outDirPath

    @property
    def targetPath(self):
        return self._targetPath

    def pathDataToDic(self):
        return {
            'emmcPath': self.emmcPath,
            'outDirPath': self.outDirPath,
            'targetPath': self.targetPath
        }



