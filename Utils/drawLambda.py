#! /usr/bin/env pythonAA

import os, multiprocessing
import copy
import math
from array import array
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory, gDirectory
from ROOT import TFile, TChain, TTree, TCut, TH1, TH1F, TH1D, TH2F, THStack, TGraph, TGraphAsymmErrors, TObject
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine, TBox

#from PhysicsTools.NanoAODTools.plotter.lambPlot import cfg
import PhysicsTools.NanoAODTools.plotter.Utils.color as col
#from PhysicsTools.NanoAODTools.plotter.Utils.variables import variable
from PhysicsTools.NanoAODTools.postprocessing.data.vars import variable
from PhysicsTools.NanoAODTools.plotter.Utils.sampleslist import *
from collections import OrderedDict
import pandas as pds
import numpy as np

gROOT.SetBatch(True)
#gROOT.Macro('functions.C')
gStyle.SetOptStat(0)

def ProjectDraw(var, cut, Lumi, samplelist, pd, ntupledir):

    histList={}
    histlet={}

    if 'mumu' in cut:
        print col.OKGREEN+var+" : "+col.ENDC+ \
            "Inv( "+col.OKGREEN+"Muon^(+/-)"+col.ENDC+" , "+col.FAIL+"Muon^(-/+)"+col.ENDC+" )" if 'OS' in cut else \
            "Inv( "+col.OKGREEN+"Muon^(+/-)"+col.ENDC+" , "+col.OKGREEN+"Muon^(+/-)"+col.ENDC+" )"
    elif 'ee' in cut:
        print col.OKGREEN+var+" : "+col.ENDC+ \
            "Inv( "+col.OKGREEN+"Electron^(+/-)"+col.ENDC+" , "+col.FAIL+"Electron^(-/+)"+col.ENDC+" )" if 'OS' in cut else \
            "Inv( "+col.OKGREEN+"Electron^(+/-)"+col.ENDC+" , "+col.OKGREEN+"Electron^(+/-)"+col.ENDC+" )"
    elif 'emu' in cut:
        print col.OKGREEN+var+" : "+col.ENDC+ \
	    "Inv( "+col.OKGREEN+"Electron^(+/-)"+col.ENDC+" , "+col.FAIL+"Muon^(-/+)"+col.ENDC+" )" if 'OS' in cut else \
            "Inv( "+col.OKGREEN+"Electron^(+/-)"+col.ENDC+" , "+col.OKGREEN+"Muon^(+/-)"+col.ENDC+" )"

    if 'C_' in var:
        ##Leptonic final state
        if var=='C_deltaRll':
            print col.WARNING+"Compute composite variable C_deltaRll"+col.ENDC
            VAR="deltaR(Lepton_eta[0],Lepton_phi[0],Lepton_eta[1],Lepton_phi[1])"
            print col.WARNING+VAR+col.ENDC
        elif var=='C_deltaPhill':
            print col.WARNING+"Compute composite variable C_deltaPhill"+col.ENDC
            VAR="deltaPhi(Lepton_phi[0],Lepton_phi[1])"
        elif var=='C_deltaEtall':
            print col.WARNING+"Compute composite variable C_deltaEtall"+col.ENDC
            VAR="deltaEta(Lepton_eta[0],Lepton_eta[1])"
        ##Hadronic final state
        elif var=='C_deltaRjj':
            print col.WARNING+"Compute composite variable C_deltaRjj"+col.ENDC
            VAR="deltaR(CleanJet_eta[0],CleanJet_phi[0],CleanJet_eta[1],CleanJet_phi[1])"
            print col.WARNING+VAR+col.ENDC
        elif var=='C_deltaPhijj':
            print col.WARNING+"Compute composite variable C_deltaPhijj"+col.ENDC
            VAR="deltaPhi(CleanJet_phi[0],CleanJet_phi[1])"
        elif var=='C_deltaEtajj':
            print col.WARNING+"Compute composite variable C_deltaEtajj"+col.ENDC
            VAR="deltaEta(CleanJet_eta[0],CleanJet_eta[1])"
        ##Invariant mass of V
        elif var=='C_Vllmass':
            print col.WARNING+"Compute composite variable C_Vllmass"+col.ENDC
            VAR="invariantMass(Lepton_pt[0],Lepton_eta[0],Lepton_phi[0],Lepton_mass[0],Lepton_pt[1],Lepton_eta[1],Lepton_phi[1],Lepton_mass[1])"
            print col.WARNING+VAR+col.ENDC
        elif var=='C_Vjjmass':
            print col.WARNING+"Compute composite variable C_Vjjmass"+col.ENDC
            VAR="invariantMass(CleanJet_pt[0],CleanJet_eta[0],CleanJet_phi[0],CleanJet_mass[0],CleanJet_pt[1],CleanJet_eta[1],CleanJet_phi[1],CleanJet_mass[1])"
            print col.WARNING+VAR+col.ENDC
        ##Invariant pt of V
        elif var=='C_Vllpt':
            print col.WARNING+"Compute composite variable C_Vllpt"+col.ENDC
            VAR="invariantMassPt(Lepton_pt[0],Lepton_eta[0],Lepton_phi[0],Lepton_mass[0],Lepton_pt[1],Lepton_eta[1],Lepton_phi[1],Lepton_mass[1])"
            print col.WARNING+VAR+col.ENDC
        elif var=='C_Vjjpt':
            print col.WARNING+"Compute composite variable C_Vjjpt"+col.ENDC
            VAR="invariantMassPt(CleanJet_pt[0],CleanJet_eta[0],CleanJet_phi[0],CleanJet_mass[0],CleanJet_pt[1],CleanJet_eta[1],CleanJet_phi[1],CleanJet_mass[1])"
            print col.WARNING+VAR+col.ENDC
    else:
        print col.OKGREEN+var+col.ENDC
        VAR=var

    CUT=selection[cut]

    for TAG in samplelist:

        # Is this necessary??
        ENUMLIST=[]
        if 'data' in TAG:
            for datalet in (samples['%s' %TAG]['files']):
                if datalet in pd:
                    ENUMLIST.append(datalet)
        elif not 'data' in TAG:
            ENUMLIST=samples['%s' %TAG]['files']
        ##########################################
        ##########################################
        for num, bkgs in enumerate(ENUMLIST):
            f = TFile.Open(ntupledir+bkgs+".root","READ")
            tree = f.Get("Events")
            gROOT.cd()
            #Define histograms
            nevents = float(sample[bkgs]['nevents'])
            xs = float(sample[bkgs]['xsec'])*float(sample[bkgs]['kfactor'])
            LumiMC = nevents/xs
            Weight = float(Lumi) / float(LumiMC)

            if variable[var]['nbins']>0: histlet[bkgs] = TH1F(bkgs, ";"+variable[var]['title']+";"+variable[var]['titleY'], variable[var]['nbins'], variable[var]['min'], variable[var]['max'])
            else: histlet[bkgs]=TH1F(bkgs,";"+variable[var]['title']+";"+variable[var]['titleY'], len(variable[var]['bins'])-1, array('f', variable[var]['bins']))
            histlet[bkgs].Sumw2()

            if 'data' in TAG:
                if cfg.dataset()=="Run2_16_nanov0":
                    print col.OKBLUE+"DATA, NO HLT : ", bkgs+col.ENDC
                    subcut= CUT.replace(MuTrig if 'mu' in cut else EleTrig,"(1==1)")
                    print subcut
                else:
                    print col.MAGENTA+"MC, With HLT : ", bkgs+col.ENDC
                    subcut=CUT
                tree.Draw("%s >> %s" %(VAR,bkgs),"%s" %subcut)
            elif not 'data' in TAG:
                ExtW=weight[cut]
                print col.MAGENTA+"MC, With HLT : ", bkgs+col.ENDC

                tree.Draw("%s >> %s" %(VAR,bkgs),"%s*%s*(%s)" %(Weight,ExtW,CUT))
            if num==0:
                histList[TAG]=histlet[bkgs]
            else:
                hnew = histlet[bkgs].Clone(bkgs)
                histList[TAG].Add(hnew)

            '''
            if 'data' in TAG:
            ##on SSmumu:
            if cut == 'SSmumu' and var == "LepIso03[1]" :
                for i in range(0,(histlet[TAG]).GetNbinsX()):
                    if i<=3:
                        histlet[TAG].SetBinContent(i,0)
            '''

        histList[TAG].SetFillColor(samples[TAG]['fillcolor'])
        histList[TAG].SetFillStyle(samples[TAG]['fillstyle'])
        histList[TAG].SetLineColor(samples[TAG]['linecolor'])
        histList[TAG].SetLineStyle(samples[TAG]['linestyle'])
    return histList
