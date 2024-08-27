import argparse

from .initiator import main as initiator_main



def main():
    main_parser = argparse.ArgumentParser("RFC")
    # main_parser.add_argument('cmd', type=str, help='command for RFC', choices=['init'], required=True)
    main_subparsers = main_parser.add_subparsers(title="sub-commands", dest="cmd")
    
    initiator_parser = main_subparsers.add_parser('init', help='initiate an RFC project')
    initiator_parser.add_argument('project_path', type=str)
    
    args = main_parser.parse_args()
    
    if args.cmd == 'init':
        initiator_main(args.project_path)
    elif args.cmd is None:
        main_parser.print_help()
    else:
        raise ValueError(f'unsupported command: {repr(args.cmd)}')