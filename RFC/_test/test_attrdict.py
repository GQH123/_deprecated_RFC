from RFC.config.attrdict import AttrDict


def test_attrdict():
    import os
    import json
    
    x = AttrDict({'a': 1, 'f': [[{'r': 9}, {'e': 6}], {'r': 9}, {'e': [{'r': 9}, {'e': 6}]}], 'b': {'c': 2, 'd': {'e': 3}}})
    print(x.a, x.f, x.f[1].r, x.f[0][1].e, x.f[2].e[0].r, sep='\n')
    y = AttrDict(json.load(open(os.path.join('test_attrdict', 'example_dict.json'))))
    print(y['3343'], y['3343'].title, y['3343'].tags, y['3343'].tags.用途, sep='\n')
    

if __name__ == '__main__':
    test_attrdict()