pass

def draw(hist, data, back, sign, snorm=1, ratio=0, poisson=True, log=False):
    # If not present, create BkgSum
    if not 'BkgSum' in hist.keys():
        hist['BkgSum'] = hist['data_obs'].Clone("BkgSum") if 'data_obs' in hist else hist[back[0]].Clone("BkgSum")
        hist['BkgSum'].Reset("MICES")
        for i, s in enumerate(back): hist['BkgSum'].Add(hist[s])
    hist['BkgSum'].SetMarkerStyle(0)

    # Some style
    for i, s in enumerate(data):
        hist[s].SetMarkerStyle(20)
        hist[s].SetMarkerSize(1.25)
    for i, s in enumerate(sign):
        hist[s].SetLineWidth(3)

    for i, s in enumerate(data+back+sign+['BkgSum']):
        addOverflow(hist[s], False) # Add overflow

    # Set Poisson error bars
    #if len(data) > 0: hist['data_obs'].SetBinErrorOption(1) # doesn't work

    # Poisson error bars for data
    if poisson:
        alpha = 1 - 0.6827
        hist['data_obs'].SetBinErrorOption(TH1.kPoisson)
        data_graph = TGraphAsymmErrors(hist['data_obs'].GetNbinsX())
        data_graph.SetMarkerStyle(hist['data_obs'].GetMarkerStyle())
        data_graph.SetMarkerSize(hist['data_obs'].GetMarkerSize())
        res_graph = data_graph.Clone()
        for i in range(hist['data_obs'].GetNbinsX()):
            N = hist['data_obs'].GetBinContent(i+1)
            B = hist['BkgSum'].GetBinContent(i+1)
            L =  0 if N==0 else ROOT.Math.gamma_quantile(alpha/2,N,1.)
            U =  ROOT.Math.gamma_quantile_c(alpha/2,N+1,1)
            data_graph.SetPoint(i, hist['data_obs'].GetXaxis().GetBinCenter(i+1), N if not N==0 else -1.e99)
            data_graph.SetPointError(i, hist['data_obs'].GetXaxis().GetBinWidth(i+1)/2., hist['data_obs'].GetXaxis().GetBinWidth(i+1)/2., N-L, U-N)
            res_graph.SetPoint(i, hist['data_obs'].GetXaxis().GetBinCenter(i+1), N/B if not B==0 and not N==0 else -1.e99)
            res_graph.SetPointError(i, hist['data_obs'].GetXaxis().GetBinWidth(i+1)/2., hist['data_obs'].GetXaxis().GetBinWidth(i+1)/2., (N-L)/B if not B==0 else -1.e99, (U-N)/B if not B==0 else -1.e99)

    # Create stack
    #bkg = THStack("Bkg", ";"+hist['BkgSum'].GetXaxis().GetTitle()+";Events")
    bkg = THStack("Bkg", ";"+hist['BkgSum'].GetXaxis().GetTitle()+";"+hist['BkgSum'].GetYaxis().GetTitle())
    for i, s in enumerate(back): bkg.Add(hist[s])

    # Legend
    n = len([x for x in data+back+['BkgSum']+sign if samples[x]['plot']])
    for i, s in enumerate(sign):
        if 'sublabel' in samples[s]: n+=1
        if 'subsublabel' in samples[s]: n+=1
    leg = TLegend(0.7, 0.9-0.05*n, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    if len(data) > 0:
        leg.AddEntry(hist[data[0]], samples[data[0]]['label'], "pl")
    for i, s in reversed(list(enumerate(['BkgSum']+back))):
        leg.AddEntry(hist[s], samples[s]['label'], "f")
    for i, s in enumerate(sign):
        if samples[s]['plot']:
            #leg.AddEntry(hist[s], samples[s]['label'].replace("m_{#Chi}=1 GeV", ""), "fl")
            leg.AddEntry(hist[s], samples[s]['label'], "fl")
            #leg.AddEntry(hist[s], "Scalar Mediator", "")

            #print samples[s]
            if 'sublabel' in samples[s]:
                leg.AddEntry(hist[s], samples[s]['sublabel'].replace("m_{#Chi}=1 GeV", ""), "")
            if 'subsublabel' in samples[s]:
                leg.AddEntry(hist[s], samples[s]['subsublabel'].replace("m_{#Chi}=1 GeV", ""), "")

     # --- Display ---
    c1 = TCanvas("c1", hist.values()[-1].GetXaxis().GetTitle(), 800, 800 if ratio else 600)

    if ratio:
        c1.Divide(1, 2)
        setTopPad(c1.GetPad(1), ratio)
        setBotPad(c1.GetPad(2), ratio)
    c1.cd(1)
    c1.GetPad(bool(ratio)).SetTopMargin(0.06)
    c1.GetPad(bool(ratio)).SetRightMargin(0.05)
    c1.GetPad(bool(ratio)).SetTicks(1, 1)
    if log:
        c1.GetPad(bool(ratio)).SetLogy()

    # Draw
    bkg.Draw("HIST") # stack
    hist['BkgSum'].Draw("SAME, E2") # sum of bkg
    if poisson: data_graph.Draw("SAME, PE")
    elif len(data) > 0: hist['data_obs'].Draw("SAME, PE")
    for i, s in enumerate(sign):
        if samples[s]['plot']:
            hist[s].DrawNormalized("SAME, HIST", hist[s].Integral()*snorm) # signals

    bkg.GetYaxis().SetTitleOffset(bkg.GetYaxis().GetTitleOffset()*1) #1.075

    if 'data_obs' in hist:
        bkg.SetMaximum((3.0 if log else 1.5)*max(bkg.GetMaximum(), hist['data_obs'].GetBinContent(hist['data_obs'].GetMaximumBin())+hist['data_obs'].GetBinError(hist['data_obs'].GetMaximumBin())))
        bkg.SetMinimum(max(min(hist['BkgSum'].GetBinContent(hist['BkgSum'].GetMinimumBin()), hist['data_obs'].GetMinimum()), 5.e-1)  if log else 0.)
    else:
        bkg.SetMaximum(bkg.GetMaximum()*(3.0 if log else 1.5)) #2.5 ; 1.2
        bkg.SetMinimum(5.e-1 if log else 0.)
    if not log:
        bkg.GetYaxis().SetNoExponent(1)
        #bkg.GetYaxis().SetNoExponent(bkg.GetMaximum() < 1.e4)
    #    bkg.GetYaxis().SetMoreLogLabels(True)

    #set range on stack
    bkg.SetMinimum(1.0)

    leg.Draw()

    setHistStyle(bkg, 1.2 if ratio else 1.1)
    setHistStyle(hist['BkgSum'], 1.2 if ratio else 1.1)

    if ratio:
        c1.cd(2)
        err = hist['BkgSum'].Clone("BkgErr;")
        err.SetTitle("")
        err.GetYaxis().SetTitle("Data / Bkg")
        for i in range(1, err.GetNbinsX()+1):
            err.SetBinContent(i, 1)
            if hist['BkgSum'].GetBinContent(i) > 0:
                err.SetBinError(i, hist['BkgSum'].GetBinError(i)/hist['BkgSum'].GetBinContent(i))
        setBotStyle(err)
        errLine = err.Clone("errLine")
        errLine.SetLineWidth(1)
        errLine.SetFillStyle(0)
        errLine.SetLineColor(1)
        #err.GetXaxis().SetLabelOffset(err.GetXaxis().GetLabelOffset()*5)
        #err.GetXaxis().SetTitleOffset(err.GetXaxis().GetTitleOffset()*2)
        err.Draw("E2")
        errLine.Draw("SAME, HIST")
        if 'data_obs' in hist:
            res = hist['data_obs'].Clone("Residues")
            for i in range(0, res.GetNbinsX()+1):
                if hist['BkgSum'].GetBinContent(i) > 0:
                    res.SetBinContent(i, res.GetBinContent(i)/hist['BkgSum'].GetBinContent(i))
                    res.SetBinError(i, res.GetBinError(i)/hist['BkgSum'].GetBinContent(i))
            setBotStyle(res)
            if poisson: res_graph.Draw("SAME, PE0")
            else: res.Draw("SAME, PE0")
            if len(err.GetXaxis().GetBinLabel(1))==0: # Bin labels: not a ordinary plot
                drawRatio(hist['data_obs'], hist['BkgSum'])
                drawKolmogorov(hist['data_obs'], hist['BkgSum'])
                drawRelativeYield(hist['data_obs'], hist['BkgSum'])
        else: res = None
    c1.Update()

    # return list of objects created by the draw() function
    if not ratio:
        return [c1, bkg, leg, data_graph if poisson else None, res_graph if poisson else None]
    else:
        return [c1, bkg, leg, err, errLine, res, data_graph if poisson else None, res_graph if poisson else None]
pass

def drawRatio(data, bkg):
    errData = array('d', [1.0])
    errBkg = array('d', [1.0])
    intData = data.IntegralAndError(1, data.GetNbinsX(), errData)
    intBkg = bkg.IntegralAndError(1, bkg.GetNbinsX(), errBkg)
    ratio = intData / intBkg if intBkg!=0 else 0.
    error = math.hypot(errData[0]*ratio/intData,  errBkg[0]*ratio/intBkg) if intData>0 and intBkg>0 else 0
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.08)
    #latex.DrawLatex(0.25, 0.85, "Data/Bkg = %.3f #pm %.3f" % (ratio, error))
    latex.DrawLatex(0.15, 0.85, "Data/Bkg = %.3f #pm %.3f" % (ratio, error))
    print "  Ratio:\t%.3f +- %.3f" % (ratio, error)
    return [ratio, error]
