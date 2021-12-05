import gui_template.template as tmpl
import nav_alg as na
import wx

class MainWindow(tmpl.MainFrame): 


    def __init__(self,parent): 
        tmpl.MainFrame.__init__(self,parent)  
        self.nav_alg = na.nav_alg()

    def run_analysis(self, event):
        selection = self.m_analysis_type.GetSelection()

        self.nav_alg = na.nav_alg(
            frequency=int(self.m_enter_freq.GetValue()),
            points_count=int(self.m_enter_points_num.GetValue())
        )

        self.nav_alg.set_coordinates(
            lat = float(self.m_enter_lat.GetValue()),
            lon = float(self.m_enter_lon.GetValue())
        )
        
        if selection == 0: # offset analysis
            g_offset = float(self.m_enter_gyr_offset.GetValue())
            a_offset = float(self.m_enter_acc_offset.GetValue())
            self.nav_alg.set_a_body(a_offset, a_offset, a_offset)
            self.nav_alg.set_w_body(g_offset, g_offset, g_offset)
        elif selection == 1: # drift analisis
            g_drift = float(self.m_enter_gyr_drift.GetValue())
            a_drift = float(self.m_enter_acc_drift.GetValue())
            self.nav_alg.set_a_body(a_drift, a_drift, a_drift)
            self.nav_alg.set_w_body(g_drift, g_drift, g_drift)
        wx.MessageBox("Running")
        self.nav_alg.analysis()
        self.nav_alg.plots()
        wx.MessageBox("All done")
        
app = wx.App(False) 
frame = MainWindow(None) 
frame.Show(True) 
#start the applications 
app.MainLoop() 