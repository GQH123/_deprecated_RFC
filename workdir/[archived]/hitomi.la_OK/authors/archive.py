import os


def system(cmd):
    print(cmd)
    os.system(cmd)

authors = os.listdir('saves/')
for author in authors:
    if os.path.exists(f'saves/{author}.zip'):
        continue
    system(f'zip -r "saves/{author}.zip" "saves/{author}"')