pass

def drawKolmogorov(data, bkg):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.08)
    #latex.DrawLatex(0.55, 0.85, "#chi^{2}/ndf = %.2f,   K-S = %.3f" % (data.Chi2Test(bkg, "CHI2/NDF"), data.KolmogorovTest(bkg)))
    latex.DrawLatex(0.45, 0.85, "#chi^{2}/ndf = %.2f,   K-S = %.3f" % (data.Chi2Test(bkg, "CHI2/NDF"), data.KolmogorovTest(bkg)))
pass

def drawRelativeYield(data,bkg):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.08)
    latex.DrawLatex(0.75, 0.85, "rel. Yield= %.3f" % ((data.Integral()/bkg.Integral())*100) )
pass

def printTable(hist, sign=[]):
    samplelist = [x for x in hist.keys() if not 'data' in x and not 'BkgSum' in x and not x in sign and not x=="files"]
    print "Sample                  Events          Entries         %"
    print "-"*80
    for i, s in enumerate(['data_obs']+samplelist+['BkgSum'] if 'data_obs' in hist.keys() else samplelist+['BkgSum']):
        if i==1 or s=="data_obs" or i==len(samplelist)+1: print "-"*80
        #Events                           #Entries
        print "%-20s" % s, "\t%-10.2f" % hist[s].Integral(), "\t%-10.0f" % (hist[s].GetEntries()-2), "\t%-10.2f" % (100.*hist[s].Integral()/hist['BkgSum'].Integral()) if hist['BkgSum'].Integral() > 0 else 0, "%"
    print "-"*80
    for i, s in enumerate(sign):
        if not samples[s]['plot']: continue
        #print "%-20s" % s, "\t%-10.2f" % hist[s].Integral(), "\t%-10.0f" % (hist[s].GetEntries()-2), "\t%-10.2f" % (100.*hist[s].GetEntries()/float(hist[s].GetOption())) if float(hist[s].GetOption()) > 0 else 0, "%"
        print "%-20s" % s, "\t%-10.2f" % hist[s].Integral(), "\t%-10.0f" % (hist[s].GetEntries()-2), "\t%-10.2f" % (hist[s].GetEntries()) if float(hist[s].GetEntries()) > 0 else 0, "%"
    print "-"*80
