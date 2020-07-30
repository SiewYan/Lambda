# cuts
supercut = 'mll>12  \
            && Lepton_pt[0]>25 && Lepton_pt[1]>20 \
            && bVeto \
            && PuppiMET_pt > 30 \
            '

cuts={}

cuts['OSmumu'] = 'isbVeto && nLepton==2 && (Lepton_pdgId[0]+Lepton_pdgId[1]==0) && nCleanJet>1 && CleanJet_pt[0]>30'

## SR 2jets
cuts['hww2l2v_13TeV_of2j_WH_SS_uu_2j'] = 'isbVeto \
                                       &&(Lepton_pdgId[0]*Lepton_pdgId[1] == 13*13) \
                                       && nLepton==2  \
                                       && nCleanJet>1 \
                                       && CleanJet_pt[0]>30 \
                                       && CleanJet_pt[1]>30 \
                                       && mjj < 100 \
                                       && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 \
                                       && abs(mll-91.2)>15 \
                                       && mlljj20_whss > 50. \
                                       '
cuts['hww2l2v_13TeV_of2j_WH_SS_eu_2j'] = 'isbVeto \
                                       && (Lepton_pdgId[0]*Lepton_pdgId[1] == 11*13) \
                                       && nLepton==2 \
                                       && nCleanJet>1 \
                                       && CleanJet_pt[0]>30 \
                                       && CleanJet_pt[1]>30 \
                                       && mjj < 100 \
                                       && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 \
                                       && mlljj20_whss > 50. \
                                       '
## SR 1jet

cuts['hww2l2v_13TeV_of2j_WH_SS_uu_1j'] = 'isbVeto \
                                       && (Lepton_pdgId[0]*Lepton_pdgId[1] == 13*13) \
                                       && nLepton==2 \
                                       && ( (nCleanJet==1 && CleanJet_pt[0]>30) || (nCleanJet>1 && CleanJet_pt[0]>30 && CleanJet_pt[1]<30) ) \
                                       && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 \
                                       && abs(mll-91.2)>15 \
                                       && mlljj20_whss > 50. \
                                       '
cuts['hww2l2v_13TeV_of2j_WH_SS_eu_1j'] = 'isbVeto \
                                       && (Lepton_pdgId[0]*Lepton_pdgId[1] == 11*13) \
                                       && nLepton==2 \
                                       && ( (nCleanJet==1 && CleanJet_pt[0]>30) || (nCleanJet>1 && CleanJet_pt[0]>30 && CleanJet_pt[1]<30) ) \
                                       && abs(Lepton_eta[0] - Lepton_eta[1])<2.0 \
                                       && mlljj20_whss > 50. \
                                       '

### WZ CR

'''
cuts['hww2l2v_13TeV_of2j_WH_SS_WZ_1j'] = '((Lepton_pdgId[0]*Lepton_pdgId[1] == 13*13) || (Lepton_pdgId[0]*Lepton_pdgId[1] == 11*13))\
                                       && (nLepton>=3 && Alt$(Lepton_pt[3],0)<10) \
                                       && Lepton_pt[2]>15 \
                                       && Alt$(CleanJet_pt[0],0)>30 \
                                       && Alt$(CleanJet_pt[1],0)<30 \
                                       && WH3l_mlll > 100 \
                                       && abs(WH3l_chlll) == 1 \
                                       '

cuts['hww2l2v_13TeV_of2j_WH_SS_WZ_2j'] = '((Lepton_pdgId[0]*Lepton_pdgId[1] == 13*13) || (Lepton_pdgId[0]*Lepton_pdgId[1] == 11*13)) \
                                       && (nLepton>=3 && Alt$(Lepton_pt[3],0)<10) \
                                       && Lepton_pt[2]>15 \
                                       && Alt$(CleanJet_pt[0],0)>30 \
                                       && Alt$(CleanJet_pt[1],0)>30 \
                                       && WH3l_mlll > 100 \
                                       && abs(WH3l_chlll) == 1 \
                                       '


cuts['zh3l_WZ_CR_2j'] = ' Alt$( CleanJet_pt[0], 0) >= 30 \
                       && Alt$( CleanJet_pt[1], 0) >= 30 \
                       && WH3l_ZVeto < 25 \
                       && bVeto \
                       && ZH3l_Z4lveto > 20 \
                       && ZH3l_dphilmetjj_test > 3.14159/2 \
                       '

cuts['zh3l_WZ_CR_1j'] = ' Alt$( CleanJet_pt[0], 0) >= 30 \
                       && Alt$( CleanJet_pt[1], 0) < 30 \
                       && WH3l_ZVeto < 25 \
                       && bVeto \
                       && ZH3l_Z4lveto > 20 \
                       && ZH3l_dphilmetj_test > 3.14159/2 \
                       '
'''
