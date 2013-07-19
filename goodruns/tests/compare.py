import ROOT
ROOT.gSystem.Load('GoodRunsLists/StandAlone/libGoodRunsLists.so')
from ROOT import Root

reader = Root.TGoodRunsListReader()
reader.AddXMLFile('grlA.xml')
reader.AddXMLFile('grlB.xml')
reader.Interpret()
grl_overlap = reader.GetMergedGoodRunsList(Root.AND)
writer = Root.TGoodRunsListWriter()
writer.SetGoodRunsList(grl_overlap)
writer.SetFilename('grl_overlap_goodrunslists.xml')
writer.WriteXMLFile()


from goodruns import GRL

grl_a = GRL('grlA.xml')
grl_b = GRL('grlB.xml')
grl_overlap = grl_a & grl_b
grl_overlap.save('grl_overlap_goodruns.xml')