pass


####### OTHER

def getPrimaryDataset(cut):
    pd = []
    #if 'HLT_DoubleMu' in cut or cut.split(" ")[0].count('Mu') > 1: pd += [x for x in samples['data_obs']['files'] if "DoubleMuon" in x]
    if 'HLT_DoubleEle' in cut or cut.split(" ")[0].count('Ele') > 1: pd += [x for x in samples['data_obs']['files'] if "DoubleEG" in x]
    if 'HLT_Mu' in cut or 'HLT_IsoMu' in cut: pd += [x for x in samples['data_obs']['files'] if "SingleMuon" in x]
    if 'HLT_Ele' in cut: pd += [x for x in samples['data_obs']['files'] if "SingleElectron" in x]
    if 'HLT_PFMET' in cut: pd += [x for x in samples['data_obs']['files'] if "MET" in x]
    return pd
pass

def getNm1Cut(var, cut):
#    try:
#        value = string(cut.split(var, 1)[1].split(" ")[0][1:])
#    except:
#        print "n-1 cut value not found"
    if ' '+var+'>' in cut: cut = cut.replace(var, "1e99")
    elif ' '+var+'<' in cut: cut = cut.replace(var, "-1e99")
    elif ' '+var+'==' in cut: cut = cut.replace(var+'==', "-9!=")
    else: print "  unrecognized var '", var ,"' in cut, cannot plot n-1 cut"
    return cut
