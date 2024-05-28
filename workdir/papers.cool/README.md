# Crawler for papers.cool by RFC

## Running Commands

First, you should check if distributed clash is running. If not, do the following:

```bash
cd dist_clash/
python dist_clash.py
chmod +x launch.sh    # this is the auto generated script for launching distributed clash
./launch.sh
```

Then, you can simply run `run_nohup.sh` to launch the crawler,

```bash
chmod +x run_nohup.sh
./run_nohup.sh
```

After every run, you should run `remove_subs.py` to remove invalid papers and get a full statistics for all saved papers.

```bash
python remove_subs.py
```

## Notes

You can change the number of clash in the code, this should be consistent with the number of `nproc` and the proxy urls should be consistent with `proxy_pool` in crawler_kimi.py. In default `nproc` is set to 3 according to previous experiments.

You can update venue_tags by visiting `https://papers.cool` and manually check all supported venues.

by Renatus

2024.05.23
