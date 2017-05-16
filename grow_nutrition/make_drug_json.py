#coding=utf-8

import fire,json,sys
import time, os
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)



def make_drug_json(drug_dat, drug_gtype, drug_result): 
    two_result_section = [
    'β2肾上腺素受体激动剂',
    '利福平',
    '卡马西平',
    '双氯芬酸',
    '吗啡',
    '地录雷他定',
    '孟鲁斯特',
    '布洛芬',
    '氟替卡松',
    '氨基糖苷类药物',
    '苯妥因',
    '阿莫西林']
    g6pd_pdpids = [
    'pdp0221','pdp0222','pdp0223','pdp0224','pdp0225','pdp0226','pdp0227',
    'pdp0228','pdp0229','pdp0230','pdp0231','pdp0232','pdp0233','pdp0234','pdp0235',
    'pdp0236','pdp0237','pdp0238','pdp0239','pdp0240','pdp0241','pdp0242','pdp0243']
    g6pd_result = []
    results_list = []
    
    with open(drug_dat) as f:
        drug_dict = json.load(f)
    with open(drug_gtype) as f:
        for line in f:
            if 'G6PD' in line:
                g_mutation = line.rstrip().split()[1]
                g6pd_result.append(g_mutation)
                continue
            tmp = line.rstrip().split()
            section_name, rsid, gtype, _, gscore = tmp[1:-1]
            drug_dict[section_name][rsid]['gscore'] = gscore
            drug_dict[section_name][rsid]['gtype'] = gtype
            drug_dict[section_name]['total_score'] += int(gscore)
    for section_name in drug_dict:
        if section_name in two_result_section:
            if drug_dict[section_name]['total_score'] == 0:
                drug_dict[section_name]['result'] = drug_dict[section_name]['score2result']['0']
            else:
                drug_dict[section_name]['result'] = drug_dict[section_name]['score2result']['1']
        else:
            max_score = (len(drug_dict[section_name].keys() ) - 2) * 2
            if drug_dict[section_name]['total_score'] >= max_score * 0.75:
                drug_dict[section_name]['result'] = drug_dict[section_name]['score2result']['2']
            elif drug_dict[section_name]['total_score'] < max_score * 0.25:
                drug_dict[section_name]['result'] = drug_dict[section_name]['score2result']['0']
            else:
                drug_dict[section_name]['result'] = drug_dict[section_name]['score2result']['1']
    g6pd_result = ','.join(g6pd_result) if g6pd_result else '未发现突变'
    time_stamp = time.ctime().replace(' ', '_')
    sample_barcode = os.path.basename(drug_gtype).split('.')[0]
    results_list.append('snp位点\t基因\t批次\t所属样本\t基因型\t检测结果\n')
    for pdpid in g6pd_pdpids:
        results_list.append('{snpid}\t\t{pici}\t{sample}\t\t{result}\n'.format(
            snpid = pdpid, pici = time_stamp, 
            sample = sample_barcode, result = g6pd_result) )
    for section_name in drug_dict:
        logging.debug(section_name)
        for rsid in drug_dict[section_name]:
            if isinstance(drug_dict[section_name][rsid], dict) and ('gscore' in drug_dict[section_name][rsid]):
                results_list.append('{snpid}\t\t{pici}\t{sample}\t{gtype}\t{dresult}\n'.format(
                    snpid = drug_dict[section_name][rsid]['pdpid'], pici = time_stamp, 
                    gtype = drug_dict[section_name][rsid]['gtype'], dresult = drug_dict[section_name]['result'],
                    sample = sample_barcode) )
    with open(drug_result, 'w') as f:
        f.writelines(results_list)

                

if __name__ == '__main__':
    fire.Fire()
   