pass

def addOverflow(hist, addUnder=True):
    n = hist.GetNbinsX()
    hist.SetBinContent(n, hist.GetBinContent(n) + hist.GetBinContent(n+1))
    hist.SetBinError(n, math.sqrt( hist.GetBinError(n)**2 + hist.GetBinError(n+1)**2 ) )
    hist.SetBinContent(n+1, 0.)
    hist.SetBinError(n+1, 0.)
    if addUnder:
        hist.SetBinContent(1, hist.GetBinContent(0) + hist.GetBinContent(1))
        hist.SetBinError(1, math.sqrt( hist.GetBinError(0)**2 + hist.GetBinError(1)**2 ) )
        hist.SetBinContent(0, 0.)
        hist.SetBinError(0, 0.)
pass

def setTopPad(TopPad, r=4):
    TopPad.SetPad("TopPad", "", 0., 1./r, 1.0, 1.0, 0, -1, 0)
    TopPad.SetTopMargin(0.24/r)
    TopPad.SetBottomMargin(0.04/r)
    TopPad.SetRightMargin(0.05)
    TopPad.SetTicks(1, 1)
pass

def setBotPad(BotPad, r=4):
    BotPad.SetPad("BotPad", "", 0., 0., 1.0, 1./r, 0, -1, 0)
    BotPad.SetTopMargin(r/100.)
    BotPad.SetBottomMargin(r/10.)
    BotPad.SetRightMargin(0.05)
    BotPad.SetTicks(1, 1)
pass

def setHistStyle(hist, r=1.1):
    hist.GetXaxis().SetTitleSize(hist.GetXaxis().GetTitleSize()*r*r)
    hist.GetYaxis().SetTitleSize(hist.GetYaxis().GetTitleSize()*r*r)
    hist.GetXaxis().SetLabelSize(hist.GetXaxis().GetLabelSize()*r)
    hist.GetYaxis().SetLabelSize(hist.GetYaxis().GetLabelSize()*r)
    hist.GetXaxis().SetLabelOffset(hist.GetXaxis().GetLabelOffset()*r*r*r*r)
    hist.GetXaxis().SetTitleOffset(hist.GetXaxis().GetTitleOffset()*r)
    hist.GetYaxis().SetTitleOffset(hist.GetYaxis().GetTitleOffset())
    if hist.GetXaxis().GetTitle().find("GeV") != -1: # and not hist.GetXaxis().IsVariableBinSize()
        div = (hist.GetXaxis().GetXmax() - hist.GetXaxis().GetXmin()) / hist.GetXaxis().GetNbins()
        hist.GetYaxis().SetTitle("Events / %.1f GeV" % div)
pass

