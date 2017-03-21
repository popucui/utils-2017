iconv -f UCS-2LE -t UTF8 -o tmp/test_B3.txt tmp/test_B.txt
awk 'NR==1{sub(/^\xef\xbb\xbf/,"")} {print}' tmp/test_B3.txt > tmp/test_B4.txt
python gs_tf_B.py makeResultSample --gtype-B  tmp/test_B4.txt 201703_3
iconv -f UTF8 -t UCS-2LE -o tmp/test_B4_sampleData_utf16.txt tmp/test_B4_sampleData.txt
#sed -i '1 s/^/\xef\xbb\xbf/' tmp/test_B4_sampleData_utf16.txt

#sed -i '1 s/^\xef\xbb\xbf//' *.txt