import FWCore.ParameterSet.Config as cms

process = cms.Process("TestElectrons")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.load("Configuration.StandardSequences.GeometryRecoDB_cff")

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
# NOTE: the pick the right global tag!
#    for Spring15 50ns MC: global tag is 'auto:run2_mc_50'
#    for Spring15 25ns MC: global tag is 'auto:run2_mc'
#    for Run 2 data: global tag is 'auto:run2_data'
#  as a rule, find the "auto" global tag in $CMSSW_RELEASE_BASE/src/Configuration/AlCa/python/autoCond.py
#  This auto global tag will look up the "proper" global tag
#  that is typically found in the DAS under the Configs for given dataset
#  (although it can be "overridden" by requirements of a given release)
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

#
# Define input data to read
#
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

inputFilesAOD = cms.untracked.vstring(
    # AOD test files from
    #  /DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16DR80-PUSpring16_80X_mcRun2_asymptotic_2016_v3_ext1-v1/AODSIM
       '/store/mc/RunIISpring16DR80/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/AODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3_ext1-v1/20000/004938DD-26FC-E511-A80F-02163E017620.root',
       '/store/mc/RunIISpring16DR80/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/AODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3_ext1-v1/20000/004F060D-ECFB-E511-90FC-0090FA9DFD8A.root',
       '/store/mc/RunIISpring16DR80/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/AODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3_ext1-v1/20000/0063C7EA-7FFB-E511-B632-0CC47A4D767A.root',
    )    

inputFilesMiniAOD = cms.untracked.vstring(
    # MiniAOD test files from 
    # /DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv1-PUSpring16_80X_mcRun2_asymptotic_2016_v3_ext1-v1/MINIAODSIM
       '/store/mc/RunIISpring16MiniAODv2/tZq_ll_4f_13TeV-amcatnlo-herwigpp/MINIAODSIM/premix_withHLT_80X_mcRun2_asymptotic_v14-v1/80000/062C87D2-456E-E611-ABF8-0CC47AA98F92.root'
    )

# Set up input/output depending on the format
# You can list here either AOD or miniAOD files, but not both types mixed
#
useAOD = False

if useAOD == True :
    inputFiles = inputFilesAOD
    outputFile = "electron_ntuple.root"
    print("AOD input files are used")
else :
    inputFiles = inputFilesMiniAOD
    outputFile = "electron_ntuple_mini.root"
    print("MiniAOD input files are used")
process.source = cms.Source ("PoolSource", fileNames = inputFiles )                             

#
# Set up electron ID (VID framework)
#

from PhysicsTools.SelectorUtils.tools.vid_id_tools import *
# turn on VID producer, indicate data format  to be
# DataFormat.AOD or DataFormat.MiniAOD, as appropriate 
if useAOD == True :
    dataFormat = DataFormat.AOD
else :
    dataFormat = DataFormat.MiniAOD

switchOnVIDElectronIdProducer(process, dataFormat)

# define which IDs we want to produce
my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff',
                 'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV60_cff']

#add them to the VID producer
for idmod in my_id_modules:
    setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

#
# Configure an example module for user analysis with electrons
#

process.ntupler = cms.EDAnalyzer(
    'ElectronNtuplerVIDDemo',
    # The module automatically detects AOD vs miniAOD, so we configure both
    #
    # Common to all formats objects
    #
    beamSpot = cms.InputTag('offlineBeamSpot'),
    genEventInfoProduct = cms.InputTag('generator'),
    #
    # Objects specific to AOD format
    #
    electrons    = cms.InputTag("gedGsfElectrons"),
    genParticles = cms.InputTag("genParticles"),
    vertices     = cms.InputTag("offlinePrimaryVertices"),
    conversions  = cms.InputTag('allConversions'),
    #
    # Objects specific to MiniAOD format
    #
    electronsMiniAOD    = cms.InputTag("slimmedElectrons"),
    genParticlesMiniAOD = cms.InputTag("prunedGenParticles"),
    verticesMiniAOD     = cms.InputTag("offlineSlimmedPrimaryVertices"),
    conversionsMiniAOD  = cms.InputTag('reducedEgamma:reducedConversions'),
    #
    # ID decisions (common to all formats)
    #
    # (all IDs listed below are available given the content of "my_id_modules" defined above.
    # only one is exercised for this example.
    #
    # eleIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-veto"),
    eleIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-loose"),
    # eleIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-medium"),
    # eleIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-tight"),
    # eleIdMap = cms.InputTag("egmGsfElectronIDs:heepElectronID-HEEPV60"),
    # An example of configuration for accessing the full cut flow info for
    # one case is shown below.
    # The map name for the full info is the same as the map name of the
    # corresponding simple pass/fail map above, they are distinguished by
    # the type of the content.
    eleIdFullInfoMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-medium"),
    # This is a fairly verbose mode if switched on, with full cut flow 
    # diagnostics for each candidate. Use it in a low event count test job.
    eleIdVerbose = cms.bool(False)
    )

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string( outputFile )
                                   )

# Make sure to add the ID sequence upstream from the user analysis module
process.p = cms.Path(process.egmGsfElectronIDSequence * process.ntupler)