def setBotStyle(h, r=4, fixRange=True):
    h.GetXaxis().SetLabelSize(h.GetXaxis().GetLabelSize()*(r-1));
    h.GetXaxis().SetLabelOffset(h.GetXaxis().GetLabelOffset()*(r-1));
    h.GetXaxis().SetTitleSize(h.GetXaxis().GetTitleSize()*(r-1));
    h.GetYaxis().SetLabelSize(h.GetYaxis().GetLabelSize()*(r-1));
    h.GetYaxis().SetNdivisions(505);
    h.GetYaxis().SetTitleSize(h.GetYaxis().GetTitleSize()*(r-1));
    h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()/(r-1));
    if fixRange:
        h.GetYaxis().SetRangeUser(0., 2.)
        for i in range(1, h.GetNbinsX()+1):
            if h.GetBinContent(i)<1.e-6:
                h.SetBinContent(i, -1.e-6)
pass

def drawCMS(lumi, text, onTop=False):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(33)
    if (type(lumi) is float or type(lumi) is int) and float(lumi) > 0: latex.DrawLatex(0.95, 0.985, "%.1f fb^{-1}  (13 TeV)" % (float(lumi)/1000.))
    elif type(lumi) is str: latex.DrawLatex(0.95, 0.985, "%s fb^{-1}  (13 TeV)" % lumi)
    if not onTop: latex.SetTextAlign(11)
    latex.SetTextFont(62)
    latex.SetTextSize(0.05 if len(text)>0 else 0.06)
    if not onTop: latex.DrawLatex(0.15, 0.87 if len(text)>0 else 0.84, "CMS")
    else: latex.DrawLatex(0.20, 0.99, "CMS")
    latex.SetTextSize(0.04)
    latex.SetTextFont(52)
    if not onTop: latex.DrawLatex(0.15, 0.83, text)
    else: latex.DrawLatex(0.40, 0.98, text)
    pass

def drawAnalysis(s, center=False):
    analyses = {"VZ" : "X #rightarrow ZV #rightarrow llqq", "VH" : "X #rightarrow Vh #rightarrow (ll,l#nu,#nu#nu)bb", "Vh" : "X #rightarrow Vh #rightarrow (ll,l#nu,#nu#nu)bb", "Zh" : "Z' #rightarrow Zh #rightarrow (ll,#nu#nu)bb", "Wh" : "W' #rightarrow Wh #rightarrow l#nu bb", "DM": "DM + heavy flavour", "AZh" : "A #rightarrow Zh #rightarrow llbb", "ZZ" : "G #rightarrow ZZ #rightarrow llqq", "WZ" : "W' #rightarrow ZW #rightarrow llqq", }
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextFont(42)
    #latex.SetTextAlign(33)
    latex.DrawLatex(0.15 if not center else 0.3, 0.95, s if not s in analyses else analyses[s])
    pass

def drawRegion(channel, left=False):
    region = { "OSmumu" : "#mu^{+}#mu^{-} / #mu^{-}#mu^{+}" , "OSee" : "e^{+}e^{-} / e^{-}e^{+}" , "OSemu" : "e^{+}#mu^{-} / e^{-}#mu^{+}" , "SSmumu" : "#mu^{+}#mu^{+} / #mu^{-}#mu^{-}" , "SSee" : "e^{+}e^{+} / e^{-}e^{-}" , "SSemu" : "e^{+}#mu^{+} / e^{-}#mu^{-}" , "WZCR" : "W(lv)Z(ll)" , "VgCR": "V#gamma" , "SSmue" : "#mu^{+}e^{+} / #mu^{-}e^{-}"  }
    text = ""
    if channel in region:
        text = region[channel]
    else:
        # leptons
        #if 'ee' in channel: text += "2e"
        #elif 'mumu' in channel: text += "2#mu"
        if 'OSmumu' in channel: text += "#mu^{#pm}#mu^{#mp}"
        elif 'OSee' in channel: text += "e^{+}e^{-}"
        elif 'OSemu' in channel: text += "e^{+}#mu^{-}"
        elif 'SSmumu' in channel: text += "#mu^{+}#mu^{+} / #mu^{-}#mu^{-}"
        elif 'SSee' in channel: text += "e^{+}e^{+} / e^{-}e^{-}"
        elif 'SSemu' in channel: text += "e^{+}#mu^{+} / e^{-}#mu^{-}"
        elif ( ('me' in channel) or ('em' in channel) ) : text += "1e 1#mu"
        elif 'e' in channel: text += "1e"
        elif 'm' in channel: text += "1#mu"
        elif 'll' in channel: text += "2l"
        elif 'l' in channel: text += "1l"
        elif 'nn' in channel: text += "0l"
        if 'Top' in channel: text += "top"
        # b-tag
        if 'bb' in channel: text += ", 2 b-tag"
        elif 'b' in channel: text += ", 1 b-tag"
        # purity
        if 'lp' in channel: text += ", low purity"
        elif 'hp' in channel: text += ", high purity"
        # region
        if 'TR' in channel: text += ", top control region"
        elif 'Inc' in channel: text += ", inclusive region"
        elif 'SB' in channel: text += ", sidebands region"
        elif 'SR' in channel: text += ", signal region"
        elif 'NR' in channel: text += ", inclusive region"
        elif 'MC' in channel: text += ", simulation"

    latex = TLatex()
    latex.SetNDC()
    latex.SetTextFont(72) #52
    latex.SetTextSize(0.035)
    if left: latex.DrawLatex(0.15, 0.75, text)
    else:
        latex.SetTextAlign(22)
        latex.DrawLatex(0.5, 0.85, text)
    pass

