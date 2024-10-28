from PyQt5 import QtNetwork
from PyQt5 import QtCore
import sys, json

class RequetePOST:

    def __init__(self):

        self.lancerRequetePOST()


    def lancerRequetePOST(self):

        data = QtCore.QByteArray()
        data.append('prenom1=Hector&')
        data.append('prenom2=Arthur')

        url = 'https://httpbin.org/post'
        requete = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        requete.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader,
            'application/x-www-form-urlencoded')

        self.manager = QtNetwork.QNetworkAccessManager()
        self.manager.finished.connect(self.gererReponse)
        self.manager.post(requete, data)


    def gererReponse(self, ret):

        er = ret.error()

        if er == QtNetwork.QNetworkReply.NoError:

            res = ret.readAll()

            json_res = json.loads(str(res, 'utf-8'))
            data = json_res['form']

            print(f"Prénom 1 : {data['prenom1']}")
            print(f"Prénom 2  : {data['prenom2']}")

        else:
            print('Détection de cette erreur : ', er)
            print(ret.errorString())

        QtCore.QCoreApplication.quit()


if __name__ == '__main__':
    app = QtCore.QCoreApplication([])
    ex = RequetePOST()
    sys.exit(app.exec_())