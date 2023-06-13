import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DUC2002_DIR = os.path.join(ROOT_DIR, 'resources/DUC2002/docs/')
# bbc news path
BBC_NEWS_PATH = os.path.dirname("/Users/hao/Data/bbc/")

# cnn dailmail
CNN_DAILYMAIL_DIR = os.path.dirname("/Users/hao/summary_data/cdtest_copy/")

# SUMMBANK
SUMMBANK_DIR = os.path.dirname("/Users/hao/Data/summbank/")
SUMMBANK_EXTRACTIVE_SUMMARY_DIR = os.path.join(SUMMBANK_DIR, "manual/manual_extracts/single_document")
SUMMBANK_HUMAN_SUMMARY_DIR = os.path.join(SUMMBANK_DIR, "manual/manual_summaries/regular")
SUMMBANK_DOCS_DIR = os.path.join(SUMMBANK_DIR, "clusters/english")

# W2V_settings
W2V_MODE = "API"    # API or PATH
W2V_CN_MODEL_PATH = os.path.join(ROOT_DIR, 'resources/w2v_model/ft-cn.vec')
# ft-cn threshold = 0.45
# train-cn threshold = 0.96
W2V_CN_MODEL_THRESHOLD = 0.45

# ft-en threshold = 0.6
# ft-en-subword threshold = 0.6
W2V_EN_MODEL_PATH = os.path.join(ROOT_DIR, 'resources/w2v_model/ft-en-subword.vec')
W2V_EN_MODEL_THRESHOLD = 0.6


W2V_API_LANG = "english"
W2V_API_WEB_API_URL = "localhost"
W2V_API_WEB_API_PORT = 8081
W2V_API_WEB_API_PATH = "/w2v"

# AutoPhrase API Setup
# AutoPhrase program folder
AUTO_PHRASE_PROGRAM = os.path.dirname("/Users/hao/Code/AutoPhrase/")
# Script file
AP_SCRIPT_FILE = os.path.join(AUTO_PHRASE_PROGRAM, "phrasal_segmentation.sh")
