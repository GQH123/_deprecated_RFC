ps x | more | grep crawler.py | cut -d ' ' -f1 | xargs -I {} kill {}
rm logs/* saves_1/ -r