def getEntiresv0(cut, Lumi, samplelist, pd, ntupledir):

    #VAR=var
    hist0={}

    for TAG in samplelist:
        ENUMLIST=[]
        if 'data' in TAG:
            for datalet in (samples['%s' %TAG]['files']):
                if datalet in pd:
                    ENUMLIST.append(datalet)
        elif not 'data' in TAG:
            ENUMLIST=samples['%s' %TAG]['files']

        cutseq=""
        final=[]
        logic=False
        for cutstring in cut:
            #dummy=hist

            if len(cutseq)==0:
                cutseq+=cutstring
            else:
                cutseq+=" && "+cutstring
            #print "cutseq = ", cutseq

            car=[]
            NData=0.
            NMC=0.
            for num, bkgs in enumerate(ENUMLIST):
                #print num, bkgs
                f = TFile.Open(ntupledir+bkgs+".root","READ")
                tree = f.Get("Events")
                gROOT.cd()
                #Define histograms

                nevents = float(sample[bkgs]['nevents'])
                xs = float(sample[bkgs]['xsec'])*float(sample[bkgs]['kfactor'])
                LumiMC = nevents/xs
                Weight = float(Lumi) / float(LumiMC)

                if 'data' in TAG:
                    #subcut=cutseq.replace(cut[0],"(1==1)")
                    subcut=cutseq
                    print "Data = ", subcut
                    NData+=tree.GetEntries("%s" %subcut)
                elif not 'data' in TAG:
                    zpt="1"
                    print "MC = ", cutseq
                    NMC+=tree.GetEntries("%s*%s*(%s)" %(zpt,Weight,cutseq))

            if 'HLT' in cutstring:
                cutstring="HLT Trigger"
            car.append(cutstring)
            if 'data' in TAG:
                car.append(NData)
            elif not 'data' in TAG:
                car.append(NMC)
            final.append(car) #for cutstring in cut:
        hist0[TAG]=final #for TAG in samplelist:
    print (hist0)
    return hist0
pass

def getEntires(cutlist, Lumi, samplelist, pd, ntupledir, sign=[]):

    megaEvt=OrderedDict()
    events={}
    ColumnCut=[]
    #Blind data if with signal
    if sign: samplelist.remove('data_obs')
    ##Looping on tag
    for num1,k in enumerate(samplelist):
        print "process = ", k
        megaEvt[k]=OrderedDict() ; events[k]={};
        cuts=''

        for j, c in enumerate(cutlist):
            file = {} ; tree = {}
            events[k][j]=0.
            cuts+=cutlist[0] if j==0 else " && "+cutlist[j]
            print "cuts = ", cuts

            for num2,filename in enumerate(samples[k]['files']):
                file[filename] = TFile(ntupledir + filename + ".root", "READ") # Read TFile
                tree[filename] = file[filename].Get("Events") # Read TTree

                if k!='data_obs':
                    nevents = float(sample[filename]['nevents'])
                    xs = float(sample[filename]['xsec'])*float(sample[filename]['kfactor'])
                    LumiMC = nevents/xs
                    Weight = float(Lumi) / float(LumiMC)

                entries = tree[filename].GetEntries(cuts)
                events[k][j]+= float(entries) * float(Weight) if k!='data_obs' else float(entries)

            ##Customize cutstring
            if 'HLT' in cutlist[j]:
                cutstring="HLT"
            elif '==13*-13' in cutlist[j] and '==-13*13' in cutlist[j]:
                cutstring="OSmumu"
            elif '==11*-11' in cutlist[j] and '==-11*11' in cutlist[j]:
                cutstring="OSee"
            elif '==11*-13' in cutlist[j] and '==-11*13' in cutlist[j]:
                cutstring="OSemu"
            elif '==11*13' in cutlist[j] and '==-11*-13' in cutlist[j]:
                cutstring="SSemu"
            elif '==13*13' in cutlist[j] and '==-13*-13' in cutlist[j]:
                cutstring="SSmumu"
            elif '==11*11' in cutlist[j] and '==-11*-11' in cutlist[j]:
                cutstring="SSee"
            else:
                cutstring=cutlist[j]

            if num1==0: ColumnCut.append(cutstring)

            megaEvt[k][cutstring]=OrderedDict()
            megaEvt[k][cutstring] = events[k][j]

    pd1=pds.DataFrame.from_dict(megaEvt,orient='index')
    ##If sign, caculate TOTAL BKG VS Signal ONLY
    ##Significant
    if sign:
        #NOT SHOWING DATA, perhaps shows s/sqrt(b) too?
        signalCol=pd1.ix[sign] #column
        pd1=pd1.drop(sign)
        #pd1=pd1.drop(['data_obs'])
        MCsum= pds.DataFrame({'MC': pd1.sum()})
        pd2=pds.DataFrame(signalCol.to_dict(), columns=ColumnCut).T
        pd2=MCsum.join(pd2)
        pd2=pd2.round(1)

        if len(sign)==1:
            significance = pds.DataFrame({'significance': (pd2[sign[0]] / np.sqrt(MCsum['MC']))})
            significance.round(2)
            pd2=pd2.join(significance)
        else:
            for j in sign:
                pd2=pd2.join(pds.DataFrame({'Sig. '+j: (pd2[j] / np.sqrt(MCsum['MC']))}))
    ##ELSE, Show all the backgrounds vs DATA
    else:
        dataCol=pd1.ix[['data_obs']]
        pd1=pd1.drop(['data_obs'])
        MCsum= pds.DataFrame({'MC': pd1.sum()})
        pd2=pds.DataFrame(pd1.to_dict(), columns=ColumnCut).T
        dataCol=pds.DataFrame(dataCol.to_dict(), columns=ColumnCut).T
        pd2=pd2.join(MCsum); pd2=pd2.join(dataCol)
        norm = pds.DataFrame({'norm': (pd2['data_obs'] / pd2['MC'])*100})
        pd2=pd2.join(norm)
        pd2=pd2.round(2)
    #pd2=pd2.round(2)
    print pd2
    return pd2
