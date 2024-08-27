from RFC.config.utils import get_username, get_hostname


def test_utils():
    print(get_hostname())
    print(get_username())


if __name__ == '__main__':
    test_utils()