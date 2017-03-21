## for taocan A, should save result  as UCS-2 LE BOM before upload to CRM system
python gs_transform4report.py 2016.09.22CQ_1.txt \
sampleData_9.26.txt \
resultData_9.26.txt \
10.09_1

##for taocan B, should save result  as UCS-2 LE BOM before upload to CRM system
python gs_tf_B.py makeResultSample --gtype-B  tmp/test_B.txt --timeStamp  201703_3
