from summarization.app.definitions import AUTO_PHRASE_PROGRAM
from subprocess import Popen
import re
import os
import time


def write_file(string, input_file):
    with open(input_file, 'w+') as x_file:
        x_file.write(string)


def read_file(string):
    with open(string, 'r') as file:
        data = file.read().replace('\n', '')
        return data


def parsing_segmenataion(string):
    p = re.compile(r'<phrase>([^<]+?)</phrase>')
    return p.findall(string)


def generating_list(string):
    timestamp = int(round(time.time()*1000))
    input_file = os.path.join(AUTO_PHRASE_PROGRAM, "%stempInput.txt" % (str(timestamp)))
    output_file = os.path.join(AUTO_PHRASE_PROGRAM, "%ssegmentation.txt" % (str(timestamp)))
    FNULL = open(os.devnull, 'w')

    # change path
    cur_path = os.getcwd()
    os.chdir(AUTO_PHRASE_PROGRAM)

    write_file(string, input_file)
    process = Popen("./phrasal_segmentation.sh %s %s" % (str(input_file), str(timestamp)), shell=True, stdout=FNULL)
    process.communicate()

    phrase_dict = []
    if process:
        phrase_dict = parsing_segmenataion(read_file(output_file))

    cleanProcess = Popen('bash ./rm_tmp_file.sh %s' % (str(timestamp)), shell=True)
    cleanProcess.communicate()

    os.chdir(cur_path)
    return phrase_dict
