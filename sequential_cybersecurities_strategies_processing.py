import os

all_difficult_pdf_files = set()
with open("difficult_pdf_files.txt", "r", encoding="utf-8") as f:
    for line in f:
        clean_line = line.strip()
        if clean_line:
            all_difficult_pdf_files.add(clean_line)

folder_path = './marker_done_seq'  # Replace with your path
finished_folder_names = set([name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))])

folder_path = "./sequential_strategies_pdf"
sequential_cyber_strategies_pdf = set()
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
        if filename != '.DS_Store' and filename[:-4] not in finished_folder_names:
            print(filename)
            sequential_cyber_strategies_pdf.add(filename)

files_requiring_marker = sequential_cyber_strategies_pdf - all_difficult_pdf_files
print(f"Need to process {len(files_requiring_marker)} files.\n")

seq_cant_process = []

import subprocess
for filename in files_requiring_marker:
    print(f'\n\n\nProcessing {filename}!\n')
    try: subprocess.run(["marker_single", "./sequential_strategies_pdf/" + filename], timeout=300)
    except subprocess.TimeoutExpired:
        print(f'\nTimeout: Skipping {filename} due to long processing time.\n')
        seq_cant_process.append(filename)
        print(f"So far, all seq pdfs skipped due to long processing time: {seq_cant_process}")
        continue

# So far, all seq pdfs skipped due to long processing time: 
# ['20130610_Japan_National Cybersecurity Strategy_ENG.pdf', 
#  '20210801_Germany_National Cybersecurity Strategy_ENG.pdf',
#    '20210201_Nigeria_National Cybersecurity Strategy_ENG.pdf',
#      '20190101_Burkina Faso_National Cybersecurity Strategy_FRN.pdf',
#        '20210731_Bangladesh_National Cybersecurity Strategy_ENG.pdf']

# So far, all seq pdfs skipped due to long processing time: 
# ['20130101_Russia_National Cybersecurity Strategy_ENG.pdf', 
#  '20210101_Costa Rica_National Cybersecurity Strategy_ESP.pdf', 
#  '20221103_Eswatini_National Cybersecurity Strategy_ENG.pdf', 
#  '20220101_United Kingdom_National Cybersecurity Strategy_ENG.pdf', 
#  '20221101_Gambia_National Cybersecurity Strategy_ENG.pdf', 
#  '20201207_Greece_National Cybersecurity Strategy_GRE.pdf', 
#  '20190101_Burkina Faso_National Cybersecurity Strategy_FRN.pdf',
#    '20190501_Norway_National Cybersecurity Strategy_ENG.pdf', 
#    '20150101_France_National Cybersecurity Strategy_FRN.pdf', 
#    '20130101_Jordan_National Cybersecurity Strategy_ENG.pdf', 
#    '20210731_Bangladesh_National Cybersecurity Strategy_ENG.pdf', 
#    '20211001_Singapore_National Cybersecurity Strategy_ENG.pdf', 
#    '20200101_Malaysia_National Cybersecurity Strategy_ENG.pdf', 
#    '20151030_USA_National Cybersecurity Strategy_ENG.pdf', 
#    '20220701_Philippines_National Cybersecurity Strategy_ENG.pdf',
#      '20200101_Australia_National Cybersecurity Strategy_ENG.pdf', 
#      '20210201_Nigeria_National Cybersecurity Strategy_ENG.pdf', 
#      '20210801_Uganda_National Cybersecurity Strategy_ENG.pdf', 
#      '20241001_Ghana_National Cybersecurity Strategy_ENG.pdf']
