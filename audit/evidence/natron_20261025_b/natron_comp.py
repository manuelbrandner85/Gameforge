
a = app1
p = a.createNode("fr.inria.openfx.ReadOIIO"); p.getParam("filename").setValue(r"C:\Users\manue\Desktop\GAMEFORGE_GODMODE_v2_0\audit\evidence\natron_20261025_b\plate_###.png")
o = a.createNode("fr.inria.openfx.ReadOIIO"); o.getParam("filename").setValue(r"C:\Users\manue\Desktop\GAMEFORGE_GODMODE_v2_0\audit\evidence\natron_20261025_b\over_###.png")
fp = o.getParam("filePremult")   # PNG alpha is straight (unassociated): read as unpremultiplied, else edges go too bright
fp.setValue(2) if fp is not None else None
m = a.createNode("net.sf.openfx.MergePlugin")
m.connectInput(0, p)      # B
m.connectInput(1, o)      # A (over)
w = a.createNode("fr.inria.openfx.WriteOIIO"); w.getParam("filename").setValue(r"C:\Users\manue\Desktop\GAMEFORGE_GODMODE_v2_0\audit\evidence\natron_20261025_b\comp_###.png")
w.connectInput(0, m)
a.render(w, 1, 5)
