cd $(dirname $0)/data/loop_free/
cp loop_free_data-test_shared_links_2.json $(dirname $0)/../data/loop_free_data.json
cd $(dirname $0)/../
python loop_free.py