pass

def printTable_html(hist,sign=[]):
    samplelist = [x for x in hist.keys() if not 'data' in x and not 'BkgSum' in x and not x in sign and not x=="files"]

    yesdata=False
    datalist=["0",1]
    if 'data_obs' in hist.keys():
        datalist=hist['data_obs']
        yesdata=True

    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<style>'
    print 'table, th, td {'
    print 'border: 1px solid black;}'
    print 'background-color: lemonchiffon;'
    print '</style>'
    print '<table>'
    print '<tr>'
    print '<th></th>'

    for i in samplelist:
        print "<th>%s</th>" %i,
    if not yesdata:
        print "<th>MC</th>"
    else:
        print "<th>MC</th><th>DATA</th><th>DATA/MC</th>"
    print '</tr>'

    for l in range(0,len(hist[samplelist[0]])):
        print '<tr>'
        print "<th>%s</th>" %((hist[samplelist[0]][l])[0]) # order cut
        count=0
        MC=0
        for i in range(0,len(samplelist)):
            print "<th>%-10.2f</th>" %((hist[samplelist[i]][l])[1])
            MC+=(hist[samplelist[i]][l])[1]
        print "<th>%-10.2f</th>" %MC
        if not yesdata:
            print "<th>%-10.2f</th>" %datalist[1]
            print "<th>%-10.2f</th>" %((datalist[1]/MC)*100)
        else:
            print "<th>%-10.2f</th>" %datalist[l][1]
            print "<th>%-10.2f</th>" %((datalist[l][1]/MC)*100)
        print '</tr>'
    print '</table>'
    print '</head>'
    print '</html>'
pass

def drawSignal(hist, sign, log=False):

    n = len(sign)
    leg = TLegend(0.7, 0.9-0.05*n, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    for i, s in enumerate(sign): leg.AddEntry(hist[s], samples[s]['label'], "fl")
    # --- Display ---
    c1 = TCanvas("c1", hist.values()[-1].GetXaxis().GetTitle(), 800, 600)
    if log:
        c1.cd(1).SetLogy()
    else:
        c1.cd(1)
    c1.GetPad(0).SetTopMargin(0.06)
    c1.GetPad(0).SetRightMargin(0.05)
    c1.GetPad(0).SetTicks(1, 1)
    if log:
        c1.GetPad(0).SetLogy()

    hist[sign[0]].SetMaximum(max(hist[sign[0]].GetMaximum(), hist[sign[-1]].GetMaximum())*5)
    if log:
        hist[sign[0]].SetMinimum(0.001)
    else:
        hist[sign[0]].SetMinimum(0.)
    # Draw
    print '-'*80
    for i, s in enumerate(sign):
        hist[s].SetLineColor(i+1)
        hist[s].Draw("SAME, HIST" if i>0 else "HIST") # signals
        print s ,": Int. = ", hist[s].Integral()
    print '-'*80

    if log:
        hist[sign[0]].GetYaxis().SetNoExponent(hist[sign[0]].GetMaximum() < 1.e4)
        hist[sign[0]].GetYaxis().SetMoreLogLabels(True)
    leg.Draw()
    #drawCMS(lumi, "Preliminary")

    c1.Update()
    # return list of objects created by the draw() function
    return [c1, leg]
pass
