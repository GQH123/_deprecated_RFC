ps x | more | grep crawler_pack | cut -d" " -f1 | xargs -I {} kill {}
ps x | more | grep crawler_pack | cut -d" " -f2 | xargs -I {} kill {}