__author__ = 'Florian Geigl'
from tools.basics import delete_file


def delete_network_files(filename):
    delete_file(filename)
    delete_file(filename.rsplit('.', 1)[0] + '.df')


def convert_to_set(iterable):
    if iterable is None:
        return {}
    else:
        return iterable if isinstance(iterable, set) else (set(iterable) if hasattr(iterable, '__iter__') else {iterable})


def convert_to_iterable(iterable):
    if hasattr(iterable, '__iter__'):
        return iterable
    else:
        return [iterable]

