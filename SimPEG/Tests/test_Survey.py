import unittest
from SimPEG import *

class DataAndFieldsTest(unittest.TestCase):

    def setUp(self):
        mesh = Mesh.TensorMesh([np.ones(n)*5 for n in [10,11,12]],[0,0,-30])
        x = np.linspace(5,10,3)
        XYZ = Utils.ndgrid(x,x,np.r_[0.])
        txLoc = np.r_[0,0,0.]
        rxList0 = Survey.BaseRx(XYZ, 'exi')
        Tx0 = Survey.BaseTx(txLoc, 'VMD', [rxList0])
        rxList1 = Survey.BaseRx(XYZ, 'bxi')
        Tx1 = Survey.BaseTx(txLoc, 'VMD', [rxList1])
        rxList2 = Survey.BaseRx(XYZ, 'bxi')
        Tx2 = Survey.BaseTx(txLoc, 'VMD', [rxList2])
        rxList3 = Survey.BaseRx(XYZ, 'bxi')
        Tx3 = Survey.BaseTx(txLoc, 'VMD', [rxList3])
        Tx4 = Survey.BaseTx(txLoc, 'VMD', [rxList0, rxList1, rxList2, rxList3])
        txList = [Tx0,Tx1,Tx2,Tx3,Tx4]
        survey = Survey.BaseSurvey(txList=txList)
        self.D = Survey.Data(survey)
        self.F = Survey.Fields(mesh, survey, knownFields={'phi':'CC','e':'E','b':'F'})
        self.Tx0 = Tx0
        self.Tx1 = Tx1
        self.mesh = mesh
        self.XYZ = XYZ

    def test_data(self):
        V = []
        for tx in self.D.survey.txList:
            for rx in tx.rxList:
                v = np.random.rand(rx.nD)
                V += [v]
                self.D[tx, rx] = v
                self.assertTrue(np.all(v == self.D[tx, rx]))
        V = np.concatenate(V)
        self.assertTrue(np.all(V == Utils.mkvc(self.D)))

        D2 = Survey.Data(self.D.survey, V)
        self.assertTrue(np.all(Utils.mkvc(D2) == Utils.mkvc(self.D)))


    def test_uniqueTxs(self):
        txs = self.D.survey.txList
        txs += [txs[0]]
        self.assertRaises(AssertionError, Survey.BaseSurvey, txList=txs)

    def test_SetGet(self):
        F = self.F
        nTx = F.survey.nTx
        e = np.random.rand(F.mesh.nE, nTx)
        F[:, 'e'] = e
        b = np.random.rand(F.mesh.nF, nTx)
        F[:, 'b'] = b

        self.assertTrue(np.all(F[:, 'e'] == e))
        self.assertTrue(np.all(F[:, 'b'] == b))
        F[:] = {'b':b,'e':e}
        self.assertTrue(np.all(F[:, 'e'] == e))
        self.assertTrue(np.all(F[:, 'b'] == b))

        b = np.random.rand(F.mesh.nF,1)
        F[self.Tx0, 'b'] = b
        self.assertTrue(np.all(F[self.Tx0, 'b'] == Utils.mkvc(b)))

        b = np.random.rand(F.mesh.nF)
        F[self.Tx0, 'b'] = b
        self.assertTrue(np.all(F[self.Tx0, 'b'] == b))

        phi = np.random.rand(F.mesh.nC,2)
        F[[self.Tx0,self.Tx1], 'phi'] = phi
        self.assertTrue(np.all(F[[self.Tx0,self.Tx1], 'phi'] == phi))

        fdict = F[:]
        self.assertTrue(type(fdict) is dict)
        self.assertTrue(sorted([k for k in fdict]) == ['b','e','phi'])

        b = np.random.rand(F.mesh.nF, 2)
        F[[self.Tx0, self.Tx1],'b'] = b
        self.assertTrue(F[self.Tx0]['b'].shape == (F.mesh.nF,))
        self.assertTrue(F[self.Tx0,'b'].shape == (F.mesh.nF,))
        self.assertTrue(np.all(F[self.Tx0,'b'] == b[:,0]))
        self.assertTrue(np.all(F[self.Tx1,'b'] == b[:,1]))

    def test_assertions(self):
        freq = [self.Tx0, self.Tx1]
        bWrongSize = np.random.rand(self.F.mesh.nE, self.F.survey.nTx)
        def fun(): self.F[freq, 'b'] = bWrongSize
        self.assertRaises(ValueError, fun)
        def fun(): self.F[-999.]
        self.assertRaises(KeyError, fun)
        def fun(): self.F['notRight']
        self.assertRaises(KeyError, fun)
        def fun(): self.F[freq,'notThere']
        self.assertRaises(KeyError, fun)

if __name__ == '__main__':
    unittest.main()