import bs4
import requests
from bs4 import BeautifulSoup
from typing import Sequence


"""
parse_config = {
    'next_page': {
        ('attr', 'div', 'class', 'mw-body-content', None): {
            ('attr', 'div', 'class', 'mw-allpages-nav', 0): {
                ('result', 'href', -1): {}
            }
        }
    },
    'article_links': {
        ('attr', 'div', 'class', 'mw-allpages-body', None): {
            ('type', 'li', None): {
                ('result', 'href', None): {}
            }
        }
    }
}
"""


def get_request_soup(r: requests.Response) -> BeautifulSoup:
    return BeautifulSoup(r.text, features="lxml")  # if error occurs, run `pip install lxml`


def get_html_soup(s: str) -> BeautifulSoup:
    return BeautifulSoup(s, features="lxml")  # if error occurs, run `pip install lxml`


def find_element_by_attr(soup: BeautifulSoup, element_tp: str, attr_key: str, attr_value: str) -> bs4.element.ResultSet:
    # https://stackoverflow.com/questions/5041008/how-to-find-elements-by-class
    return soup.find_all(element_tp, {attr_key: attr_value})


def find_element_by_type(soup: BeautifulSoup, element_tp: str) -> bs4.element.ResultSet:
    return soup.find_all(element_tp)


def extract_all_text(soup):
    return soup.find_all(text=True)


def extract_all_href(soup):
    return soup.find_all('a', href=True)


def get_shortened_str(s: str, length: int = 100) -> str:
    s = ''.join(s.split())
    if s == '':
        s = 'None'
    return s[:length] + ('...' if len(s) > length else '')


def parse(soup: BeautifulSoup, parses: dict, return_str=False, debug=False) -> Sequence[str]:
    def _parse_element_by_type(soup: BeautifulSoup, element_tp: str) -> BeautifulSoup:
        try:
            return find_element_by_type(soup, element_tp)
        except IndexError:
            return None
            
    def _parse_element_by_content(soup: BeautifulSoup) -> BeautifulSoup:
        return soup.contents
    
    def _parse_element_by_href(soup: BeautifulSoup) -> BeautifulSoup:
        return extract_all_href(soup)
    
    def _parse_element_by_text(soup: BeautifulSoup) -> BeautifulSoup:
        return ''.join([''.join(_soup.split()) for _soup in extract_all_text(soup)])

    def _parse_element_by_attr(soup: BeautifulSoup, element_tp: str, attr_key: str, attr_value: str) -> BeautifulSoup:
        return find_element_by_attr(soup, element_tp, attr_key, attr_value)
    
    def _parse(soup: BeautifulSoup, parses: dict, element_id: Sequence[int] = [], element_ns: Sequence[int] = []):
        if debug:
            for i in range(len(element_id)):
                if i == len(element_id) - 1:
                    if element_id[i] == element_ns[i] - 1:
                        print('└── ', end='')
                    else:
                        print('├── ', end='')
                else:
                    if element_id[i] == element_ns[i] - 1:
                        print('    ', end='')
                    else:
                        print('│   ', end='')
            print(get_shortened_str(str(soup)))

        if parses == {}:
            return [str(soup) if return_str else soup]

        if soup is None:
            print('warning: soup is guided to None, please debug your parse')
            return []

        __soup = soup
        full_soup = []
        for parse in parses:
            soup = __soup
            parse_type = parse[0]
            parse_index = parse[-1]
            if isinstance(parse_index, int) or isinstance(parse_index, slice):
                index = parse_index
            elif isinstance(parse_index, tuple):
                index = slice(*parse_index)
            elif parse_index is None:
                index = slice(None)
            else:
                raise ValueError(f"unidentified index type of {repr(parse_index)}")
            if parse_type == 'type':
                # ('type', <type>, <index>)
                soup = _parse_element_by_type(soup, parse[1])
            elif parse_type == 'result':
                attr_type = parse[1]
                if attr_type == 'contents':
                    # ('result', 'contents', <index>)
                    soup = _parse_element_by_content(soup)
                elif attr_type == 'text':
                    # ('result', 'text', <index>)
                    soup = _parse_element_by_text(soup)
                elif attr_type == 'href':
                    # ('result', 'href', <index>)
                    soup = _parse_element_by_href(soup)
                else:
                    print(f'warning: unsupported attr_type {repr(attr_type)}, all supported attr_type are {repr(["contents", "text", "href"])}')
                    soup = None
            elif parse_type == 'attr':
                # ('attr', <element_type>, <attr_key>, <attr_value>, <index>)
                soup = _parse_element_by_attr(soup, parse[1], parse[2], parse[3])
            else:
                raise NotImplementedError
            if soup is not None:
                if not isinstance(soup, list):
                    soup = [soup]
                try:
                    soup = soup[index]
                except (IndexError, KeyError):
                    soup = [None]
                if not isinstance(soup, list):
                    soup = [soup]
                full_soup += list(zip([parses[parse]] * len(soup), soup))
        nsoup = len(full_soup)
        result = []
        for i, _soup in enumerate(full_soup):
            result += _parse(_soup[1], _soup[0], element_id=element_id+[i], element_ns=element_ns+[nsoup])
        return result
    return _parse(soup, parses)