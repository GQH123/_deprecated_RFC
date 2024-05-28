ps x | more | grep crawler_xxx | cut -d" " -f1 | xargs -I {} kill {}
ps x | more | grep crawler_xxx | cut -d" " -f2 | xargs -I {} kill {}