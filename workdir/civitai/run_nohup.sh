# nohup python ./crawler.py 2>&1 > RFC_stderr.log &
# nohup python ./crawler_civitai_page.py 2>&1 > /dev/null &
nohup python ./crawler_civitai_model.py 2>&1 > /dev/null &