import sys
import pandas as pd
import numpy as np

marker = pd.read_table( sys.argv[1] )
all_sites = pd.read_table( sys.argv[2] )
msi_result = sys.argv[3]

selected_sites = pd.merge(marker, all_sites, on=['site'], how='inner')
MARKER_NUM = selected_sites.shape[0]
RATIO_CUTOFF = 0.2

sample_names = []
for  header_column in  list(selected_sites):
    if header_column.endswith('_avrgCov'):
        sample_name = header_column.rstrip('_avrgCov')
        sample_names.append(sample_name)
        current_sample_score = '{0}_score'.format(sample_name)
        selected_sites[current_sample_score] = np.where(selected_sites[header_column] > selected_sites['cutoff'], 0, 1 )

selected_sites_score = selected_sites.filter(like="_score")
msi_status = pd.DataFrame(selected_sites_score.sum(), columns=['score_total'] )
msi_status.index = np.array(sample_names)

msi_status['ratio'] = msi_status['score_total'] / MARKER_NUM
msi_status['msi_status'] = np.where( msi_status['ratio'] > RATIO_CUTOFF, 'MSI', 'MSS' )

msi_status.to_csv(msi_result, index=True, header=True, sep='\t')
