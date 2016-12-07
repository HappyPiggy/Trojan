from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys  
import client  
      
class TestDialog(QDialog,client.Ui_Dialog):
        def __init__(self,parent=None):  
            super(TestDialog,self).__init__(parent)  
            self.setupUi(self)
            self.client=''
      
app=QApplication(sys.argv)  
dialog=TestDialog()  
dialog.show()  
app.exec_()  
